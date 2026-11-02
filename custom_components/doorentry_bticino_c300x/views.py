"""Endpoint HTTP autenticati di Home Assistant per registrazioni e istantanea.

Il browser non puo' raggiungere l'add-on (il suo nome host e' interno a Home Assistant),
quindi i file vengono serviti da Home Assistant stesso, con il suo login, leggendoli da /share.
FileResponse gestisce le richieste Range: nel player si puo' andare avanti e indietro.
"""
from __future__ import annotations

import os

from aiohttp import web
from homeassistant.components.http import HomeAssistantView

from .const import API_BASE, RECORDINGS_DIR, SNAPSHOT_FILE


class RecordingView(HomeAssistantView):
    url = API_BASE + "/recordings/{name}"
    name = "api:doorentry_bticino_c300x:recording"
    requires_auth = True

    async def get(self, request: web.Request, name: str) -> web.StreamResponse:
        if "/" in name or ".." in name or not name.endswith(".mp4"):
            return web.Response(status=400)
        path = os.path.join(RECORDINGS_DIR, name)
        if not os.path.isfile(path):
            return web.Response(status=404)
        return web.FileResponse(path, headers={"Content-Type": "video/mp4"})


class SnapshotView(HomeAssistantView):
    url = API_BASE + "/snapshot.jpg"
    name = "api:doorentry_bticino_c300x:snapshot"
    requires_auth = True

    async def get(self, request: web.Request) -> web.StreamResponse:
        if not os.path.isfile(SNAPSHOT_FILE):
            return web.Response(status=404)
        return web.FileResponse(SNAPSHOT_FILE, headers={"Content-Type": "image/jpeg"})
