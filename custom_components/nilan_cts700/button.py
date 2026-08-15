"""Button entities for Nilan CTS700."""

from __future__ import annotations

from homeassistant.components.button import ButtonEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import DOMAIN, ROLE_COMPACT
from .coordinator import NilanDataUpdateCoordinator
from .entity import NilanEntity


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up Nilan buttons."""
    coordinator: NilanDataUpdateCoordinator = hass.data[DOMAIN][entry.entry_id]
    async_add_entities([NilanResetAlarmsButton(coordinator)])


class NilanResetAlarmsButton(NilanEntity, ButtonEntity):
    """Reset active alarms on the Compact P controller."""

    _attr_icon = "mdi:alarm-light-off"

    def __init__(self, coordinator: NilanDataUpdateCoordinator) -> None:
        """Initialize the button."""
        super().__init__(
            coordinator,
            name="Nilan nulstil alarmer",
            unique_id="nilan_reset_alarms",
            role=ROLE_COMPACT,
        )

    async def async_press(self) -> None:
        """Send the documented CTS700 alarm reset magic value."""
        await self.coordinator.async_write(ROLE_COMPACT, 22491, 48815)
