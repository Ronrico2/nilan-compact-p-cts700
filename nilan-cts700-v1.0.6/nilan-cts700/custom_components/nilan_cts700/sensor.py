"""Sensor entities for Nilan CTS700."""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass

from homeassistant.components.sensor import (
    SensorDeviceClass,
    SensorEntity,
    SensorEntityDescription,
    SensorStateClass,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import (
    CONCENTRATION_PARTS_PER_MILLION,
    PERCENTAGE,
    UnitOfTemperature,
    UnitOfTime,
)
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import DOMAIN, ROLE_AIR9, ROLE_COMPACT
from .coordinator import NilanDataUpdateCoordinator
from .entity import NilanEntity


@dataclass(frozen=True, kw_only=True)
class NilanSensorDescription(SensorEntityDescription):
    """Describe a Nilan register sensor."""

    role: str
    address: int
    signed: bool = False
    scale: float = 1.0
    value_map: Mapping[int, str] | None = None


def _temperature(key: str, name: str, role: str, address: int) -> NilanSensorDescription:
    return NilanSensorDescription(
        key=key,
        name=name,
        role=role,
        address=address,
        signed=True,
        scale=0.1,
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        device_class=SensorDeviceClass.TEMPERATURE,
        state_class=SensorStateClass.MEASUREMENT,
    )


def _percentage(key: str, name: str, role: str, address: int) -> NilanSensorDescription:
    return NilanSensorDescription(
        key=key,
        name=name,
        role=role,
        address=address,
        native_unit_of_measurement=PERCENTAGE,
        state_class=SensorStateClass.MEASUREMENT,
    )


SENSORS: tuple[NilanSensorDescription, ...] = (
    NilanSensorDescription(
        key="nilan_outdoor_filter_interval_raw",
        name="Nilan filterinterval udeluft intern",
        role=ROLE_COMPACT,
        address=20102,
        native_unit_of_measurement=UnitOfTime.DAYS,
    ),
    NilanSensorDescription(
        key="nilan_outdoor_filter_days_remaining",
        name="Nilan dage til skift af udeluftfilter",
        role=ROLE_COMPACT,
        address=20103,
        native_unit_of_measurement=UnitOfTime.DAYS,
    ),
    NilanSensorDescription(
        key="nilan_exhaust_filter_interval_raw",
        name="Nilan filterinterval udsugning intern",
        role=ROLE_COMPACT,
        address=20106,
        native_unit_of_measurement=UnitOfTime.DAYS,
    ),
    NilanSensorDescription(
        key="nilan_exhaust_filter_days_remaining",
        name="Nilan dage til skift af udsugningsfilter",
        role=ROLE_COMPACT,
        address=20107,
        native_unit_of_measurement=UnitOfTime.DAYS,
    ),
    NilanSensorDescription(
        key="nilan_average_humidity",
        name="Nilan gennemsnitlig luftfugtighed",
        role=ROLE_COMPACT,
        address=20164,
        native_unit_of_measurement=PERCENTAGE,
        device_class=SensorDeviceClass.HUMIDITY,
        state_class=SensorStateClass.MEASUREMENT,
    ),
    _percentage(
        "nilan_fan_level_1_supply_setting",
        "Nilan blæsertrin 1 tilluft",
        ROLE_COMPACT,
        20140,
    ),
    _percentage(
        "nilan_fan_level_1_exhaust_setting",
        "Nilan blæsertrin 1 udsugning",
        ROLE_COMPACT,
        20141,
    ),
    _percentage(
        "nilan_fan_level_2_supply_setting",
        "Nilan blæsertrin 2 tilluft",
        ROLE_COMPACT,
        20142,
    ),
    _percentage(
        "nilan_fan_level_2_exhaust_setting",
        "Nilan blæsertrin 2 udsugning",
        ROLE_COMPACT,
        20143,
    ),
    _percentage(
        "nilan_fan_level_3_supply_setting",
        "Nilan blæsertrin 3 tilluft",
        ROLE_COMPACT,
        20144,
    ),
    _percentage(
        "nilan_fan_level_3_exhaust_setting",
        "Nilan blæsertrin 3 udsugning",
        ROLE_COMPACT,
        20145,
    ),
    _percentage(
        "nilan_fan_level_4_supply_setting",
        "Nilan blæsertrin 4 tilluft",
        ROLE_COMPACT,
        20146,
    ),
    _percentage(
        "nilan_fan_level_4_exhaust_setting",
        "Nilan blæsertrin 4 udsugning",
        ROLE_COMPACT,
        20147,
    ),
    _temperature(
        "nilan_summer_winter_threshold_raw",
        "Nilan sommer vinter temperatur intern",
        ROLE_COMPACT,
        20261,
    ),
    _temperature(
        "nilan_frost_protection_threshold_raw",
        "Nilan frostsikring temperatur intern",
        ROLE_COMPACT,
        20340,
    ),
    _temperature(
        "nilan_hot_water_electric_threshold_raw",
        "Nilan varmtvand el temperatur intern",
        ROLE_COMPACT,
        20462,
    ),
    _temperature(
        "nilan_t1_outdoor_temperature",
        "Nilan T1 udendørstemperatur",
        ROLE_COMPACT,
        20282,
    ),
    _temperature(
        "nilan_t2_supply_air_temperature",
        "Nilan T2 tilluftstemperatur",
        ROLE_COMPACT,
        20284,
    ),
    _temperature(
        "nilan_t3_extract_air_temperature",
        "Nilan T3 fraluftstemperatur",
        ROLE_COMPACT,
        20286,
    ),
    _temperature(
        "nilan_t4_exhaust_after_exchanger",
        "Nilan T4 afkast efter veksler",
        ROLE_COMPACT,
        20288,
    ),
    _temperature(
        "nilan_t5_exhaust_after_heat_pump",
        "Nilan T5 afkast efter varmepumpe",
        ROLE_COMPACT,
        20290,
    ),
    _temperature(
        "nilan_t6_evaporator_temperature",
        "Nilan T6 fordampertemperatur",
        ROLE_COMPACT,
        20292,
    ),
    _temperature(
        "nilan_t7_supply_after_heater",
        "Nilan T7 tilluft efter varmelegeme",
        ROLE_COMPACT,
        20294,
    ),
    _temperature(
        "nilan_t8_outdoor_before_preheater",
        "Nilan T8 udeluft før forvarmer",
        ROLE_COMPACT,
        20296,
    ),
    _temperature(
        "nilan_t9_water_after_heater",
        "Nilan T9 vand efter varmelegeme",
        ROLE_COMPACT,
        20298,
    ),
    _temperature(
        "nilan_t11_hot_water_top",
        "Nilan T11 varmtvandsbeholder top",
        ROLE_COMPACT,
        20520,
    ),
    _temperature(
        "nilan_t12_hot_water_bottom",
        "Nilan T12 varmtvandsbeholder bund",
        ROLE_COMPACT,
        20522,
    ),
    NilanSensorDescription(
        key="nilan_system_state_raw",
        name="Nilan systemtilstand intern",
        role=ROLE_COMPACT,
        address=21770,
    ),
    _percentage(
        "nilan_actual_supply_fan_speed",
        "Nilan faktisk tilluftventilatorhastighed",
        ROLE_COMPACT,
        21771,
    ),
    _percentage(
        "nilan_actual_exhaust_fan_speed",
        "Nilan faktisk udsugningsventilatorhastighed",
        ROLE_COMPACT,
        21772,
    ),
    _percentage(
        "nilan_afterheater_output",
        "Nilan eftervarmeflade ydelse",
        ROLE_COMPACT,
        21774,
    ),
    NilanSensorDescription(
        key="nilan_actual_humidity",
        name="Nilan faktisk luftfugtighed",
        role=ROLE_COMPACT,
        address=21776,
        native_unit_of_measurement=PERCENTAGE,
        device_class=SensorDeviceClass.HUMIDITY,
        state_class=SensorStateClass.MEASUREMENT,
    ),
    NilanSensorDescription(
        key="nilan_co2_level",
        name="Nilan CO2-niveau",
        role=ROLE_COMPACT,
        address=21778,
        native_unit_of_measurement=CONCENTRATION_PARTS_PER_MILLION,
        device_class=SensorDeviceClass.CO2,
        state_class=SensorStateClass.MEASUREMENT,
    ),
    NilanSensorDescription(
        key="nilan_four_way_valve_raw",
        name="Nilan firevejsventil intern",
        role=ROLE_COMPACT,
        address=21791,
    ),
    _temperature(
        "nilan_air_t17_outdoor_unit_supply",
        "Nilan AIR T17 fremløb udendørsenhed",
        ROLE_AIR9,
        20684,
    ),
    _temperature(
        "nilan_air_t18_buffer_supply",
        "Nilan AIR T18 fremløb buffertank",
        ROLE_AIR9,
        20686,
    ),
    _temperature(
        "nilan_air_t20_outdoor_temperature",
        "Nilan AIR T20 udendørstemperatur",
        ROLE_AIR9,
        20688,
    ),
    _temperature(
        "nilan_air_t23_evaporator_temperature",
        "Nilan AIR T23 fordampertemperatur",
        ROLE_AIR9,
        20690,
    ),
    NilanSensorDescription(
        key="nilan_air_system_state_raw",
        name="Nilan AIR systemtilstand intern",
        role=ROLE_AIR9,
        address=21900,
    ),
    _percentage(
        "nilan_air_evaporator_fan_speed",
        "Nilan AIR fordamperventilatorhastighed",
        ROLE_AIR9,
        21901,
    ),
    _percentage(
        "nilan_air_compressor_level",
        "Nilan AIR kompressorniveau",
        ROLE_AIR9,
        21902,
    ),
    NilanSensorDescription(
        key="nilan_air_three_way_valve_raw",
        name="Nilan AIR trevejsventil intern",
        role=ROLE_AIR9,
        address=21905,
    ),
    NilanSensorDescription(
        key="nilan_system_state",
        name="Nilan systemtilstand",
        role=ROLE_COMPACT,
        address=21770,
        icon="mdi:hvac",
        device_class=SensorDeviceClass.ENUM,
        value_map={0: "Auto", 1: "Køling", 2: "Opvarmning"},
    ),
    NilanSensorDescription(
        key="nilan_four_way_valve",
        name="Nilan firevejsventil",
        role=ROLE_COMPACT,
        address=21791,
        icon="mdi:valve",
        device_class=SensorDeviceClass.ENUM,
        value_map={0: "Åben", 1: "Lukket"},
    ),
    NilanSensorDescription(
        key="nilan_air_system_state",
        name="Nilan AIR systemtilstand",
        role=ROLE_AIR9,
        address=21900,
        icon="mdi:heat-pump",
        device_class=SensorDeviceClass.ENUM,
        value_map={0: "Auto", 1: "Køling", 2: "Opvarmning"},
    ),
    NilanSensorDescription(
        key="nilan_air_three_way_valve",
        name="Nilan AIR trevejsventil",
        role=ROLE_AIR9,
        address=21905,
        icon="mdi:valve",
        device_class=SensorDeviceClass.ENUM,
        value_map={0: "Gulvvarme", 1: "Varmt vand"},
    ),
)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up Nilan sensors."""
    coordinator: NilanDataUpdateCoordinator = hass.data[DOMAIN][entry.entry_id]
    async_add_entities(
        NilanSensor(coordinator, description)
        for description in SENSORS
        if description.role != ROLE_AIR9 or coordinator.api.use_air9
    )


class NilanSensor(NilanEntity, SensorEntity):
    """Representation of a Nilan sensor."""

    entity_description: NilanSensorDescription

    def __init__(
        self,
        coordinator: NilanDataUpdateCoordinator,
        description: NilanSensorDescription,
    ) -> None:
        """Initialize the sensor."""
        NilanEntity.__init__(
            self,
            coordinator,
            name=description.name or description.key,
            unique_id=description.key,
            role=description.role,
            address=description.address,
        )
        self.entity_description = description
        if description.value_map:
            self._attr_options = list(description.value_map.values()) + ["Ukendt"]

    @property
    def native_value(self) -> int | float | str | None:
        """Return the decoded sensor state."""
        value = self.decoded_value(
            signed=self.entity_description.signed,
            scale=self.entity_description.scale,
        )
        if value is None:
            return None
        if self.entity_description.value_map is not None:
            return self.entity_description.value_map.get(int(value), "Ukendt")
        return value
