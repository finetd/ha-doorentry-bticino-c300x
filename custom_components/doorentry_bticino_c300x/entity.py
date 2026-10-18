"""Entità base con informazioni dispositivo comuni."""
from __future__ import annotations

from homeassistant.helpers.entity import DeviceInfo
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN
from .coordinator import DoorbellCoordinator


class BticinoEntity(CoordinatorEntity[DoorbellCoordinator]):
    _attr_has_entity_name = True

    def __init__(self, coordinator: DoorbellCoordinator, entry_id: str) -> None:
        super().__init__(coordinator)
        self._entry_id = entry_id
        data = coordinator.data or {}
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, entry_id)},
            name="Videocitofono BTicino C300X",
            manufacturer="BTicino / Legrand",
            model="Classe 300X (Door Entry)",
            configuration_url=coordinator.client.base,
        )
