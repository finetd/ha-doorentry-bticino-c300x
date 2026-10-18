"""Client HTTP verso l'add-on e coordinatore di aggiornamento."""
from __future__ import annotations

import logging
from datetime import timedelta

import aiohttp
import async_timeout

from homeassistant.core import HomeAssistant
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .const import UPDATE_INTERVAL

_LOGGER = logging.getLogger(__name__)


class AddonClient:
    """Piccolo client per l'API HTTP dell'add-on."""

    def __init__(self, hass: HomeAssistant, host: str, port: int) -> None:
        self._session = async_get_clientsession(hass)
        self._base = f"http://{host}:{port}"

    @property
    def base(self) -> str:
        return self._base

    async def get_state(self) -> dict:
        async with async_timeout.timeout(10):
            async with self._session.get(f"{self._base}/state") as resp:
                resp.raise_for_status()
                return await resp.json(content_type=None)

    async def get_snapshot(self) -> bytes | None:
        try:
            async with async_timeout.timeout(15):
                async with self._session.get(f"{self._base}/snapshot") as resp:
                    if resp.status != 200:
                        return None
                    return await resp.read()
        except Exception:  # noqa: BLE001
            return None

    async def send_cmd(self, action: str) -> bool:
        try:
            async with async_timeout.timeout(15):
                async with self._session.get(f"{self._base}/cmd/{action}") as resp:
                    return resp.status == 200
        except Exception as err:  # noqa: BLE001
            _LOGGER.error("Comando %s fallito: %s", action, err)
            return False


class DoorbellCoordinator(DataUpdateCoordinator):
    """Interroga periodicamente /state dell'add-on."""

    def __init__(self, hass: HomeAssistant, client: AddonClient) -> None:
        super().__init__(
            hass,
            _LOGGER,
            name="doorentry_bticino_c300x",
            update_interval=timedelta(seconds=UPDATE_INTERVAL),
        )
        self.client = client

    async def _async_update_data(self) -> dict:
        try:
            return await self.client.get_state()
        except Exception as err:  # noqa: BLE001
            raise UpdateFailed(f"Add-on non raggiungibile: {err}") from err
