from __future__ import annotations

from datetime import datetime

from homeassistant.components.sensor import SensorEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    coordinator = hass.data[DOMAIN][entry.entry_id]
    async_add_entities([TaaklogApiStatusSensor(coordinator, entry)])


class TaaklogApiStatusSensor(CoordinatorEntity, SensorEntity):
    _attr_has_entity_name = True
    _attr_name = "Status"

    def __init__(self, coordinator, entry: ConfigEntry):
        super().__init__(coordinator)
        self._entry = entry
        self._attr_unique_id = f"{entry.entry_id}_status"

    @property
    def native_value(self):
        if not self.coordinator.last_update_success:
            return "Fout"
        return "OK"

    @property
    def extra_state_attributes(self):
        data = self.coordinator.data or {}

        return {
            "laatste_update": datetime.now().isoformat(timespec="seconds"),
            "http_status": data.get("status_code"),
            "response": data.get("response"),
            "request": data.get("request"),
        }
