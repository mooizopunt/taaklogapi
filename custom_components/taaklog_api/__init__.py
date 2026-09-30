from __future__ import annotations

from datetime import timedelta
import logging
import aiohttp

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .const import *

_LOGGER = logging.getLogger(__name__)
PLATFORMS = ["sensor"]


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    data = {**entry.data, **entry.options}
    session = async_get_clientsession(hass)

    async def async_post_taaklog():
        headers = {
            "X-API-User": data[CONF_API_USER],
            "X-API-Key": data[CONF_API_KEY],
        }

        body = {
            "Naam": data[CONF_NAAM],
            "Soort": data[CONF_SOORT],
            "Resultaat": data[CONF_RESULTAAT],
            "ServerName": data[CONF_SERVER_NAME],
            "TaskId": int(data[CONF_TASK_ID]),
        }

        try:
            async with session.post(
                data[CONF_URL],
                headers=headers,
                json=body,
                timeout=aiohttp.ClientTimeout(total=30),
            ) as response:
                txt = await response.text()
                if not 200 <= response.status < 300:
                    raise UpdateFailed(f"HTTP {response.status}: {txt[:500]}")
                return {
                    "status_code": response.status,
                    "response": txt[:1000],
                    "request": body,
                }
        except (aiohttp.ClientError, TimeoutError) as err:
            raise UpdateFailed(str(err)) from err

    coordinator = DataUpdateCoordinator(
        hass,
        _LOGGER,
        name="Taaklog API",
        update_method=async_post_taaklog,
        update_interval=timedelta(minutes=int(data.get(CONF_INTERVAL, 5))),
    )

    await coordinator.async_config_entry_first_refresh()
    hass.data.setdefault(DOMAIN, {})[entry.entry_id] = coordinator
    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    entry.async_on_unload(entry.add_update_listener(async_reload_entry))
    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    ok = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
    if ok:
        hass.data[DOMAIN].pop(entry.entry_id, None)
    return ok


async def async_reload_entry(hass: HomeAssistant, entry: ConfigEntry) -> None:
    await hass.config_entries.async_reload(entry.entry_id)
