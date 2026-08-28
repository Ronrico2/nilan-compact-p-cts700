"""Number entities for writable Nilan settings."""

from __future__ import annotations

from dataclasses import dataclass

from homeassistant.components.number import NumberDeviceClass, NumberEntity, NumberEntityDescription
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import UnitOfTemperature, UnitOfTime
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import DOMAIN, ROLE_COMPACT
from .coordinator import NilanDataUpdateCoordinator
from .entity import NilanEntity


@dataclass(frozen=True, kw_only=True)
class NilanNumberDescription(NumberEntityDescription):
    """Describe a writable number register."""

    role: str
    address: int
    scale: float = 1.0
    signed: bool = False


NUMBERS: tuple[NilanNumberDescription, ...] = (
    NilanNumberDescription(
        key="nilan_outdoor_filter_interval",
        name="Nilan filterinterval udeluft",
        role=ROLE_COMPACT,
        address=20102,
        icon="mdi:air-filter",
        native_min_value=30,
        native_max_value=180,
        native_step=1,
        native_unit_of_measurement=UnitOfTime.DAYS,
    ),
    NilanNumberDescription(
        key="nilan_exhaust_filter_interval",
        name="Nilan filterinterval udsugning",
        role=ROLE_COMPACT,
        address=20106,
        icon="mdi:air-filter",
        native_min_value=30,
        native_max_value=180,
        native_step=1,
        native_unit_of_measurement=UnitOfTime.DAYS,
    ),
    NilanNumberDescription(
        key="nilan_summer_winter_threshold",
        name="Nilan sommer-vinter-grænse",
        role=ROLE_COMPACT,
        address=20261,
        icon="mdi:sun-snowflake-variant",
        native_min_value=5,
        native_max_value=30,
        native_step=0.5,
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        device_class=NumberDeviceClass.TEMPERATURE,
        scale=0.1,
        signed=True,
    ),
    NilanNumberDescription(
        key="nilan_frost_protection_start",
        name="Nilan frostsikring start",
        role=ROLE_COMPACT,
        address=20340,
        icon="mdi:snowflake-thermometer",
        native_min_value=1,
        native_max_value=5,
        native_step=0.1,
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        device_class=NumberDeviceClass.TEMPERATURE,
        scale=0.1,
        signed=True,
    ),
    NilanNumberDescription(
        key="nilan_hot_water_electric_threshold",
        name="Nilan aktiveringstemperatur for eltilskud til varmt vand",
        role=ROLE_COMPACT,
        address=20462,
        icon="mdi:water-boiler",
        native_min_value=30,
        native_max_value=65,
        native_step=1,
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        device_class=NumberDeviceClass.TEMPERATURE,
        scale=0.1,
        signed=True,
    ),
)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up Nilan number entities."""
    coordinator: NilanDataUpdateCoordinator = hass.data[DOMAIN][entry.entry_id]
    async_add_entities(NilanNumber(coordinator, description) for description in NUMBERS)


class NilanNumber(NilanEntity, NumberEntity):
    """Representation of a writable Nilan number."""

    entity_description: NilanNumberDescription

    def __init__(
        self,
        coordinator: NilanDataUpdateCoordinator,
        description: NilanNumberDescription,
    ) -> None:
        """Initialize the number."""
        NilanEntity.__init__(
            self,
            coordinator,
            name=description.name or description.key,
            unique_id=description.key,
            role=description.role,
            address=description.address,
        )
        self.entity_description = description

    @property
    def native_value(self) -> int | float | None:
        """Return the current number value."""
        return self.decoded_value(
            signed=self.entity_description.signed,
            scale=self.entity_description.scale,
        )

    async def async_set_native_value(self, value: float) -> None:
        """Write the number setting."""
        raw = round(value / self.entity_description.scale)
        await self.coordinator.async_write(self.role, self.entity_description.address, raw)
