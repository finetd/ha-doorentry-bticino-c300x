"""Telecamere dell'integrazione:
- DoorbellCamera: snapshot istantaneo dal videocitofono.
- LastRecordingCamera: riproduce l'ultima registrazione video (on-demand o chiamata persa)
  usando internamente la stessa logica della platform `ffmpeg` di HA, puntata al symlink
  `last.mp4` che l'add-on tiene sempre allineato all'ultima registrazione in assoluto.
"""
from __future__ import annotations

from homeassistant.components.camera import Camera
from homeassistant.components.ffmpeg.camera import FFmpegCamera, DEFAULT_ARGUMENTS
from homeassistant.components.ffmpeg import CONF_EXTRA_ARGUMENTS, CONF_INPUT
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_NAME
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import DOMAIN
from .entity import BticinoEntity


# Path fisso al symlink dell'ultima registrazione: la directory /share e' montata sia
# dall'add-on sia dal core di HA, quindi il path e' valido per ffmpeg di HA.
LAST_RECORDING_PATH = "/share/doorentry_bticino_c300x/recordings/last.mp4"


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry,
                            async_add_entities: AddEntitiesCallback) -> None:
    coordinator = hass.data[DOMAIN][entry.entry_id]
    async_add_entities([
        DoorbellCamera(coordinator, entry.entry_id),
        LastRecordingCamera(hass, coordinator, entry.entry_id),
    ])


class DoorbellCamera(BticinoEntity, Camera):
    _attr_name = "Videocitofono"

    def __init__(self, coordinator, entry_id):
        BticinoEntity.__init__(self, coordinator, entry_id)
        Camera.__init__(self)
        self._attr_unique_id = f"{entry_id}_camera"

    async def async_camera_image(self, width=None, height=None) -> bytes | None:
        return await self.coordinator.client.get_snapshot()


class LastRecordingCamera(BticinoEntity, FFmpegCamera):
    """Replica di `camera.ffmpeg` dentro l'integrazione: ffmpeg legge il MP4 con `-re`
    e lo serve come stream MJPEG, HA lo riproduce nel player della camera.

    Il path puntato e' il symlink `last.mp4` che l'add-on aggiorna ad ogni registrazione
    (on-demand o chiamata persa), quindi la camera mostra sempre l'ultima in assoluto
    senza che l'utente debba cambiare config.
    """
    _attr_name = "Ultima registrazione video"
    _attr_icon = "mdi:video-box"

    def __init__(self, hass: HomeAssistant, coordinator, entry_id: str) -> None:
        BticinoEntity.__init__(self, coordinator, entry_id)
        FFmpegCamera.__init__(self, hass, {
            CONF_NAME: "Ultima registrazione video",
            CONF_INPUT: f"-re -i {LAST_RECORDING_PATH}",
            CONF_EXTRA_ARGUMENTS: DEFAULT_ARGUMENTS,
        })
        self._attr_unique_id = f"{entry_id}_last_recording_camera"

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
