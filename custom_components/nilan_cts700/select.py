"""Ventilation level selector for Nilan CTS700."""

from __future__ import annotations

import asyncio
from time import monotonic

from homeassistant.components.select import SelectEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import DOMAIN, FAN_COMMANDS, FAN_OPTIONS, ROLE_COMPACT
from .coordinator import NilanDataUpdateCoordinator
from .entity import NilanEntity

OPTIMISTIC_TIMEOUT = 45


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up the Nilan ventilation selector."""
    coordinator: NilanDataUpdateCoordinator = hass.data[DOMAIN][entry.entry_id]
    async_add_entities([NilanVentilationSelect(coordinator)])


class NilanVentilationSelect(NilanEntity, SelectEntity):
    """Select the current Nilan ventilation level."""

    _attr_icon = "mdi:fan"
    _attr_options = list(FAN_OPTIONS)

    def __init__(self, coordinator: NilanDataUpdateCoordinator) -> None:
        """Initialize the selector."""
        super().__init__(
            coordinator,
            name="Nilan ventilationstrin",
            unique_id="nilan_ventilation_level_control",
            role=ROLE_COMPACT,
            address=21771,
        )
        self._optimistic_option: str | None = None
        self._optimistic_until = 0.0

    @property
    def current_option(self) -> str | None:
        """Infer the active level from pause state and actual fan speed."""
        measured_option = self._measured_option()
        if self._optimistic_option is None:
            return measured_option
        if measured_option == self._optimistic_option or monotonic() >= self._optimistic_until:
            self._optimistic_option = None
            return measured_option
        return self._optimistic_option

    def _measured_option(self) -> str | None:
        """Calculate the measured ventilation level."""
        pause = self.raw_value(20100)
        actual = self.raw_value(21771)
        if pause is None or actual is None:
            return None
        if pause == 1 or actual < 1:
            return "Slukket"

        configured = (
            self.raw_value(20140),
            self.raw_value(20142),
            self.raw_value(20144),
            self.raw_value(20146),
        )
        if any(value is None for value in configured):
            return None
        differences = [abs(actual - int(value)) for value in configured]
        return f"Trin {differences.index(min(differences)) + 1}"

    async def async_select_option(self, option: str) -> None:
        """Set ventilation off or issue a CTS700 user-function fan command."""
        if option not in FAN_OPTIONS:
            raise ValueError(f"Ukendt ventilationstrin: {option}")

        self._optimistic_option = option
        self._optimistic_until = monotonic() + OPTIMISTIC_TIMEOUT
        self.async_write_ha_state()

        try:
            if option == "Slukket":
                await self.coordinator.async_write(ROLE_COMPACT, 20100, 1)
            else:
                await self.coordinator.api.async_write_register(
                    ROLE_COMPACT, 4747, FAN_COMMANDS[option]
                )
                await asyncio.sleep(0.3)
                await self.coordinator.async_write(ROLE_COMPACT, 20100, 0)
        except Exception:
            self._optimistic_option = None
            self.async_write_ha_state()
            raise

        self.hass.async_create_task(self._async_delayed_refresh())

    async def _async_delayed_refresh(self) -> None:
        """Confirm the commanded fan level without delaying the UI action."""
        await asyncio.sleep(2)
        await self.coordinator.async_request_refresh()
