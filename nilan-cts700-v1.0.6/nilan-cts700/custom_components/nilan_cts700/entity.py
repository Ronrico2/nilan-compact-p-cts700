"""Shared entity helpers for Nilan CTS700."""

from __future__ import annotations

from typing import Any

from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .api import decode_int16
from .const import DOMAIN, ROLE_AIR9
from .coordinator import NilanDataUpdateCoordinator


class NilanEntity(CoordinatorEntity[NilanDataUpdateCoordinator]):
    """Base class for a register-backed Nilan entity."""

    _attr_has_entity_name = False

    def __init__(
        self,
        coordinator: NilanDataUpdateCoordinator,
        *,
        name: str,
        unique_id: str,
        role: str,
        address: int | None = None,
    ) -> None:
        """Initialize the entity."""
        super().__init__(coordinator)
        self._attr_name = name
        self._attr_unique_id = unique_id
        self.role = role
        self.address = address

    @property
    def available(self) -> bool:
        """Report availability for this entity's register."""
        if not super().available:
            return False
        if self.address is None:
            return True
        return (self.role, self.address) in self.coordinator.data

    @property
    def device_info(self) -> DeviceInfo:
        """Return the associated physical device."""
        host = self.coordinator.api.host
        if self.role == ROLE_AIR9:
            return DeviceInfo(
                identifiers={(DOMAIN, "air9")},
                manufacturer="Nilan",
                model="AIR9",
                name="Nilan AIR9",
                configuration_url=f"http://{host}",
            )
        return DeviceInfo(
            identifiers={(DOMAIN, "compact_p")},
            manufacturer="Nilan",
            model="CTS700 Compact P",
            name="Nilan Compact P",
            configuration_url=f"http://{host}",
        )

    def raw_value(self, address: int | None = None) -> int | None:
        """Return a raw unsigned register value."""
        key_address = self.address if address is None else address
        if key_address is None:
            return None
        return self.coordinator.data.get((self.role, key_address))

    def decoded_value(
        self,
        address: int | None = None,
        *,
        signed: bool = False,
        scale: float = 1.0,
    ) -> int | float | None:
        """Decode a register using signedness and scale metadata."""
        raw = self.raw_value(address)
        if raw is None:
            return None
        value: int | float = decode_int16(raw) if signed else raw
        if scale != 1:
            value = round(value * scale, 3)
        return value


def value_or_none(value: Any) -> Any:
    """Keep entity property expressions compact and explicit."""
    return value if value is not None else None
