"""Integrazione Door Entry BTicino C300X: si accoppia all'add-on e crea le entità."""
from __future__ import annotations

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import Platform
from homeassistant.core import HomeAssistant

from .const import CONF_HOST, CONF_PORT, DOMAIN
from .coordinator import AddonClient, DoorbellCoordinator
from .views import RecordingView, SnapshotView

PLATFORMS: list[Platform] = [
    Platform.BINARY_SENSOR,
    Platform.CAMERA,
    Platform.SWITCH,
    Platform.BUTTON,
    Platform.SENSOR,
]


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    client = AddonClient(hass, entry.data[CONF_HOST], entry.data[CONF_PORT])
    coordinator = DoorbellCoordinator(hass, client)
    await coordinator.async_config_entry_first_refresh()

    hass.data.setdefault(DOMAIN, {})[entry.entry_id] = coordinator
    # endpoint HTTP per servire video e istantanea al browser (registrati una sola volta)
    if not hass.data.get(f"{DOMAIN}_views"):
        hass.http.register_view(RecordingView())
        hass.http.register_view(SnapshotView())
        hass.data[f"{DOMAIN}_views"] = True
    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    unload_ok = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
    if unload_ok:
        hass.data[DOMAIN].pop(entry.entry_id, None)
    return unload_ok
