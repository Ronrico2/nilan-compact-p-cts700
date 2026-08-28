"""Ventilation level selector for Nilan CTS700."""

from __future__ import annotations

import asyncio

from homeassistant.components.select import SelectEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import DOMAIN, FAN_COMMANDS, FAN_OPTIONS, ROLE_COMPACT
from .coordinator import NilanDataUpdateCoordinator
from .entity import NilanEntity


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
        # CTS700 exposes the measured fan percentage, but not a reliable
        # readable register for the last user-function level command. Keep the
        # commanded option locally so the selector and Picture Elements image
        # do not jump back to whichever configured level happens to be nearest
        # to the measured percentage.
        self._commanded_option: str | None = None
        self._attr_assumed_state = True

    @property
    def current_option(self) -> str | None:
        """Return the commanded level, or infer an initial level after startup."""
        if self._commanded_option is not None:
            return self._commanded_option
        return self._measured_option()

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

        previous_option = self._commanded_option
        self._commanded_option = option
        self.async_write_ha_state()

        try:
            if option == "Slukket":
                await self.coordinator.async_write(ROLE_COMPACT, 20100, 1)
            else:
                # CTS700 can ignore the fan command while ventilation pause is
                # active. Always release the pause before selecting a level so
                # the unit cannot remain stopped after choosing "Slukket".
                await self.coordinator.async_write(ROLE_COMPACT, 20100, 0)
                await asyncio.sleep(0.3)
                await self.coordinator.api.async_write_register(
                    ROLE_COMPACT, 4747, FAN_COMMANDS[option]
                )
        except Exception:
            self._commanded_option = previous_option
            self.async_write_ha_state()
            raise

        self.hass.async_create_task(self._async_delayed_refresh())

    async def _async_delayed_refresh(self) -> None:
        """Refresh measured ventilation data without replacing the command."""
        await asyncio.sleep(2)
        await self.coordinator.async_request_refresh()
