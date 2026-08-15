"""Unit tests for the standalone Modbus client."""

from __future__ import annotations

from dataclasses import dataclass

import pytest

from custom_components.nilan_cts700.api import (
    NilanConnectionError,
    NilanModbusClient,
    decode_int16,
    encode_int16,
)
from custom_components.nilan_cts700.const import ROLE_AIR9, ROLE_COMPACT


@dataclass
class FakeResponse:
    registers: list[int]
    error: bool = False

    def isError(self) -> bool:  # noqa: N802 - mirrors pymodbus
        return self.error


class FakeClient:
    """Minimal pymodbus-compatible fake."""

    def __init__(self, *args, **kwargs) -> None:
        self.connected = False
        self.reads: list[tuple[int, int, int]] = []
        self.writes: list[tuple[int, int, int]] = []
        self.fail_addresses: set[int] = set()
        self.closed = False

    async def connect(self) -> bool:
        self.connected = True
        return True

    async def read_holding_registers(
        self, address: int, *, count: int, device_id: int
    ) -> FakeResponse:
        self.reads.append((address, count, device_id))
        if address in self.fail_addresses:
            return FakeResponse([], error=True)
        return FakeResponse([address + offset & 0xFFFF for offset in range(count)])

    async def write_register(self, address: int, value: int, *, device_id: int) -> FakeResponse:
        self.writes.append((address, value, device_id))
        return FakeResponse([])

    def close(self) -> None:
        self.closed = True


def make_client(*, use_air9: bool = True) -> NilanModbusClient:
    return NilanModbusClient(
        "192.0.2.10",
        502,
        1,
        4,
        use_air9,
        message_wait=0,
        client_factory=FakeClient,
    )


def test_int16_codec() -> None:
    assert decode_int16(0) == 0
    assert decode_int16(32767) == 32767
    assert decode_int16(65535) == -1
    assert encode_int16(-1) == 65535
    assert encode_int16(250) == 250


@pytest.mark.asyncio
async def test_reads_all_blocks_for_both_devices() -> None:
    client = make_client()
    data = await client.async_read_all()

    assert data[(ROLE_COMPACT, 20282)] == 20282
    assert data[(ROLE_COMPACT, 22490)] == 22490
    assert data[(ROLE_AIR9, 20684)] == 20684
    assert data[(ROLE_AIR9, 21913)] == 21913
    assert all(count <= 125 for _, count, _ in client._client.reads)
    assert {device_id for _, _, device_id in client._client.reads} == {1, 4}


@pytest.mark.asyncio
async def test_air9_can_be_disabled() -> None:
    client = make_client(use_air9=False)
    data = await client.async_read_all()

    assert all(role == ROLE_COMPACT for role, _ in data)
    assert {device_id for _, _, device_id in client._client.reads} == {1}


@pytest.mark.asyncio
async def test_partial_block_failure_keeps_other_data() -> None:
    client = make_client()
    client._client.fail_addresses.add(21900)

    data = await client.async_read_all()

    assert (ROLE_AIR9, 21900) not in data
    assert data[(ROLE_AIR9, 20684)] == 20684
    assert data[(ROLE_COMPACT, 21770)] == 21770


@pytest.mark.asyncio
async def test_all_blocks_failed_raises_connection_error() -> None:
    client = make_client()
    client._client.fail_addresses.update(
        {20100, 20260, 20340, 20460, 21770, 22490, 20602, 20680, 21900}
    )

    with pytest.raises(NilanConnectionError):
        await client.async_read_all()


@pytest.mark.asyncio
async def test_write_uses_role_device_id_and_encodes_signed_value() -> None:
    client = make_client()

    await client.async_write_register(ROLE_AIR9, 20680, -10)

    assert client._client.writes == [(20680, 65526, 4)]
