"""Nilan CTS700 Compact P + AIR9 integration."""

from __future__ import annotations

from pathlib import Path

from homeassistant.components.http import StaticPathConfig
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_HOST, CONF_PORT, CONF_SCAN_INTERVAL, Platform
from homeassistant.core import HomeAssistant

from .api import NilanModbusClient
from .const import (
    CONF_AIR9_SLAVE,
    CONF_COMPACT_SLAVE,
    CONF_MESSAGE_WAIT,
    CONF_USE_AIR9,
    DEFAULT_AIR9_SLAVE,
    DEFAULT_COMPACT_SLAVE,
    DEFAULT_MESSAGE_WAIT,
    DEFAULT_PORT,
    DEFAULT_SCAN_INTERVAL,
    DEFAULT_TIMEOUT,
    DOMAIN,
    PLATFORMS,
)
from .coordinator import NilanDataUpdateCoordinator

STATIC_URL = "/nilan_cts700_static"


async def async_setup(hass: HomeAssistant, config: dict) -> bool:
    """Set up static dashboard assets."""
    frontend_dir = Path(__file__).parent / "frontend"
    await hass.http.async_register_static_paths(
        [StaticPathConfig(STATIC_URL, str(frontend_dir), cache_headers=False)]
    )
    return True


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up Nilan from a config entry."""
    api = NilanModbusClient(
        entry.data[CONF_HOST],
        entry.data.get(CONF_PORT, DEFAULT_PORT),
        entry.data.get(CONF_COMPACT_SLAVE, DEFAULT_COMPACT_SLAVE),
        entry.data.get(CONF_AIR9_SLAVE, DEFAULT_AIR9_SLAVE),
        entry.data.get(CONF_USE_AIR9, True),
        timeout=DEFAULT_TIMEOUT,
        message_wait=entry.options.get(CONF_MESSAGE_WAIT, DEFAULT_MESSAGE_WAIT) / 1000,
    )
    coordinator = NilanDataUpdateCoordinator(
        hass,
        entry,
        api,
        entry.options.get(CONF_SCAN_INTERVAL, DEFAULT_SCAN_INTERVAL),
    )
    await coordinator.async_config_entry_first_refresh()

    hass.data.setdefault(DOMAIN, {})[entry.entry_id] = coordinator
    entry.async_on_unload(entry.add_update_listener(_async_reload_entry))
    await hass.config_entries.async_forward_entry_setups(
        entry, [Platform(platform) for platform in PLATFORMS]
    )
    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    unloaded = await hass.config_entries.async_unload_platforms(
        entry, [Platform(platform) for platform in PLATFORMS]
    )
    if unloaded:
        coordinator: NilanDataUpdateCoordinator = hass.data[DOMAIN].pop(entry.entry_id)
        await coordinator.api.async_close()
    return unloaded


async def _async_reload_entry(hass: HomeAssistant, entry: ConfigEntry) -> None:
    """Reload after options change."""
    await hass.config_entries.async_reload(entry.entry_id)
