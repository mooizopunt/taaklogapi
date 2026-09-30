from __future__ import annotations

from datetime import timedelta
import logging

import aiohttp
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .const import (
    DOMAIN,
    CONF_URL,
    CONF_API_USER,
    CONF_API_KEY,
    CONF_NAAM,
    CONF_SOORT,
    CONF_RESULTAAT,
    CONF_SERVER_NAME,
    CONF_TASK_ID,
    CONF_INTERVAL,
)

_LOGGER = logging.getLogger(__name__)

PLATFORMS = ["sensor"]


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    data = {**entry.data, **entry.options}

    async def async_post_taaklog():
        url = data[CONF_URL]

        headers = {
            "X-API-User": data[CONF_API_USER],
            "X-API-Key": data[CONF_API_KEY],
            "Content-Type": "application/json",
        }

        body = {
            "Naam": data[CONF_NAAM],
            "Soort": data[CONF_SOORT],
            "Resultaat": data[CONF_RESULTAAT],
            "ServerName": data[CONF_SERVER_NAME],
            "TaskId": int(data[CONF_TASK_ID]),
        }

        timeout = aiohttp.ClientTimeout(total=30)

        try:
            async with aiohttp.ClientSession(timeout=timeout) as session:
                async with session.post(url, headers=headers, json=body) as response:
                    text = await response.text()

                    if response.status < 200 or response.status >= 300:
                        raise UpdateFailed(
                            f"HTTP {response.status}: {text[:500]}"
                        )

                    _LOGGER.info(
                        "Taaklog API uitgevoerd: HTTP %s - %s",
                        response.status,
                        text[:500],
                    )

                    return {
                        "ok": True,
                        "status_code": response.status,
                        "response": text[:1000],
                        "request": body,
                    }

        except aiohttp.ClientError as err:
            raise UpdateFailed(f"Verbindingsfout: {err}") from err

    interval_minutes = int(data.get(CONF_INTERVAL, 5))

    coordinator = DataUpdateCoordinator(
        hass,
        _LOGGER,
        name="Taaklog API",
        update_method=async_post_taaklog,
        update_interval=timedelta(minutes=interval_minutes),
    )

    # Meteen één keer uitvoeren bij het laden.
    await coordinator.async_config_entry_first_refresh()

    hass.data.setdefault(DOMAIN, {})[entry.entry_id] = coordinator

    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    entry.async_on_unload(entry.add_update_listener(async_reload_entry))

    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    unload_ok = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)

    if unload_ok:
        hass.data[DOMAIN].pop(entry.entry_id)

    return unload_ok


async def async_reload_entry(hass: HomeAssistant, entry: ConfigEntry) -> None:
    await hass.config_entries.async_reload(entry.entry_id)
