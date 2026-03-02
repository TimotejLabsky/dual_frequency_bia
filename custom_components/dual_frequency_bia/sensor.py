"""Sensor platform for Dual Frequency BIA integration."""

from __future__ import annotations

from dataclasses import dataclass

from homeassistant.components.sensor import (
    SensorDeviceClass,
    SensorEntity,
    SensorEntityDescription,
    SensorStateClass,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import (
    PERCENTAGE,
    UnitOfMass,
)
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .entity import DualFrequencyBIAEntity
from .metrics import BodyCompositionMetricsHandler
from .models import Metric


@dataclass(frozen=True, kw_only=True)
class DualFrequencyBIASensorDescription(SensorEntityDescription):
    """Sensor entity description for body composition metrics."""

    metric: Metric


SENSOR_DESCRIPTIONS: tuple[DualFrequencyBIASensorDescription, ...] = (
    DualFrequencyBIASensorDescription(
        key="weight",
        metric=Metric.WEIGHT,
        native_unit_of_measurement=UnitOfMass.KILOGRAMS,
        device_class=SensorDeviceClass.WEIGHT,
        state_class=SensorStateClass.MEASUREMENT,
        suggested_display_precision=1,
    ),
    DualFrequencyBIASensorDescription(
        key="bmi",
        metric=Metric.BMI,
        translation_key="bmi",
        native_unit_of_measurement="kg/m²",
        state_class=SensorStateClass.MEASUREMENT,
        suggested_display_precision=1,
    ),
    DualFrequencyBIASensorDescription(
        key="basal_metabolism",
        metric=Metric.BASAL_METABOLISM,
        translation_key="basal_metabolism",
        native_unit_of_measurement="kcal",
        state_class=SensorStateClass.MEASUREMENT,
        suggested_display_precision=0,
    ),
    DualFrequencyBIASensorDescription(
        key="visceral_fat",
        metric=Metric.VISCERAL_FAT,
        translation_key="visceral_fat",
        state_class=SensorStateClass.MEASUREMENT,
        suggested_display_precision=1,
    ),
    DualFrequencyBIASensorDescription(
        key="ideal_weight",
        metric=Metric.IDEAL_WEIGHT,
        translation_key="ideal_weight",
        native_unit_of_measurement=UnitOfMass.KILOGRAMS,
        device_class=SensorDeviceClass.WEIGHT,
        state_class=SensorStateClass.MEASUREMENT,
        suggested_display_precision=1,
    ),
    DualFrequencyBIASensorDescription(
        key="total_body_water",
        metric=Metric.TOTAL_BODY_WATER,
        translation_key="total_body_water",
        native_unit_of_measurement="L",
        device_class=SensorDeviceClass.VOLUME_STORAGE,
        state_class=SensorStateClass.MEASUREMENT,
        suggested_display_precision=2,
    ),
    DualFrequencyBIASensorDescription(
        key="extracellular_water",
        metric=Metric.EXTRACELLULAR_WATER,
        translation_key="extracellular_water",
        native_unit_of_measurement="L",
        device_class=SensorDeviceClass.VOLUME_STORAGE,
        state_class=SensorStateClass.MEASUREMENT,
        suggested_display_precision=2,
    ),
    DualFrequencyBIASensorDescription(
        key="intracellular_water",
        metric=Metric.INTRACELLULAR_WATER,
        translation_key="intracellular_water",
        native_unit_of_measurement="L",
        device_class=SensorDeviceClass.VOLUME_STORAGE,
        state_class=SensorStateClass.MEASUREMENT,
        suggested_display_precision=2,
    ),
    DualFrequencyBIASensorDescription(
        key="fat_free_mass",
        metric=Metric.FAT_FREE_MASS,
        translation_key="fat_free_mass",
        native_unit_of_measurement=UnitOfMass.KILOGRAMS,
        device_class=SensorDeviceClass.WEIGHT,
        state_class=SensorStateClass.MEASUREMENT,
        suggested_display_precision=2,
    ),
    DualFrequencyBIASensorDescription(
        key="body_fat",
        metric=Metric.BODY_FAT,
        translation_key="body_fat",
        native_unit_of_measurement=PERCENTAGE,
        state_class=SensorStateClass.MEASUREMENT,
        suggested_display_precision=1,
    ),
    DualFrequencyBIASensorDescription(
        key="lean_body_mass",
        metric=Metric.LEAN_BODY_MASS,
        translation_key="lean_body_mass",
        native_unit_of_measurement=UnitOfMass.KILOGRAMS,
        device_class=SensorDeviceClass.WEIGHT,
        state_class=SensorStateClass.MEASUREMENT,
        suggested_display_precision=2,
    ),
    DualFrequencyBIASensorDescription(
        key="water_percentage",
        metric=Metric.WATER_PERCENTAGE,
        translation_key="water_percentage",
        native_unit_of_measurement=PERCENTAGE,
        state_class=SensorStateClass.MEASUREMENT,
        suggested_display_precision=1,
    ),
    DualFrequencyBIASensorDescription(
        key="bone_mass",
        metric=Metric.BONE_MASS,
        translation_key="bone_mass",
        native_unit_of_measurement=UnitOfMass.KILOGRAMS,
        device_class=SensorDeviceClass.WEIGHT,
        state_class=SensorStateClass.MEASUREMENT,
        suggested_display_precision=2,
    ),
    DualFrequencyBIASensorDescription(
        key="muscle_mass",
        metric=Metric.MUSCLE_MASS,
        translation_key="muscle_mass",
        native_unit_of_measurement=UnitOfMass.KILOGRAMS,
        device_class=SensorDeviceClass.WEIGHT,
        state_class=SensorStateClass.MEASUREMENT,
        suggested_display_precision=2,
    ),
    DualFrequencyBIASensorDescription(
        key="metabolic_age",
        metric=Metric.METABOLIC_AGE,
        translation_key="metabolic_age",
        native_unit_of_measurement="years",
        state_class=SensorStateClass.MEASUREMENT,
        suggested_display_precision=0,
    ),
    DualFrequencyBIASensorDescription(
        key="protein",
        metric=Metric.PROTEIN,
        translation_key="protein",
        native_unit_of_measurement=PERCENTAGE,
        state_class=SensorStateClass.MEASUREMENT,
        suggested_display_precision=1,
    ),
    DualFrequencyBIASensorDescription(
        key="body_score",
        metric=Metric.BODY_SCORE,
        translation_key="body_score",
        state_class=SensorStateClass.MEASUREMENT,
        suggested_display_precision=0,
    ),
    DualFrequencyBIASensorDescription(
        key="ecw_tbw_ratio",
        metric=Metric.ECW_TBW_RATIO,
        translation_key="ecw_tbw_ratio",
        state_class=SensorStateClass.MEASUREMENT,
        suggested_display_precision=3,
    ),
    DualFrequencyBIASensorDescription(
        key="ecw_tbw_status",
        metric=Metric.ECW_TBW_STATUS,
        translation_key="ecw_tbw_status",
        device_class=SensorDeviceClass.ENUM,
    ),
    DualFrequencyBIASensorDescription(
        key="heart_rate",
        metric=Metric.HEART_RATE,
        translation_key="heart_rate",
        native_unit_of_measurement="bpm",
        state_class=SensorStateClass.MEASUREMENT,
        suggested_display_precision=0,
    ),
)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up Dual Frequency BIA sensors from a config entry."""
    handler: BodyCompositionMetricsHandler = entry.runtime_data

    entities = [
        DualFrequencyBIASensor(
            handler=handler,
            entry_id=entry.entry_id,
            description=description,
        )
        for description in SENSOR_DESCRIPTIONS
    ]

    async_add_entities(entities)


class DualFrequencyBIASensor(DualFrequencyBIAEntity, SensorEntity):
    """Sensor entity for a body composition metric."""

    entity_description: DualFrequencyBIASensorDescription

    def __init__(
        self,
        handler: BodyCompositionMetricsHandler,
        entry_id: str,
        description: DualFrequencyBIASensorDescription,
    ) -> None:
        """Initialize the sensor."""
        super().__init__(handler=handler, entry_id=entry_id, metric=description.metric)
        self.entity_description = description

    async def async_added_to_hass(self) -> None:
        """Register with the metrics handler when added to hass."""
        self._handler.subscribe(
            self.entity_description.metric,
            self._on_metric_updated,
        )

        # Set initial value if available
        value = self._handler.get_value(self.entity_description.metric)
        if value is not None:
            self._attr_native_value = value

    @callback
    def _on_metric_updated(self) -> None:
        """Handle metric value update."""
        value = self._handler.get_value(self.entity_description.metric)
        if value is not None:
            self._attr_native_value = value
            self.async_write_ha_state()

    @property
    def available(self) -> bool:
        """Return True if the sensor has a value."""
        return self._handler.get_value(self.entity_description.metric) is not None
