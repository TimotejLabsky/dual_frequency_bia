"""Base entity for Dual Frequency BIA sensors."""

from __future__ import annotations

from homeassistant.helpers.entity import DeviceInfo

from .const import DOMAIN
from .metrics import BodyCompositionMetricsHandler
from .models import Metric


class DualFrequencyBIAEntity:
    """Base class for dual frequency BIA entities."""

    _attr_has_entity_name = True

    def __init__(
        self,
        handler: BodyCompositionMetricsHandler,
        entry_id: str,
        metric: Metric,
    ) -> None:
        """Initialize the entity."""
        self._handler = handler
        self._metric = metric
        self._attr_unique_id = f"{entry_id}_{metric.value}"

    @property
    def device_info(self) -> DeviceInfo:
        """Return device info to group all sensors under one device."""
        return DeviceInfo(
            identifiers={(DOMAIN, self._attr_unique_id.rsplit("_", 1)[0])},
            name=f"{self._handler.profile.name} Body Composition",
            manufacturer="Dual Frequency BIA",
            model="Dual-Frequency BIA",
        )
