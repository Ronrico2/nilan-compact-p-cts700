"""Switch entities for Nilan CTS700."""

from __future__ import annotations

from dataclasses import dataclass

from homeassistant.components.switch import SwitchEntity, SwitchEntityDescription
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import DOMAIN, ROLE_AIR9, ROLE_COMPACT
from .coordinator import NilanDataUpdateCoordinator
from .entity import NilanEntity


@dataclass(frozen=True, kw_only=True)
class NilanSwitchDescription(SwitchEntityDescription):
    """Describe a writable Nilan switch register."""

    role: str
    address: int


SWITCHES: tuple[NilanSwitchDescription, ...] = (
    NilanSwitchDescription(
        key="nilan_ventilation_pause",
        name="Nilan ventilationspause",
        role=ROLE_COMPACT,
        address=20100,
        icon="mdi:fan-off",
    ),
    NilanSwitchDescription(
        key="nilan_active_cooling",
        name="Nilan aktiv køling",
        role=ROLE_COMPACT,
        address=20180,
        icon="mdi:snowflake",
    ),
    NilanSwitchDescription(
        key="nilan_hot_water_electric_supplement",
        name="Nilan eltilskud til varmt vand",
        role=ROLE_COMPACT,
        address=20464,
        icon="mdi:water-boiler",
    ),
    NilanSwitchDescription(
        key="nilan_central_heating_power",
        name="Nilan centralvarme drift",
        role=ROLE_AIR9,
        address=20602,
        icon="mdi:radiator",
    ),
    NilanSwitchDescription(
        key="nilan_buffer_electric_supplement",
        name="Nilan eltilskud til buffertank",
        role=ROLE_AIR9,
        address=20700,
        icon="mdi:heat-wave",
    ),
)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up Nilan switches."""
    coordinator: NilanDataUpdateCoordinator = hass.data[DOMAIN][entry.entry_id]
    async_add_entities(
        NilanSwitch(coordinator, description)
        for description in SWITCHES
        if description.role != ROLE_AIR9 or coordinator.api.use_air9
    )


class NilanSwitch(NilanEntity, SwitchEntity):
    """Representation of a Nilan switch."""

    entity_description: NilanSwitchDescription

    def __init__(
        self,
        coordinator: NilanDataUpdateCoordinator,
        description: NilanSwitchDescription,
    ) -> None:
        """Initialize the switch."""
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
        """Return the current switch state."""
        value = self.raw_value()
        return None if value is None else value == 1

    async def async_turn_on(self, **kwargs) -> None:
        """Turn the setting on."""
        await self.coordinator.async_write(self.role, self.entity_description.address, 1)

    async def async_turn_off(self, **kwargs) -> None:
        """Turn the setting off."""
        await self.coordinator.async_write(self.role, self.entity_description.address, 0)
