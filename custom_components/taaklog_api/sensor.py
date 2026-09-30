"""Sensor platform for Taaklog API."""

from __future__ import annotations

from homeassistant.components.sensor import SensorEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import (
    AddEntitiesCallback,
)
from homeassistant.helpers.update_coordinator import (
    CoordinatorEntity,
)

from .const import DOMAIN


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up the Taaklog API status sensor."""
    coordinator = hass.data[DOMAIN][entry.entry_id]

    async_add_entities(
        [
            TaaklogApiStatusSensor(
                coordinator,
                entry,
            )
        ]
    )


class TaaklogApiStatusSensor(
    CoordinatorEntity,
    SensorEntity,
):
    """Taaklog API status sensor."""

    _attr_has_entity_name = True
    _attr_name = "Status"
    _attr_icon = "mdi:server-network"

    def __init__(self, coordinator, entry: ConfigEntry):
        """Initialize the sensor."""
        super().__init__(coordinator)

        self._attr_unique_id = (
            f"{entry.entry_id}_status"
        )

    @property
    def native_value(self):
        """Return status."""
        if self.coordinator.last_update_success:
            return "OK"

        return "Fout"

    @property
    def extra_state_attributes(self):
        """Return diagnostic information."""
        data = self.coordinator.data or {}

        return {
            "http_status": data.get("status_code"),
            "response": data.get("response"),
            "request": data.get("request"),
            "ca_file": data.get("ca_file"),
            "ca_url": data.get("ca_url"),
            "laatste_update_succesvol":
                self.coordinator.last_update_success,
        }
