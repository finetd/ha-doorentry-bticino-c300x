"""Media source: espone le registrazioni video sotto il menu Media di Home Assistant.

Struttura del browser:
    root (nome dell'integrazione)
      - Door Entry BTicino (nome del dispositivo, uno per config entry)
          - last.mp4
          - call-20261026-093558.mp4
          - call-20261026-100102.mp4
          - ...

Al click su un video, HA risolve l'URL diretto all'add-on (http://IP_HA:PORT/recordings/<nome>)
e il player web lo riproduce. Richiede che il browser dell'utente possa raggiungere l'add-on
sulla porta HTTP configurata (default 8099), cosa vera nelle installazioni domestiche tipiche.
"""
from __future__ import annotations

from datetime import datetime

from homeassistant.components.media_player import MediaClass, MediaType
from homeassistant.components.media_source import (
    BrowseMediaSource,
    MediaSource,
    MediaSourceItem,
    PlayMedia,
    Unresolvable,
)
from homeassistant.core import HomeAssistant

from .const import API_BASE, DOMAIN


async def async_get_media_source(hass: HomeAssistant) -> "DoorbellMediaSource":
    """Entry-point: Home Assistant lo chiama quando scopre il file media_source.py."""
    return DoorbellMediaSource(hass)


class DoorbellMediaSource(MediaSource):
    name = "Videocitofono Door Entry BTicino"

    def __init__(self, hass: HomeAssistant) -> None:
        super().__init__(DOMAIN)
        self.hass = hass

    def _coordinators(self):
        """Ritorna la mappa entry_id -> DoorbellCoordinator."""
        return self.hass.data.get(DOMAIN, {})

    async def async_resolve_media(self, item: MediaSourceItem) -> PlayMedia:
        """L'utente ha cliccato un video: ritorniamo l'URL per il player.

        item.identifier ha forma "<entry_id>/<filename>", es.
        "01HEXAMPLE1234/call-20261026-093558.mp4"
        """
        _, _, filename = item.identifier.partition("/")
        if not filename.endswith(".mp4") or "/" in filename or ".." in filename:
            raise Unresolvable("registrazione non trovata")
        # Percorso relativo servito da Home Assistant (views.py): HA lo firma da solo,
        # cosi' il browser lo apre con il proprio login, anche da remoto.
        return PlayMedia(f"{API_BASE}/recordings/{filename}", "video/mp4")

    async def async_browse_media(self, item: MediaSourceItem) -> BrowseMediaSource:
        """Costruisce l'albero del browser Media di HA."""
        coordinators = self._coordinators()

        # Radice: elenca i config entry (dispositivi)
        if not item.identifier:
            children = []
            for entry_id, coord in coordinators.items():
                children.append(BrowseMediaSource(
                    domain=DOMAIN,
                    identifier=entry_id,
                    media_class=MediaClass.DIRECTORY,
                    media_content_type="",
                    title=(coord.data or {}).get("plant_name") or "Door Entry BTicino",
                    can_play=False,
                    can_expand=True,
                ))
            return BrowseMediaSource(
                domain=DOMAIN,
                identifier="",
                media_class=MediaClass.APP,
                media_content_type="",
                title="Videocitofono Door Entry BTicino",
                can_play=False,
                can_expand=True,
                children=children,
                children_media_class=MediaClass.DIRECTORY,
            )

        # Un livello sotto: identifier = entry_id -> lista video dell'entry
        entry_id, _, filename = item.identifier.partition("/")
        coord = coordinators.get(entry_id)
        if not coord:
            raise Unresolvable("configurazione non trovata")

        if not filename:
            # Lista tutti i video chiedendo /recordings all'add-on
            items = await coord.client.list_recordings()
            children = []
            for rec in items:
                name = rec.get("name") or ""
                mtime = rec.get("mtime") or 0
                try:
                    ts_label = datetime.fromtimestamp(mtime).strftime("%d/%m/%Y %H:%M:%S")
                except Exception:
                    ts_label = name
                size_mb = (rec.get("size") or 0) / (1024 * 1024)
                title = f"{ts_label} ({size_mb:.1f} MB)" if size_mb > 0 else ts_label
                children.append(BrowseMediaSource(
                    domain=DOMAIN,
                    identifier=f"{entry_id}/{name}",
                    media_class=MediaClass.VIDEO,
                    media_content_type=MediaType.VIDEO,
                    title=title,
                    can_play=True,
                    can_expand=False,
                    thumbnail=_signed(self.hass, f"{API_BASE}/snapshot.jpg"),
                ))
            return BrowseMediaSource(
                domain=DOMAIN,
                identifier=entry_id,
                media_class=MediaClass.DIRECTORY,
                media_content_type="",
                title=(coord.data or {}).get("plant_name") or "Door Entry BTicino",
                can_play=False,
                can_expand=True,
                children=children,
                children_media_class=MediaClass.VIDEO,
            )

        # Foglia: un file -> ritorniamo un BrowseMediaSource "playable"
        return BrowseMediaSource(
            domain=DOMAIN,
            identifier=item.identifier,
            media_class=MediaClass.VIDEO,
            media_content_type=MediaType.VIDEO,
            title=filename,
            can_play=True,
            can_expand=False,
        )


def _signed(hass: HomeAssistant, path: str) -> str | None:
    """Firma un percorso per poterlo usare come <img> nel browser (anteprima)."""
    try:
        from datetime import timedelta
        from homeassistant.components.http.auth import async_sign_path
        return async_sign_path(hass, path, timedelta(hours=1))
    except Exception:  # noqa: BLE001
        return None
