"""Sensori informativi sull'impianto (sola lettura)."""
from __future__ import annotations

from homeassistant.components.sensor import SensorEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import DOMAIN
from .entity import BticinoEntity


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry,
                            async_add_entities: AddEntitiesCallback) -> None:
    coordinator = hass.data[DOMAIN][entry.entry_id]
    async_add_entities([
        # Impianto e Gateway sono info statiche: create ma disattivate di default
        InfoSensor(coordinator, entry.entry_id, "Impianto", "plant_name", "mdi:home-city",
                   enabled_default=False),
        InfoSensor(coordinator, entry.entry_id, "Gateway", "gateway_id", "mdi:router-network",
                   enabled_default=False),
        InfoSensor(coordinator, entry.entry_id, "Dispositivi", "device_count", "mdi:devices"),
    ])


class InfoSensor(BticinoEntity, SensorEntity):
    def __init__(self, coordinator, entry_id, name, key, icon, enabled_default=True):
        super().__init__(coordinator, entry_id)
        self._key = key
        self._attr_name = name
        self._attr_icon = icon
        self._attr_unique_id = f"{entry_id}_{key}"
        self._attr_entity_registry_enabled_default = enabled_default

    @property
    def native_value(self):
        return (self.coordinator.data or {}).get(self._key)

    @property
    def extra_state_attributes(self):
        if self._key == "device_count":
            d = self.coordinator.data or {}
            return {"devices": d.get("devices"), "locks": d.get("locks")}
        if self._key == "plant_name":
            return {"devaddr": (self.coordinator.data or {}).get("devaddr")}
        return None
