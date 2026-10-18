"""Telecamera: mostra l'ultima istantanea catturata dal videocitofono."""
from __future__ import annotations

from homeassistant.components.camera import Camera
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import DOMAIN
from .entity import BticinoEntity


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry,
                            async_add_entities: AddEntitiesCallback) -> None:
    coordinator = hass.data[DOMAIN][entry.entry_id]
    async_add_entities([DoorbellCamera(coordinator, entry.entry_id)])


class DoorbellCamera(BticinoEntity, Camera):
    _attr_name = "Videocitofono"

    def __init__(self, coordinator, entry_id):
        BticinoEntity.__init__(self, coordinator, entry_id)
        Camera.__init__(self)
        self._attr_unique_id = f"{entry_id}_camera"

    async def async_camera_image(self, width=None, height=None) -> bytes | None:
        return await self.coordinator.client.get_snapshot()
