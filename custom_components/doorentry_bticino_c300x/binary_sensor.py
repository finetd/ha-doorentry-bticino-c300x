"""Sensore binario: qualcuno sta suonando."""
from __future__ import annotations

from homeassistant.components.binary_sensor import (
    BinarySensorDeviceClass,
    BinarySensorEntity,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import DOMAIN
from .entity import BticinoEntity


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry,
                            async_add_entities: AddEntitiesCallback) -> None:
    coordinator = hass.data[DOMAIN][entry.entry_id]
    async_add_entities([
        RingingBinarySensor(coordinator, entry.entry_id),
        MissedBinarySensor(coordinator, entry.entry_id),
    ])


class RingingBinarySensor(BticinoEntity, BinarySensorEntity):
    _attr_name = "Sta suonando"
    _attr_device_class = BinarySensorDeviceClass.OCCUPANCY
    _attr_icon = "mdi:doorbell-video"

    def __init__(self, coordinator, entry_id):
        super().__init__(coordinator, entry_id)
        self._attr_unique_id = f"{entry_id}_ringing"

    @property
    def is_on(self) -> bool:
        return bool((self.coordinator.data or {}).get("ringing"))

    @property
    def extra_state_attributes(self):
        d = self.coordinator.data or {}
        return {
            "ring_count": d.get("ring_count"),
            "last_ring": d.get("last_ring"),
        }


class MissedBinarySensor(BticinoEntity, BinarySensorEntity):
    _attr_name = "Chiamata persa"
    _attr_icon = "mdi:phone-missed"

    def __init__(self, coordinator, entry_id):
        super().__init__(coordinator, entry_id)
        self._attr_unique_id = f"{entry_id}_missed"

    @property
    def is_on(self) -> bool:
        return bool((self.coordinator.data or {}).get("missed"))

    @property
    def extra_state_attributes(self):
        d = self.coordinator.data or {}
        return {
            "missed_count": d.get("missed_count"),
            "last_missed": d.get("last_missed"),
        }
