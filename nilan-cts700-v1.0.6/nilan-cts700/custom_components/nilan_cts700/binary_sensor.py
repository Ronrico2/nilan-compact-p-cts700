"""Binary sensor entities for Nilan CTS700."""

from __future__ import annotations

from dataclasses import dataclass

from homeassistant.components.binary_sensor import (
    BinarySensorDeviceClass,
    BinarySensorEntity,
    BinarySensorEntityDescription,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import DOMAIN, ROLE_AIR9, ROLE_COMPACT
from .coordinator import NilanDataUpdateCoordinator
from .entity import NilanEntity


@dataclass(frozen=True, kw_only=True)
class NilanBinarySensorDescription(BinarySensorEntityDescription):
    """Describe a Nilan binary sensor."""

    role: str
    address: int


BINARY_SENSORS: tuple[NilanBinarySensorDescription, ...] = (
    NilanBinarySensorDescription(
        key="nilan_bypass_open",
        name="Nilan bypass åben",
        role=ROLE_COMPACT,
        address=21773,
    ),
    NilanBinarySensorDescription(
        key="nilan_compressor_active",
        name="Nilan kompressor aktiv",
        role=ROLE_COMPACT,
        address=21775,
    ),
    NilanBinarySensorDescription(
        key="nilan_user_program_1_active",
        name="Nilan brugerprogram 1 aktivt",
        role=ROLE_COMPACT,
        address=21780,
    ),
    NilanBinarySensorDescription(
        key="nilan_user_program_2_active",
        name="Nilan brugerprogram 2 aktivt",
        role=ROLE_COMPACT,
        address=21781,
    ),
    NilanBinarySensorDescription(
        key="nilan_hot_water_electric_supplement_active",
        name="Nilan eltilskud til varmt vand aktivt",
        role=ROLE_COMPACT,
        address=21788,
    ),
    NilanBinarySensorDescription(
        key="nilan_alarm_active",
        name="Nilan alarm aktiv",
        role=ROLE_COMPACT,
        address=22490,
        device_class=BinarySensorDeviceClass.PROBLEM,
    ),
    NilanBinarySensorDescription(
        key="nilan_air_circulation_pump_active",
        name="Nilan AIR cirkulationspumpe aktiv",
        role=ROLE_AIR9,
        address=21903,
        device_class=BinarySensorDeviceClass.RUNNING,
    ),
    NilanBinarySensorDescription(
        key="nilan_air_central_heating_pump_active",
        name="Nilan AIR centralvarmepumpe aktiv",
        role=ROLE_AIR9,
        address=21904,
        device_class=BinarySensorDeviceClass.RUNNING,
    ),
    NilanBinarySensorDescription(
        key="nilan_air_buffer_supplement_active",
        name="Nilan AIR eltilskud til buffertank aktivt",
        role=ROLE_AIR9,
        address=21913,
    ),
)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up Nilan binary sensors."""
    coordinator: NilanDataUpdateCoordinator = hass.data[DOMAIN][entry.entry_id]
    async_add_entities(
        NilanBinarySensor(coordinator, description)
        for description in BINARY_SENSORS
        if description.role != ROLE_AIR9 or coordinator.api.use_air9
    )


class NilanBinarySensor(NilanEntity, BinarySensorEntity):
    """Representation of a Nilan binary sensor."""

    entity_description: NilanBinarySensorDescription

    def __init__(
        self,
        coordinator: NilanDataUpdateCoordinator,
        description: NilanBinarySensorDescription,
    ) -> None:
        """Initialize the binary sensor."""
        NilanEntity.__init__(
            self,
            coordinator,
            name=description.name or description.key,
            unique_id=description.key,
            role=description.role,
            address=description.address,
        )
        self.entity_description = description

    @property
    def is_on(self) -> bool | None:
        """Return true when the register is non-zero."""
        value = self.raw_value()
        return None if value is None else bool(value)
