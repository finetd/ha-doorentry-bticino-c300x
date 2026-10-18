"""Interruttore: segreteria (risponditore) del videocitofono.

Nota: lo stato è "optimistic" (il citofono non comunica indietro il suo stato), quindi riflette
l'ultimo comando inviato."""
from __future__ import annotations

from homeassistant.components.switch import SwitchEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import CMD_ANSWERING_OFF, CMD_ANSWERING_ON, DOMAIN
from .entity import BticinoEntity


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry,
                            async_add_entities: AddEntitiesCallback) -> None:
    coordinator = hass.data[DOMAIN][entry.entry_id]
    async_add_entities([AnsweringMachineSwitch(coordinator, entry.entry_id)])


class AnsweringMachineSwitch(BticinoEntity, SwitchEntity):
    _attr_name = "Segreteria"
    _attr_icon = "mdi:voicemail"

    def __init__(self, coordinator, entry_id):
        super().__init__(coordinator, entry_id)
        self._attr_unique_id = f"{entry_id}_answering"
        self._is_on = False

    @property
    def is_on(self) -> bool:
        return self._is_on

    async def async_turn_on(self, **kwargs) -> None:
        if await self.coordinator.client.send_cmd(CMD_ANSWERING_ON):
            self._is_on = True
            self.async_write_ha_state()

    async def async_turn_off(self, **kwargs) -> None:
        if await self.coordinator.client.send_cmd(CMD_ANSWERING_OFF):
            self._is_on = False
            self.async_write_ha_state()
