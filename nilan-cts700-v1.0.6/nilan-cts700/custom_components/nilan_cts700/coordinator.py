"""Data update coordinator for Nilan CTS700."""

from __future__ import annotations

import logging
from datetime import timedelta

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .api import NilanError, NilanModbusClient, RegisterKey, encode_int16
from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)


class NilanDataUpdateCoordinator(DataUpdateCoordinator[dict[RegisterKey, int]]):
    """Coordinate efficient polling and writes for all Nilan entities."""

    def __init__(
        self,
        hass: HomeAssistant,
        entry: ConfigEntry,
        api: NilanModbusClient,
        scan_interval: int,
    ) -> None:
        """Initialize the coordinator."""
        super().__init__(
            hass,
            _LOGGER,
            name=DOMAIN,
            update_interval=timedelta(seconds=scan_interval),
            always_update=False,
        )
        self.config_entry = entry
        self.api = api

    async def _async_update_data(self) -> dict[RegisterKey, int]:
        """Fetch all relevant Modbus registers."""
        try:
            return await self.api.async_read_all()
        except NilanError as err:
            raise UpdateFailed(str(err)) from err

    async def async_write(self, role: str, address: int, value: int) -> None:
        """Write a value and publish it without blocking on a complete poll."""
        try:
            await self.api.async_write_register(role, address, value)
        except NilanError as err:
            raise UpdateFailed(str(err)) from err

        updated_data = dict(self.data)
        updated_data[(role, address)] = encode_int16(value)
        self.async_set_updated_data(updated_data)
