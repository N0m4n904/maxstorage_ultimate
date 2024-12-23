"""Platform for Max Storage Ultimate sensor integration."""
from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass
import logging
from typing import Any

from homeassistant.components.sensor import (
    SensorDeviceClass,
    SensorEntity,
    SensorEntityDescription,
    SensorStateClass,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import PERCENTAGE, UnitOfEnergy, UnitOfPower
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN
from .coordinator import MaxStorageDataUpdateCoordinator

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant, config: ConfigEntry, async_add_entities
):
    """Set up the sensor platform."""
    _LOGGER.debug("sensor.py:async_setup_entry: %s", config)

    coordinator = hass.data[DOMAIN][config.entry_id]["coordinator"]

    sensors: list[MaxStorageSensor] = [
        MaxStorageSensor(coordinator, description) for description in SENSOR_TYPES
    ]
    async_add_entities(sensors)


@dataclass(frozen=True)
class MaxStorageSensorDescriptionMixin:
    """Mixin for sensor descriptions."""

    value_fn: Callable[[dict[str, Any]], str | int | float | None]


@dataclass(frozen=True)
class MaxStorageSensorDescription(
    SensorEntityDescription, MaxStorageSensorDescriptionMixin
):
    """Describes MaxStorage sensor entity."""

    attr_fn: Callable[[dict[str, Any]], dict[str, Any]] = lambda _: {}


class MaxStorageSensor(
    CoordinatorEntity[MaxStorageDataUpdateCoordinator], SensorEntity
):
    """Representation of a MaxStorage sensor."""

    _attr_has_entity_name = True
    entity_description: MaxStorageSensorDescription

    def __init__(
        self,
        coordinator: MaxStorageDataUpdateCoordinator,
        description: MaxStorageSensorDescription,
    ) -> None:
        """Initialize the sensor."""
        super().__init__(coordinator)
        self.entity_description = description
        self._attr_unique_id = (
            f"{coordinator.api.device_info['Ident']}_{description.translation_key}"
        )
        self._attr_device_info = coordinator.device_info

    @property
    def native_value(self) -> str | int | float | None:
        """Return the state of the sensor."""
        return self.entity_description.value_fn(self.coordinator.data)

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        """Return the state attributes of the sensor."""
        return self.entity_description.attr_fn(self.coordinator.data)

    @callback
    def _handle_coordinator_update(self) -> None:
        """Handle updated data from the coordinator."""
        self.async_write_ha_state()


SENSOR_TYPES: tuple[MaxStorageSensorDescription, ...] = (
    MaxStorageSensorDescription(
        key="batterySoC",
        translation_key="battery_soc",
        icon="mdi:battery",
        value_fn=lambda data: data["batterySoC"],
        native_unit_of_measurement=PERCENTAGE,
        state_class=SensorStateClass.MEASUREMENT,
        device_class=SensorDeviceClass.BATTERY,
    ),
    MaxStorageSensorDescription(
        key="batteryCapacity",
        translation_key="battery_capacity",
        icon="mdi:battery",
        value_fn=lambda data: data["batteryCapacity"],
        native_unit_of_measurement=UnitOfEnergy.WATT_HOUR,
        state_class=SensorStateClass.MEASUREMENT,
        device_class=SensorDeviceClass.ENERGY_STORAGE,
    ),
    MaxStorageSensorDescription(
        key="batteryPower",
        translation_key="battery_power",
        icon="mdi:battery",
        value_fn=lambda data: data["batteryPower"],
        native_unit_of_measurement=UnitOfPower.WATT,
        state_class=SensorStateClass.MEASUREMENT,
        device_class=SensorDeviceClass.POWER,
    ),
    MaxStorageSensorDescription(
        key="gridPower",
        translation_key="grid_power",
        icon="mdi:transmission-tower",
        value_fn=lambda data: data["gridPower"],
        native_unit_of_measurement=UnitOfPower.WATT,
        state_class=SensorStateClass.MEASUREMENT,
        device_class=SensorDeviceClass.POWER,
    ),
    MaxStorageSensorDescription(
        key="usagePower",
        translation_key="usage_power",
        icon="mdi:transmission-tower",
        value_fn=lambda data: data["usagePower"],
        native_unit_of_measurement=UnitOfPower.WATT,
        state_class=SensorStateClass.MEASUREMENT,
        device_class=SensorDeviceClass.POWER,
    ),
    MaxStorageSensorDescription(
        key="plantPower",
        translation_key="plant_power",
        icon="mdi:solar-power",
        value_fn=lambda data: data["plantPower"],
        native_unit_of_measurement=UnitOfPower.WATT,
        state_class=SensorStateClass.MEASUREMENT,
        device_class=SensorDeviceClass.POWER,
    ),
    MaxStorageSensorDescription(
        key="storage_dc_power",
        translation_key="storageDCPower",
        icon="mdi:solar-power",
        value_fn=lambda data: data["storageDCPower"],
        native_unit_of_measurement=UnitOfPower.WATT,
        state_class=SensorStateClass.MEASUREMENT,
        device_class=SensorDeviceClass.POWER,
    ),
    MaxStorageSensorDescription(
        key="mppt1Power",
        translation_key="mppt1_power",
        icon="mdi:solar-power",
        value_fn=lambda data: data["storageMPPT1Power"],
        native_unit_of_measurement=UnitOfPower.WATT,
        state_class=SensorStateClass.MEASUREMENT,
        device_class=SensorDeviceClass.POWER,
    ),
    MaxStorageSensorDescription(
        key="mppt2Power",
        translation_key="mppt2_power",
        icon="mdi:solar-power",
        value_fn=lambda data: data["storageMPPT2Power"],
        native_unit_of_measurement=UnitOfPower.WATT,
        state_class=SensorStateClass.MEASUREMENT,
        device_class=SensorDeviceClass.POWER,
    ),
    MaxStorageSensorDescription(
        key="deviceInUpdate",
        translation_key="device_in_update",
        icon="mdi:update",
        value_fn=lambda data: data["SpecialState"]["deviceInUpdate"] == "true",
    ),
    MaxStorageSensorDescription(
        key="dcSwitchOff",
        translation_key="dc_switch_off",
        icon="mdi:toggle-switch-off",
        value_fn=lambda data: data["SpecialState"]["dcSwitchOff"] == "true",
    ),
    MaxStorageSensorDescription(
        key="gridCodeUnknown",
        translation_key="grid_code_unknown",
        icon="mdi:help",
        value_fn=lambda data: data["SpecialState"]["gridCodeUnknown"] == "true",
    ),
    MaxStorageSensorDescription(
        key="inWinterMode",
        translation_key="in_winter_mode",
        icon="mdi:snowflake",
        value_fn=lambda data: data["SpecialState"]["inWinterMode"] == "true",
    ),
    MaxStorageSensorDescription(
        key="inBMZEqualization",
        translation_key="in_bmz_equalization",
        icon="mdi:battery-50",
        value_fn=lambda data: data["SpecialState"]["inBMZEqualization"] == "true",
    ),
    MaxStorageSensorDescription(
        key="inPeakShaving",
        translation_key="in_peak_shaving",
        icon="mdi:flash",
        value_fn=lambda data: data["SpecialState"]["inPeakShaving"] == "true",
    ),
    MaxStorageSensorDescription(
        key="inOptimizationLimit",
        translation_key="in_optimization_limit",
        icon="mdi:tune",
        value_fn=lambda data: data["SpecialState"]["inOptimizationLimit"] == "true",
    ),
    MaxStorageSensorDescription(
        key="inBatteryCalibration",
        translation_key="in_battery_calibration",
        icon="mdi:battery-sync",
        value_fn=lambda data: data["SpecialState"]["inBatteryCalibration"] == "true",
    ),
    MaxStorageSensorDescription(
        key="noPowerMeter",
        translation_key="no_power_meter",
        icon="mdi:diameter-variant",
        value_fn=lambda data: data["SpecialState"]["noPowerMeter"] == "true",
    ),
    MaxStorageSensorDescription(
        key="gridError",
        translation_key="grid_error",
        icon="mdi:alert-circle-outline",
        value_fn=lambda data: data["SpecialState"]["gridError"] == "true",
    ),
    MaxStorageSensorDescription(
        key="gridLocked",
        translation_key="grid_locked",
        icon="mdi:lock",
        value_fn=lambda data: data["SpecialState"]["gridLocked"] == "true",
    ),
    MaxStorageSensorDescription(
        key="islandActive",
        translation_key="island_active",
        icon="mdi:island",
        value_fn=lambda data: data["SpecialState"]["islandActive"] == "true",
    ),
    MaxStorageSensorDescription(
        key="serviceMode",
        translation_key="service_mode",
        icon="mdi:toolbox-outline",
        value_fn=lambda data: data["SpecialState"]["serviceMode"] == "true",
    ),
)
