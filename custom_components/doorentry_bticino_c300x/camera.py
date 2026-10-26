"""Telecamera: mostra l'ultima istantanea catturata dal videocitofono."""
from __future__ import annotations

from homeassistant.components.camera import Camera, CameraEntityFeature
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import DOMAIN
from .entity import BticinoEntity


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry,
                            async_add_entities: AddEntitiesCallback) -> None:
    coordinator = hass.data[DOMAIN][entry.entry_id]
    async_add_entities([
        DoorbellCamera(coordinator, entry.entry_id),
        LastRecordingCamera(coordinator, entry.entry_id),
    ])


class DoorbellCamera(BticinoEntity, Camera):
    _attr_name = "Videocitofono"

    def __init__(self, coordinator, entry_id):
        BticinoEntity.__init__(self, coordinator, entry_id)
        Camera.__init__(self)
        self._attr_unique_id = f"{entry_id}_camera"

    async def async_camera_image(self, width=None, height=None) -> bytes | None:
        return await self.coordinator.client.get_snapshot()


class LastRecordingCamera(BticinoEntity, Camera):
    """Mostra la thumbnail dell'ultima registrazione video.

    - Nella lista entita' e nelle dashboard appare come immagine (primo frame del MP4),
      aggiornata ogni volta che una registrazione termina.
    - Il feature STREAM espone l'URL del MP4 cosi' il player di HA (ffmpeg/go2rtc) possa
      riprodurlo in play. Il MP4 e' un file statico, non uno stream live, quindi la
      riproduzione finisce quando il video termina.
    """
    _attr_name = "Ultima registrazione video"
    _attr_icon = "mdi:video-box"
    _attr_supported_features = CameraEntityFeature.STREAM

    def __init__(self, coordinator, entry_id):
        BticinoEntity.__init__(self, coordinator, entry_id)
        Camera.__init__(self)
        self._attr_unique_id = f"{entry_id}_last_recording_camera"

    def _recording_name(self) -> str | None:
        rec = (self.coordinator.data or {}).get("last_recording")
        return rec.get("name") if rec else None

    async def async_camera_image(self, width=None, height=None) -> bytes | None:
        name = self._recording_name()
        if not name:
            return None
        return await self.coordinator.client.get_recording_thumbnail(name)

    async def stream_source(self) -> str | None:
        name = self._recording_name()
        if not name:
            return None
        return f"{self.coordinator.client.base}/recordings/{name}"

    @property
    def extra_state_attributes(self):
        rec = (self.coordinator.data or {}).get("last_recording")
        if not rec:
            return None
        return {
            "name": rec.get("name"),
            "size": rec.get("size"),
            "mtime": rec.get("mtime"),
            "video_url": f"{self.coordinator.client.base}/recordings/{rec.get('name')}",
        }
