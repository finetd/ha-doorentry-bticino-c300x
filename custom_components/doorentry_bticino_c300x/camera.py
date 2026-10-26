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
    """Riproduce l'ultima registrazione video del citofono.

    - async_camera_image: thumbnail (primo frame del MP4) per lista entita' e card.
    - stream_source: URL del MP4 convertito da ffmpeg/stream di HA in HLS live. Il video
      non e' uno stream continuo ma un file: quando finisce, lo stream si chiude. Al
      prossimo click (o aggiornamento) parte da capo. Per sfogliare la cronologia completa
      di tutte le registrazioni, usa il menu Media di HA (platform media_source).
    """
    _attr_name = "Ultima registrazione video"
    _attr_icon = "mdi:video-box"
    _attr_supported_features = CameraEntityFeature.STREAM

    def __init__(self, coordinator, entry_id):
        BticinoEntity.__init__(self, coordinator, entry_id)
        Camera.__init__(self)
        self._attr_unique_id = f"{entry_id}_last_recording_camera"

    def _rec_name(self) -> str | None:
        rec = (self.coordinator.data or {}).get("last_recording")
        return rec.get("name") if rec else None

    async def async_camera_image(self, width=None, height=None) -> bytes | None:
        name = self._rec_name()
        if not name:
            return None
        return await self.coordinator.client.get_recording_thumbnail(name)

    async def stream_source(self) -> str | None:
        name = self._rec_name()
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
