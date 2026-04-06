"""Sensors for TAC2100."""

from __future__ import annotations

from dataclasses import dataclass

from homeassistant.components.sensor import (
    SensorDeviceClass,
    SensorEntity,
    SensorEntityDescription,
    SensorStateClass,
)
from homeassistant.const import (
    DEGREE,
    UnitOfApparentPower,
    UnitOfElectricCurrent,
    UnitOfElectricPotential,
    UnitOfEnergy,
    UnitOfFrequency,
    UnitOfPower,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity import DeviceInfo
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN
from .coordinator import Tac2100Coordinator


@dataclass(frozen=True, kw_only=True)
class Tac2100SensorEntityDescription(SensorEntityDescription):
    """Describe TAC2100 sensor entities."""

    value_key: str
    apply_import_offset: bool = False
    apply_export_offset: bool = False
    decimals: int | None = None


SENSOR_TYPES: tuple[Tac2100SensorEntityDescription, ...] = (
    Tac2100SensorEntityDescription(
        key="voltage",
        translation_key="voltage",
        value_key="voltage",
        native_unit_of_measurement=UnitOfElectricPotential.VOLT,
        device_class=SensorDeviceClass.VOLTAGE,
        state_class=SensorStateClass.MEASUREMENT,
        decimals=2,
    ),
    Tac2100SensorEntityDescription(
        key="current",
        translation_key="current",
        value_key="current",
        native_unit_of_measurement=UnitOfElectricCurrent.AMPERE,
        device_class=SensorDeviceClass.CURRENT,
        state_class=SensorStateClass.MEASUREMENT,
        decimals=3,
    ),
    Tac2100SensorEntityDescription(
        key="active_power",
        translation_key="active_power",
        value_key="active_power",
        native_unit_of_measurement=UnitOfPower.WATT,
        device_class=SensorDeviceClass.POWER,
        state_class=SensorStateClass.MEASUREMENT,
        decimals=2,
    ),
    Tac2100SensorEntityDescription(
        key="reactive_power",
        translation_key="reactive_power",
        value_key="reactive_power",
        native_unit_of_measurement="var",
        device_class=SensorDeviceClass.REACTIVE_POWER,
        state_class=SensorStateClass.MEASUREMENT,
        decimals=2,
    ),
    Tac2100SensorEntityDescription(
        key="apparent_power",
        translation_key="apparent_power",
        value_key="apparent_power",
        native_unit_of_measurement=UnitOfApparentPower.VOLT_AMPERE,
        device_class=SensorDeviceClass.APPARENT_POWER,
        state_class=SensorStateClass.MEASUREMENT,
        decimals=2,
    ),
    Tac2100SensorEntityDescription(
        key="power_factor",
        translation_key="power_factor",
        value_key="power_factor",
        native_unit_of_measurement=None,
        device_class=SensorDeviceClass.POWER_FACTOR,
        state_class=SensorStateClass.MEASUREMENT,
        decimals=3,
    ),
    Tac2100SensorEntityDescription(
        key="phase_angle",
        translation_key="phase_angle",
        value_key="phase_angle",
        native_unit_of_measurement=DEGREE,
        device_class=None,
        state_class=SensorStateClass.MEASUREMENT,
        decimals=2,
    ),
    Tac2100SensorEntityDescription(
        key="frequency",
        translation_key="frequency",
        value_key="frequency",
        native_unit_of_measurement=UnitOfFrequency.HERTZ,
        device_class=SensorDeviceClass.FREQUENCY,
        state_class=SensorStateClass.MEASUREMENT,
        decimals=2,
    ),
    Tac2100SensorEntityDescription(
        key="load_nature",
        translation_key="load_nature",
        value_key="load_nature",
        native_unit_of_measurement=None,
        device_class=None,
        state_class=SensorStateClass.MEASUREMENT,
        decimals=0,
    ),
    Tac2100SensorEntityDescription(
        key="active_power_demand",
        translation_key="active_power_demand",
        value_key="active_power_demand",
        native_unit_of_measurement=UnitOfPower.WATT,
        device_class=SensorDeviceClass.POWER,
        state_class=SensorStateClass.MEASUREMENT,
        decimals=2,
    ),
    Tac2100SensorEntityDescription(
        key="reactive_power_demand",
        translation_key="reactive_power_demand",
        value_key="reactive_power_demand",
        native_unit_of_measurement="var",
        device_class=SensorDeviceClass.REACTIVE_POWER,
        state_class=SensorStateClass.MEASUREMENT,
        decimals=2,
    ),
    Tac2100SensorEntityDescription(
        key="apparent_power_demand",
        translation_key="apparent_power_demand",
        value_key="apparent_power_demand",
        native_unit_of_measurement=UnitOfApparentPower.VOLT_AMPERE,
        device_class=SensorDeviceClass.APPARENT_POWER,
        state_class=SensorStateClass.MEASUREMENT,
        decimals=2,
    ),
    Tac2100SensorEntityDescription(
        key="current_demand",
        translation_key="current_demand",
        value_key="current_demand",
        native_unit_of_measurement=UnitOfElectricCurrent.AMPERE,
        device_class=SensorDeviceClass.CURRENT,
        state_class=SensorStateClass.MEASUREMENT,
        decimals=3,
    ),
    Tac2100SensorEntityDescription(
        key="import_active_power_demand",
        translation_key="import_active_power_demand",
        value_key="import_active_power_demand",
        native_unit_of_measurement=UnitOfPower.WATT,
        device_class=SensorDeviceClass.POWER,
        state_class=SensorStateClass.MEASUREMENT,
        decimals=2,
    ),
    Tac2100SensorEntityDescription(
        key="export_active_power_demand",
        translation_key="export_active_power_demand",
        value_key="export_active_power_demand",
        native_unit_of_measurement=UnitOfPower.WATT,
        device_class=SensorDeviceClass.POWER,
        state_class=SensorStateClass.MEASUREMENT,
        decimals=2,
    ),
    Tac2100SensorEntityDescription(
        key="max_active_power_demand",
        translation_key="max_active_power_demand",
        value_key="max_active_power_demand",
        native_unit_of_measurement=UnitOfPower.WATT,
        device_class=SensorDeviceClass.POWER,
        state_class=SensorStateClass.MEASUREMENT,
        decimals=2,
    ),
    Tac2100SensorEntityDescription(
        key="max_reactive_power_demand",
        translation_key="max_reactive_power_demand",
        value_key="max_reactive_power_demand",
        native_unit_of_measurement="var",
        device_class=SensorDeviceClass.REACTIVE_POWER,
        state_class=SensorStateClass.MEASUREMENT,
        decimals=2,
    ),
    Tac2100SensorEntityDescription(
        key="max_apparent_power_demand",
        translation_key="max_apparent_power_demand",
        value_key="max_apparent_power_demand",
        native_unit_of_measurement=UnitOfApparentPower.VOLT_AMPERE,
        device_class=SensorDeviceClass.APPARENT_POWER,
        state_class=SensorStateClass.MEASUREMENT,
        decimals=2,
    ),
    Tac2100SensorEntityDescription(
        key="max_current_demand",
        translation_key="max_current_demand",
        value_key="max_current_demand",
        native_unit_of_measurement=UnitOfElectricCurrent.AMPERE,
        device_class=SensorDeviceClass.CURRENT,
        state_class=SensorStateClass.MEASUREMENT,
        decimals=3,
    ),
    Tac2100SensorEntityDescription(
        key="max_import_active_power_demand",
        translation_key="max_import_active_power_demand",
        value_key="max_import_active_power_demand",
        native_unit_of_measurement=UnitOfPower.WATT,
        device_class=SensorDeviceClass.POWER,
        state_class=SensorStateClass.MEASUREMENT,
        decimals=2,
    ),
    Tac2100SensorEntityDescription(
        key="max_export_active_power_demand",
        translation_key="max_export_active_power_demand",
        value_key="max_export_active_power_demand",
        native_unit_of_measurement=UnitOfPower.WATT,
        device_class=SensorDeviceClass.POWER,
        state_class=SensorStateClass.MEASUREMENT,
        decimals=2,
    ),
    Tac2100SensorEntityDescription(
        key="total_import_active_energy",
        translation_key="total_import_active_energy",
        value_key="total_import_active_energy_raw",
        native_unit_of_measurement=UnitOfEnergy.KILO_WATT_HOUR,
        device_class=SensorDeviceClass.ENERGY,
        state_class=SensorStateClass.TOTAL_INCREASING,
        suggested_display_precision=3,
        apply_import_offset=True,
    ),
    Tac2100SensorEntityDescription(
        key="total_export_active_energy",
        translation_key="total_export_active_energy",
        value_key="total_export_active_energy_raw",
        native_unit_of_measurement=UnitOfEnergy.KILO_WATT_HOUR,
        device_class=SensorDeviceClass.ENERGY,
        state_class=SensorStateClass.TOTAL_INCREASING,
        suggested_display_precision=3,
        apply_export_offset=True,
    ),
    Tac2100SensorEntityDescription(
        key="total_active_energy",
        translation_key="total_active_energy",
        value_key="total_active_energy_raw",
        native_unit_of_measurement=UnitOfEnergy.KILO_WATT_HOUR,
        device_class=SensorDeviceClass.ENERGY,
        state_class=SensorStateClass.TOTAL_INCREASING,
        suggested_display_precision=3,
    ),
    Tac2100SensorEntityDescription(
        key="total_import_reactive_energy",
        translation_key="total_import_reactive_energy",
        value_key="total_import_reactive_energy_raw",
        native_unit_of_measurement="kvarh",
        device_class=None,
        state_class=SensorStateClass.TOTAL_INCREASING,
        suggested_display_precision=3,
    ),
    Tac2100SensorEntityDescription(
        key="total_export_reactive_energy",
        translation_key="total_export_reactive_energy",
        value_key="total_export_reactive_energy_raw",
        native_unit_of_measurement="kvarh",
        device_class=None,
        state_class=SensorStateClass.TOTAL_INCREASING,
        suggested_display_precision=3,
    ),
    Tac2100SensorEntityDescription(
        key="total_reactive_energy",
        translation_key="total_reactive_energy",
        value_key="total_reactive_energy_raw",
        native_unit_of_measurement="kvarh",
        device_class=None,
        state_class=SensorStateClass.TOTAL_INCREASING,
        suggested_display_precision=3,
    ),
)


async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    async_add_entities,
) -> None:
    """Set up TAC2100 sensors."""
    coordinator: Tac2100Coordinator = hass.data[DOMAIN][config_entry.entry_id]
    async_add_entities(
        Tac2100Sensor(coordinator, description) for description in SENSOR_TYPES
    )


class Tac2100Sensor(CoordinatorEntity[Tac2100Coordinator], SensorEntity):
    """Representation of a TAC2100 sensor."""

    entity_description: Tac2100SensorEntityDescription
    _attr_has_entity_name = True

    def __init__(
        self,
        coordinator: Tac2100Coordinator,
        description: Tac2100SensorEntityDescription,
    ) -> None:
        super().__init__(coordinator)
        self.entity_description = description
        self._attr_unique_id = f"{coordinator.config_entry.entry_id}_{description.key}"
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, coordinator.config_entry.entry_id)},
            name=coordinator.config_entry.title,
            manufacturer="Wenzhou Taiye Electric Co., Ltd.",
            model="TAC2100",
        )

    @property
    def native_value(self) -> float | int | None:
        """Return sensor state."""
        raw = self.coordinator.data.get(self.entity_description.value_key)
        if raw is None:
            return None
        val = float(raw)
        if self.entity_description.apply_import_offset:
            val += self.coordinator.import_energy_offset
        elif self.entity_description.apply_export_offset:
            val += self.coordinator.export_energy_offset
        if self.entity_description.decimals is not None:
            if self.entity_description.decimals == 0:
                return int(round(val))
            return round(val, self.entity_description.decimals)
        return val
