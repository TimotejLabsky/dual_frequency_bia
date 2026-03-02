"""Config flow for Dual Frequency BIA integration.

Two-step flow:
1. User profile: name, birthday, gender, height, profile_id
2. Sensor selection: weight, impedance_high, impedance_low, heart_rate, profile_id_sensor
"""

from __future__ import annotations

from typing import Any

import voluptuous as vol

from homeassistant.config_entries import ConfigFlow, ConfigFlowResult
from homeassistant.const import CONF_NAME
from homeassistant.helpers.selector import (
    DateSelector,
    EntitySelector,
    EntitySelectorConfig,
    NumberSelector,
    NumberSelectorConfig,
    NumberSelectorMode,
    SelectSelector,
    SelectSelectorConfig,
    SelectSelectorMode,
    TextSelector,
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
    DOMAIN,
    HEIGHT_MAX,
    HEIGHT_MIN,
    PROFILE_ID_MAX,
    PROFILE_ID_MIN,
)
from .models import Gender

STEP_USER_SCHEMA = vol.Schema(
    {
        vol.Required(CONF_NAME): TextSelector(),
        vol.Required(CONF_BIRTHDAY): DateSelector(),
        vol.Required(CONF_GENDER): SelectSelector(
            SelectSelectorConfig(
                options=[
                    {"value": Gender.MALE, "label": "Male"},
                    {"value": Gender.FEMALE, "label": "Female"},
                ],
                mode=SelectSelectorMode.DROPDOWN,
            )
        ),
        vol.Required(CONF_HEIGHT): NumberSelector(
            NumberSelectorConfig(
                min=HEIGHT_MIN,
                max=HEIGHT_MAX,
                step=1,
                unit_of_measurement="cm",
                mode=NumberSelectorMode.BOX,
            )
        ),
        vol.Optional(CONF_PROFILE_ID): NumberSelector(
            NumberSelectorConfig(
                min=PROFILE_ID_MIN,
                max=PROFILE_ID_MAX,
                step=1,
                mode=NumberSelectorMode.BOX,
            )
        ),
    }
)

SENSOR_DOMAIN_FILTER = EntitySelectorConfig(domain="sensor")

STEP_SENSORS_SCHEMA = vol.Schema(
    {
        vol.Required(CONF_SENSOR_WEIGHT): EntitySelector(SENSOR_DOMAIN_FILTER),
        vol.Required(CONF_SENSOR_IMPEDANCE_HIGH): EntitySelector(SENSOR_DOMAIN_FILTER),
        vol.Required(CONF_SENSOR_IMPEDANCE_LOW): EntitySelector(SENSOR_DOMAIN_FILTER),
        vol.Optional(CONF_SENSOR_HEART_RATE): EntitySelector(SENSOR_DOMAIN_FILTER),
        vol.Optional(CONF_SENSOR_PROFILE_ID): EntitySelector(SENSOR_DOMAIN_FILTER),
    }
)


class DualFrequencyBIAConfigFlow(ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Dual Frequency BIA."""

    VERSION = 1

    def __init__(self) -> None:
        """Initialize flow."""
        self._user_data: dict[str, Any] = {}

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        """Step 1: User profile (name, birthday, gender, height, profile_id)."""
        if user_input is not None:
            self._user_data = user_input
            return await self.async_step_sensors()

        return self.async_show_form(
            step_id="user",
            data_schema=STEP_USER_SCHEMA,
        )

    async def async_step_sensors(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        """Step 2: Source sensor entity selection."""
        if user_input is not None:
            data = {**self._user_data, **user_input}

            # Convert height to int
            data[CONF_HEIGHT] = int(data[CONF_HEIGHT])

            # Convert profile_id to int if present
            if CONF_PROFILE_ID in data and data[CONF_PROFILE_ID] is not None:
                data[CONF_PROFILE_ID] = int(data[CONF_PROFILE_ID])

            return self.async_create_entry(
                title=data[CONF_NAME],
                data=data,
            )

        return self.async_show_form(
            step_id="sensors",
            data_schema=STEP_SENSORS_SCHEMA,
        )
