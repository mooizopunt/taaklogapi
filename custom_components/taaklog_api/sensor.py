"""Sensor platform for Taaklog API."""

from homeassistant.components.sensor import SensorEntity
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN


async def async_setup_entry(hass, entry, async_add_entities):
    coordinator = hass.data[DOMAIN][entry.entry_id]
    async_add_entities([TaaklogApiStatusSensor(coordinator, entry)])


class TaaklogApiStatusSensor(CoordinatorEntity, SensorEntity):
    _attr_has_entity_name = True
    _attr_name = "Status"
    _attr_icon = "mdi:server-network"

    def __init__(self, coordinator, entry):
        super().__init__(coordinator)
        self._attr_unique_id = f"{entry.entry_id}_status"

    @property
    def native_value(self):
        return "OK" if self.coordinator.last_update_success else "Fout"

    @property
    def extra_state_attributes(self):
        data = self.coordinator.data or {}

        return {
            "http_status": data.get("status_code"),
            "response": data.get("response"),
            "request": data.get("request"),
            "ca_source_file": data.get("ca_source_file"),
            "ca_pem_file": data.get("ca_pem_file"),
            "ca_url": data.get("ca_url"),
            "laatste_update_succesvol": self.coordinator.last_update_success,
        }
