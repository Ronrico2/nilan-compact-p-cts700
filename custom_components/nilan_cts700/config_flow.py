"""Config flow for Nilan CTS700."""

from __future__ import annotations

from typing import Any

import voluptuous as vol
from homeassistant import config_entries
from homeassistant.config_entries import ConfigFlowResult
from homeassistant.const import CONF_HOST, CONF_PORT, CONF_SCAN_INTERVAL
from homeassistant.core import callback

from .api import NilanError, NilanModbusClient
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
    MAX_SCAN_INTERVAL,
    MIN_SCAN_INTERVAL,
    NAME,
)


class NilanConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Nilan CTS700."""

    VERSION = 1

    async def async_step_user(self, user_input: dict[str, Any] | None = None) -> ConfigFlowResult:
        """Handle the initial setup step."""
        errors: dict[str, str] = {}

        if self._async_current_entries():
            return self.async_abort(reason="single_instance_allowed")

        if user_input is not None:
            client = NilanModbusClient(
                user_input[CONF_HOST],
                user_input[CONF_PORT],
                user_input[CONF_COMPACT_SLAVE],
                user_input[CONF_AIR9_SLAVE],
                user_input[CONF_USE_AIR9],
                timeout=DEFAULT_TIMEOUT,
                message_wait=DEFAULT_MESSAGE_WAIT / 1000,
            )
            try:
                await client.async_validate()
            except NilanError:
                errors["base"] = "cannot_connect"
            except Exception:  # noqa: BLE001 - config flow must never crash on I/O
                errors["base"] = "unknown"
            finally:
                await client.async_close()

            if not errors:
                await self.async_set_unique_id("nilan_cts700_compactp_air9")
                self._abort_if_unique_id_configured()
                return self.async_create_entry(
                    title=f"{NAME} ({user_input[CONF_HOST]})",
                    data=user_input,
                    options={
                        CONF_SCAN_INTERVAL: DEFAULT_SCAN_INTERVAL,
                        CONF_MESSAGE_WAIT: DEFAULT_MESSAGE_WAIT,
                    },
                )

        schema = vol.Schema(
            {
                vol.Required(CONF_HOST): str,
                vol.Required(CONF_PORT, default=DEFAULT_PORT): vol.All(
                    vol.Coerce(int), vol.Range(min=1, max=65535)
                ),
                vol.Required(CONF_COMPACT_SLAVE, default=DEFAULT_COMPACT_SLAVE): vol.All(
                    vol.Coerce(int), vol.Range(min=0, max=247)
                ),
                vol.Required(CONF_USE_AIR9, default=True): bool,
                vol.Required(CONF_AIR9_SLAVE, default=DEFAULT_AIR9_SLAVE): vol.All(
                    vol.Coerce(int), vol.Range(min=0, max=247)
                ),
            }
        )
        return self.async_show_form(step_id="user", data_schema=schema, errors=errors)

    @staticmethod
    @callback
    def async_get_options_flow(
        config_entry: config_entries.ConfigEntry,
    ) -> config_entries.OptionsFlow:
        """Create the options flow."""
        return NilanOptionsFlow(config_entry)


class NilanOptionsFlow(config_entries.OptionsFlow):
    """Handle polling and pacing options."""

    def __init__(self, config_entry: config_entries.ConfigEntry) -> None:
        """Initialize options flow."""
        self._config_entry = config_entry

    async def async_step_init(self, user_input: dict[str, Any] | None = None) -> ConfigFlowResult:
        """Manage integration options."""
        if user_input is not None:
            return self.async_create_entry(title="", data=user_input)

        return self.async_show_form(
            step_id="init",
            data_schema=vol.Schema(
                {
                    vol.Required(
                        CONF_SCAN_INTERVAL,
                        default=self._config_entry.options.get(
                            CONF_SCAN_INTERVAL, DEFAULT_SCAN_INTERVAL
                        ),
                    ): vol.All(
                        vol.Coerce(int),
                        vol.Range(min=MIN_SCAN_INTERVAL, max=MAX_SCAN_INTERVAL),
                    ),
                    vol.Required(
                        CONF_MESSAGE_WAIT,
                        default=self._config_entry.options.get(
                            CONF_MESSAGE_WAIT, DEFAULT_MESSAGE_WAIT
                        ),
                    ): vol.All(vol.Coerce(int), vol.Range(min=0, max=1000)),
                }
            ),
        )
