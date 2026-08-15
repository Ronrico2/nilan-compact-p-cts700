"""Async Modbus client for Nilan CTS700 Compact P and AIR9."""

from __future__ import annotations

import asyncio
import logging
from collections.abc import Callable
from typing import Any

from pymodbus.client import AsyncModbusTcpClient

from .const import REGISTER_BLOCKS, ROLE_AIR9, ROLE_COMPACT

_LOGGER = logging.getLogger(__name__)

RegisterKey = tuple[str, int]


class NilanError(Exception):
    """Base exception for Nilan communication errors."""


class NilanConnectionError(NilanError):
    """Raised when the Nilan controller cannot be reached."""


class NilanModbusError(NilanError):
    """Raised for an invalid or failed Modbus response."""


def decode_int16(value: int) -> int:
    """Decode an unsigned Modbus register as a signed 16-bit value."""
    return value - 0x10000 if value & 0x8000 else value


def encode_int16(value: int) -> int:
    """Encode a signed value for a single Modbus register."""
    return value & 0xFFFF


class NilanModbusClient:
    """Small serialized async client for a Nilan Modbus TCP gateway."""

    def __init__(
        self,
        host: str,
        port: int,
        compact_slave: int,
        air9_slave: int,
        use_air9: bool,
        *,
        timeout: float = 5,
        message_wait: float = 0.05,
        client_factory: Callable[..., Any] = AsyncModbusTcpClient,
    ) -> None:
        """Initialize the client."""
        self.host = host
        self.port = port
        self.compact_slave = compact_slave
        self.air9_slave = air9_slave
        self.use_air9 = use_air9
        self.message_wait = message_wait
        self._client = client_factory(host, port=port, timeout=timeout, retries=2)
        self._lock = asyncio.Lock()

    def slave_for_role(self, role: str) -> int:
        """Return the configured Modbus device id for a logical device role."""
        if role == ROLE_COMPACT:
            return self.compact_slave
        if role == ROLE_AIR9:
            return self.air9_slave
        raise ValueError(f"Unknown Nilan role: {role}")

    async def async_connect(self) -> None:
        """Connect if needed."""
        if self._client.connected:
            return
        try:
            connected = await self._client.connect()
        except (TimeoutError, OSError) as err:
            raise NilanConnectionError(f"Kan ikke forbinde til {self.host}:{self.port}") from err
        if not connected:
            raise NilanConnectionError(f"Kan ikke forbinde til {self.host}:{self.port}")

    async def async_validate(self) -> None:
        """Validate the connection with a known Compact P status register."""
        async with self._lock:
            await self.async_connect()
            await self._async_read_block(ROLE_COMPACT, 21770, 1)

    async def async_read_all(self) -> dict[RegisterKey, int]:
        """Read all configured register blocks.

        A failed AIR9 block does not hide working Compact P entities. Setup only
        fails when no block at all can be read.
        """
        data: dict[RegisterKey, int] = {}
        errors: list[str] = []

        async with self._lock:
            await self.async_connect()
            roles = [ROLE_COMPACT]
            if self.use_air9:
                roles.append(ROLE_AIR9)

            for role in roles:
                for start, count in REGISTER_BLOCKS[role]:
                    try:
                        registers = await self._async_read_block(role, start, count)
                    except NilanError as err:
                        errors.append(str(err))
                    else:
                        for offset, value in enumerate(registers):
                            data[(role, start + offset)] = value
                    if self.message_wait:
                        await asyncio.sleep(self.message_wait)

        if not data:
            detail = errors[0] if errors else "Intet svar fra anlægget"
            raise NilanConnectionError(detail)
        if errors:
            _LOGGER.debug("Nogle Nilan-registerblokke kunne ikke læses: %s", "; ".join(errors))
        return data

    async def _async_read_block(self, role: str, address: int, count: int) -> list[int]:
        """Read one block while the caller holds the client lock."""
        slave = self.slave_for_role(role)
        try:
            response = await self._client.read_holding_registers(
                address, count=count, device_id=slave
            )
        except (TimeoutError, OSError) as err:
            raise NilanConnectionError(f"Timeout ved slave {slave}, register {address}") from err
        if response.isError() or not hasattr(response, "registers"):
            raise NilanModbusError(
                f"Modbus-fejl ved slave {slave}, register {address}, antal {count}"
            )
        registers = list(response.registers)
        if len(registers) != count:
            raise NilanModbusError(f"Forkert svarlængde ved slave {slave}, register {address}")
        return registers

    async def async_write_register(self, role: str, address: int, value: int) -> None:
        """Write one holding register."""
        slave = self.slave_for_role(role)
        async with self._lock:
            await self.async_connect()
            try:
                response = await self._client.write_register(
                    address, encode_int16(value), device_id=slave
                )
            except (TimeoutError, OSError) as err:
                raise NilanConnectionError(
                    f"Kunne ikke skrive slave {slave}, register {address}"
                ) from err
            if response.isError():
                raise NilanModbusError(
                    f"Modbus afviste skrivning til slave {slave}, register {address}"
                )
            if self.message_wait:
                await asyncio.sleep(self.message_wait)

    async def async_close(self) -> None:
        """Close the TCP connection."""
        self._client.close()
