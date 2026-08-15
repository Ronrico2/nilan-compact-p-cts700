"""Climate entities for Nilan CTS700."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from homeassistant.components.climate import ClimateEntity, ClimateEntityFeature
from homeassistant.components.climate.const import HVACMode
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import ATTR_TEMPERATURE, UnitOfTemperature
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import DOMAIN, ROLE_AIR9, ROLE_COMPACT
from .coordinator import NilanDataUpdateCoordinator
from .entity import NilanEntity


@dataclass(frozen=True, kw_only=True)
class NilanClimateDescription:
    """Describe a Nilan climate setpoint."""

    key: str
    name: str
    role: str
    current_address: int
    target_address: int
    minimum: float
    maximum: float
    step: float
    mode_address: int | None = None


CLIMATES: tuple[NilanClimateDescription, ...] = (
    NilanClimateDescription(
        key="nilan_ventilation_temperature",
        name="Nilan ventilationstemperatur",
        role=ROLE_COMPACT,
        current_address=20286,
        target_address=20260,
        mode_address=20120,
        minimum=15,
        maximum=30,
        step=0.5,
    ),
    NilanClimateDescription(
        key="nilan_hot_water",
        name="Nilan varmt vand",
        role=ROLE_COMPACT,
        current_address=20520,
        target_address=20460,
        minimum=10,
        maximum=60,
        step=1,
    ),
    NilanClimateDescription(
        key="nilan_central_heating_air9",
        name="Nilan centralvarme",
        role=ROLE_AIR9,
        current_address=20684,
        target_address=20680,
        minimum=5,
        maximum=50,
        step=0.5,
    ),
)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up Nilan climate entities."""
    coordinator: NilanDataUpdateCoordinator = hass.data[DOMAIN][entry.entry_id]
    async_add_entities(
        NilanClimate(coordinator, description)
        for description in CLIMATES
        if description.role != ROLE_AIR9 or coordinator.api.use_air9
    )


class NilanClimate(NilanEntity, ClimateEntity):
    """Representation of a Nilan temperature setpoint."""

    _attr_temperature_unit = UnitOfTemperature.CELSIUS
    _attr_supported_features = ClimateEntityFeature.TARGET_TEMPERATURE

    def __init__(
        self,
        coordinator: NilanDataUpdateCoordinator,
        description: NilanClimateDescription,
    ) -> None:
        """Initialize the climate entity."""
        super().__init__(
            coordinator,
            name=description.name,
            unique_id=description.key,
            role=description.role,
            address=description.current_address,
        )
        self.description = description
        self._attr_min_temp = description.minimum
        self._attr_max_temp = description.maximum
        self._attr_target_temperature_step = description.step
        self._attr_hvac_modes = (
            [HVACMode.AUTO, HVACMode.COOL, HVACMode.HEAT]
            if description.mode_address is not None
            else [HVACMode.HEAT]
        )

    @property
    def available(self) -> bool:
        """Require both current and target temperature registers."""
        return super().available and self.raw_value(self.description.target_address) is not None

    @property
    def current_temperature(self) -> float | None:
        """Return the measured temperature."""
        value = self.decoded_value(self.description.current_address, signed=True, scale=0.1)
        return float(value) if value is not None else None

    @property
    def target_temperature(self) -> float | None:
        """Return the configured temperature setpoint."""
        value = self.decoded_value(self.description.target_address, signed=True, scale=0.1)
        return float(value) if value is not None else None

    @property
    def hvac_mode(self) -> HVACMode | None:
        """Return the ventilation mode or a fixed heat mode."""
        if self.description.mode_address is None:
            return HVACMode.HEAT
        raw = self.raw_value(self.description.mode_address)
        return {
            0: HVACMode.AUTO,
            1: HVACMode.COOL,
            2: HVACMode.HEAT,
        }.get(raw)

    async def async_set_temperature(self, **kwargs: Any) -> None:
        """Set the target temperature."""
        if (temperature := kwargs.get(ATTR_TEMPERATURE)) is None:
            return
        raw = round(float(temperature) * 10)
        await self.coordinator.async_write(self.role, self.description.target_address, raw)

    async def async_set_hvac_mode(self, hvac_mode: HVACMode) -> None:
        """Set the ventilation mode when supported."""
        if self.description.mode_address is None:
            if hvac_mode != HVACMode.HEAT:
                raise ValueError("Denne temperaturstyring understøtter kun varme")
            return
        value = {
            HVACMode.AUTO: 0,
            HVACMode.COOL: 1,
            HVACMode.HEAT: 2,
        }.get(hvac_mode)
        if value is None:
            raise ValueError(f"Ikke-understøttet HVAC-tilstand: {hvac_mode}")
        await self.coordinator.async_write(self.role, self.description.mode_address, value)
