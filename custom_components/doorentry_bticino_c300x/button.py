"""Pulsanti: luce scale e una "Apri" per ogni serratura rilevata (creazione dinamica)."""
from __future__ import annotations

from homeassistant.components.button import ButtonEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import CMD_LIGHT, DOMAIN
from .entity import BticinoEntity


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry,
                            async_add_entities: AddEntitiesCallback) -> None:
    coordinator = hass.data[DOMAIN][entry.entry_id]

    # luce scale: sempre presente
    async_add_entities([
        LightButton(coordinator, entry.entry_id),
        RecordButton(coordinator, entry.entry_id),
    ])

    known: set[str] = set()

    @callback
    def _sync_locks():
        locks = (coordinator.data or {}).get("locks") or []
        new = []
        single = len(locks) == 1
        for lk in locks:
            pe = str(lk.get("pe", "")).strip()
            if not pe or pe in known:
                continue
            known.add(pe)
            name = "Apri porta" if single else f"Apri {lk.get('name', 'serratura')}"
            new.append(LockButton(coordinator, entry.entry_id, pe, name))
        if new:
            async_add_entities(new)

    _sync_locks()                                   # crea quelli già noti ora
    entry.async_on_unload(coordinator.async_add_listener(_sync_locks))  # e i futuri


class LightButton(BticinoEntity, ButtonEntity):
    _attr_name = "Luce scale"
    _attr_icon = "mdi:stairs"

    def __init__(self, coordinator, entry_id):
        super().__init__(coordinator, entry_id)
        self._attr_unique_id = f"{entry_id}_light"

    async def async_press(self) -> None:
        await self.coordinator.client.send_cmd(CMD_LIGHT)


class RecordButton(BticinoEntity, ButtonEntity):
    _attr_name = "Registra 30 secondi"
    _attr_icon = "mdi:record-rec"

    def __init__(self, coordinator, entry_id):
        super().__init__(coordinator, entry_id)
        self._attr_unique_id = f"{entry_id}_record"

    async def async_press(self) -> None:
        await self.coordinator.client.send_cmd("record?duration=30")


class LockButton(BticinoEntity, ButtonEntity):
    _attr_icon = "mdi:door-open"

    def __init__(self, coordinator, entry_id, pe, name):
        super().__init__(coordinator, entry_id)
        self._pe = pe
        self._attr_name = name
        self._attr_unique_id = f"{entry_id}_lock_{pe}"

    @property
    def available(self) -> bool:
        # non disponibile se questa serratura non è più nei dati (es. entità vecchia residua)
        locks = (self.coordinator.data or {}).get("locks") or []
        return any(str(l.get("pe", "")).strip() == self._pe for l in locks)

    async def async_press(self) -> None:
        await self.coordinator.client.send_cmd(f"lock/{self._pe}")
