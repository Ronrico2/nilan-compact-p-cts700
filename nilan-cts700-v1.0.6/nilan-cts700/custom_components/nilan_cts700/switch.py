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
    optimistic: bool = False


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
        # Some AIR9 firmware accepts writes to 20602 but keeps returning 0.
        # Preserve the last successful command so toggle and dashboard colour
        # remain usable instead of immediately falling back to off.
        optimistic=True,
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
        self._optimistic_is_on: bool | None = None
        self._attr_assumed_state = description.optimistic

    @property
    def is_on(self) -> bool | None:
        """Return the current switch state."""
        if self.entity_description.optimistic and self._optimistic_is_on is not None:
            return self._optimistic_is_on
        value = self.raw_value()
        return None if value is None else value == 1

    async def async_turn_on(self, **kwargs) -> None:
        """Turn the setting on."""
        await self._async_set_state(True)

    async def async_turn_off(self, **kwargs) -> None:
        """Turn the setting off."""
        await self._async_set_state(False)

    async def _async_set_state(self, turn_on: bool) -> None:
        """Write a switch command and retain it for write-only-style firmware."""
        previous_state = self._optimistic_is_on
        if self.entity_description.optimistic:
            self._optimistic_is_on = turn_on
            self.async_write_ha_state()

        try:
            await self.coordinator.async_write(
                self.role,
                self.entity_description.address,
                int(turn_on),
            )
        except Exception:
            self._optimistic_is_on = previous_state
            self.async_write_ha_state()
            raise
