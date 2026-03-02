"""Dual Frequency BIA integration.

Listens for state changes on configured source sensors (weight, impedance, heart_rate),
gates by profile ID when configured, debounces rapid BLE updates, and recalculates
body composition metrics using dual-frequency BIA.
"""

from __future__ import annotations

import logging
from datetime import date, datetime

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_NAME, EVENT_HOMEASSISTANT_STARTED, Platform
from homeassistant.core import Event, HomeAssistant, callback
from homeassistant.helpers.event import (
    async_call_later,
    async_track_state_change_event,
)

from .const import (
    CONF_BIRTHDAY,
    CONF_GENDER,
    CONF_HEIGHT,
    CONF_PROFILE_ID,
    CONF_SENSOR_HEART_RATE,
    CONF_SENSOR_IMPEDANCE_HIGH,
    CONF_SENSOR_IMPEDANCE_LOW,
    CONF_SENSOR_PROFILE_ID,
    CONF_SENSOR_WEIGHT,
    DEBOUNCE_DELAY,
    IMPEDANCE_MAX,
    IMPEDANCE_MIN,
    WEIGHT_MAX,
    WEIGHT_MIN,
)
from .metrics import BodyCompositionMetricsHandler
from .models import Gender, UserProfile

_LOGGER = logging.getLogger(__name__)

PLATFORMS = [Platform.SENSOR]

type DualFrequencyBIAConfigEntry = ConfigEntry[BodyCompositionMetricsHandler]


async def async_setup_entry(
    hass: HomeAssistant, entry: DualFrequencyBIAConfigEntry
) -> bool:
    """Set up Dual Frequency BIA from a config entry."""
    # Build user profile from config
    birthday = date.fromisoformat(entry.data[CONF_BIRTHDAY])
    profile = UserProfile(
        name=entry.data[CONF_NAME],
        birthday=birthday,
        gender=Gender(entry.data[CONF_GENDER]),
        height=entry.data[CONF_HEIGHT],
        profile_id=entry.data.get(CONF_PROFILE_ID),
    )

    handler = BodyCompositionMetricsHandler(profile)
    entry.runtime_data = handler

    # Source sensor entity IDs
    weight_entity = entry.data[CONF_SENSOR_WEIGHT]
    impedance_high_entity = entry.data[CONF_SENSOR_IMPEDANCE_HIGH]
    impedance_low_entity = entry.data[CONF_SENSOR_IMPEDANCE_LOW]
    heart_rate_entity = entry.data.get(CONF_SENSOR_HEART_RATE)
    profile_id_entity = entry.data.get(CONF_SENSOR_PROFILE_ID)

    # Track which entities to listen to
    tracked_entities = [weight_entity, impedance_high_entity, impedance_low_entity]
    if heart_rate_entity:
        tracked_entities.append(heart_rate_entity)
    if profile_id_entity:
        tracked_entities.append(profile_id_entity)

    # Debounce handle
    debounce_cancel: list[callback | None] = [None]

    # Mapping from entity_id to input key
    entity_to_input: dict[str, str] = {
        weight_entity: "weight",
        impedance_high_entity: "impedance_high",
        impedance_low_entity: "impedance_low",
    }
    if heart_rate_entity:
        entity_to_input[heart_rate_entity] = "heart_rate"

    def _parse_float(state_value: str | None) -> float | None:
        """Parse a state value to float, returning None on failure."""
        if state_value is None or state_value in ("unknown", "unavailable", ""):
            return None
        try:
            return float(state_value)
        except (ValueError, TypeError):
            return None

    def _validate_input(key: str, value: float) -> bool:
        """Validate an input value is within expected range."""
        if key == "weight":
            return WEIGHT_MIN <= value <= WEIGHT_MAX
        if key in ("impedance_high", "impedance_low"):
            return IMPEDANCE_MIN <= value <= IMPEDANCE_MAX
        return True  # heart_rate: accept any positive value

    def _check_profile_id() -> bool:
        """Check if the current profile_id matches this entry's profile."""
        if profile.profile_id is None or profile_id_entity is None:
            return True  # No profile gating

        state = hass.states.get(profile_id_entity)
        if state is None:
            return False

        try:
            current_id = int(float(state.state))
        except (ValueError, TypeError):
            return False

        return current_id == profile.profile_id

    @callback
    def _debounced_recalculate(_now: datetime | None = None) -> None:
        """Perform the actual recalculation after debounce delay."""
        debounce_cancel[0] = None

        if not _check_profile_id():
            _LOGGER.debug(
                "Profile ID mismatch for %s, skipping recalculation",
                profile.name,
            )
            return

        handler.recalculate()

    @callback
    def _schedule_recalculate() -> None:
        """Schedule a debounced recalculation."""
        # Cancel any pending recalculation
        if debounce_cancel[0] is not None:
            debounce_cancel[0]()  # type: ignore[misc]

        debounce_cancel[0] = async_call_later(
            hass, DEBOUNCE_DELAY, _debounced_recalculate
        )

    @callback
    def _on_state_change(event: Event) -> None:
        """Handle state changes from source sensors."""
        entity_id = event.data.get("entity_id")
        if entity_id is None:
            return

        new_state = event.data.get("new_state")
        if new_state is None:
            return

        # Profile ID sensor change — just reschedule
        if entity_id == profile_id_entity:
            _schedule_recalculate()
            return

        # Map entity to input key
        input_key = entity_to_input.get(entity_id)
        if input_key is None:
            return

        value = _parse_float(new_state.state)
        if value is None:
            return

        if not _validate_input(input_key, value):
            _LOGGER.warning(
                "Value %.2f for %s (%s) out of range, ignoring",
                value,
                input_key,
                entity_id,
            )
            return

        handler.update_input(input_key, value)
        _schedule_recalculate()

    @callback
    def _read_initial_states(_event: Event | None = None) -> None:
        """Read current states of all source sensors on startup."""
        for entity_id, input_key in entity_to_input.items():
            state = hass.states.get(entity_id)
            if state is not None:
                value = _parse_float(state.state)
                if value is not None and _validate_input(input_key, value):
                    handler.update_input(input_key, value)

        # Do an initial calculation if we have all inputs
        if handler.has_required_inputs() and _check_profile_id():
            handler.recalculate()

    # Set up state change listeners
    entry.async_on_unload(
        async_track_state_change_event(hass, tracked_entities, _on_state_change)
    )

    # Read initial states after HA is fully started
    if hass.is_running:
        _read_initial_states()
    else:
        hass.bus.async_listen_once(EVENT_HOMEASSISTANT_STARTED, _read_initial_states)

    # Forward to sensor platform
    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)

    return True


async def async_unload_entry(
    hass: HomeAssistant, entry: DualFrequencyBIAConfigEntry
) -> bool:
    """Unload a config entry."""
    return await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
