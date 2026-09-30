"""Taaklog API integration."""

from __future__ import annotations

from datetime import timedelta
import logging
from pathlib import Path
import ssl

import aiohttp

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_VERIFY_SSL
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import ConfigEntryNotReady
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from homeassistant.helpers.update_coordinator import (
    DataUpdateCoordinator,
    UpdateFailed,
)

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
    CONF_CA_URL,
    DEFAULT_CA_URL,
    CA_DIRECTORY,
    CA_FILENAME,
)

_LOGGER = logging.getLogger(__name__)

PLATFORMS = ["sensor"]


async def _async_write_file(
    hass: HomeAssistant,
    path: Path,
    content: bytes,
) -> None:
    """Write a file outside the event loop."""

    def _write() -> None:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(content)

    await hass.async_add_executor_job(_write)


async def _async_download_ca_certificate(
    hass: HomeAssistant,
    ca_url: str,
    ca_path: Path,
) -> None:
    """Download the intermediate CA certificate from GitHub."""
    session = async_get_clientsession(hass)

    _LOGGER.info("Downloading Taaklog CA certificate from %s", ca_url)

    try:
        async with session.get(
            ca_url,
            timeout=aiohttp.ClientTimeout(total=30),
        ) as response:
            if response.status != 200:
                text = await response.text()
                raise ConfigEntryNotReady(
                    f"CA-certificaat downloaden mislukt: "
                    f"HTTP {response.status}: {text[:300]}"
                )

            certificate = await response.read()

    except (aiohttp.ClientError, TimeoutError) as err:
        raise ConfigEntryNotReady(
            f"CA-certificaat downloaden mislukt: {err}"
        ) from err

    if b"BEGIN CERTIFICATE" not in certificate:
        raise ConfigEntryNotReady(
            "Gedownload CA-bestand bevat geen PEM-certificaat"
        )

    await _async_write_file(hass, ca_path, certificate)

    _LOGGER.info("Taaklog CA certificate saved to %s", ca_path)


async def _async_create_ssl_context(
    hass: HomeAssistant,
    ca_path: Path,
) -> ssl.SSLContext:
    """Create SSL context with the additional intermediate certificate."""

    def _create() -> ssl.SSLContext:
        context = ssl.create_default_context()
        context.load_verify_locations(cafile=str(ca_path))
        return context

    try:
        return await hass.async_add_executor_job(_create)
    except (OSError, ssl.SSLError) as err:
        raise ConfigEntryNotReady(
            f"CA-certificaat kan niet worden geladen: {err}"
        ) from err


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
) -> bool:
    """Set up Taaklog API from a config entry."""

    data = {**entry.data, **entry.options}
    session = async_get_clientsession(hass)

    # Persistent path below /config.
    ca_path = (
        Path(hass.config.config_dir)
        / CA_DIRECTORY
        / CA_FILENAME
    )

    ca_url = data.get(CONF_CA_URL, DEFAULT_CA_URL)

    # Deliberately refresh the CA file whenever the integration starts.
    # This keeps the local copy synchronized with the GitHub repository.
    await _async_download_ca_certificate(
        hass,
        ca_url,
        ca_path,
    )

    ssl_context = await _async_create_ssl_context(
        hass,
        ca_path,
    )

    async def async_post_taaklog():
        """Post one Taaklog heartbeat."""

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
                ssl=ssl_context,
                timeout=aiohttp.ClientTimeout(total=30),
            ) as response:

                response_text = await response.text()

                if not 200 <= response.status < 300:
                    raise UpdateFailed(
                        f"HTTP {response.status}: "
                        f"{response_text[:500]}"
                    )

                _LOGGER.info(
                    "Taaklog API OK: HTTP %s - %s",
                    response.status,
                    response_text[:300],
                )

                return {
                    "status": "OK",
                    "status_code": response.status,
                    "response": response_text[:1000],
                    "request": body,
                    "ca_file": str(ca_path),
                    "ca_url": ca_url,
                }

        except ssl.SSLCertVerificationError as err:
            raise UpdateFailed(
                f"SSL-certificaatcontrole mislukt: {err}"
            ) from err

        except aiohttp.ClientConnectorCertificateError as err:
            raise UpdateFailed(
                f"SSL-certificaatcontrole mislukt: {err}"
            ) from err

        except (aiohttp.ClientError, TimeoutError) as err:
            raise UpdateFailed(
                f"Verbindingsfout: {err}"
            ) from err

    coordinator = DataUpdateCoordinator(
        hass,
        _LOGGER,
        name="Taaklog API",
        update_method=async_post_taaklog,
        update_interval=timedelta(
            minutes=int(data.get(CONF_INTERVAL, 5))
        ),
    )

    # Execute immediately once. Afterwards DataUpdateCoordinator
    # automatically repeats it at the configured interval.
    await coordinator.async_config_entry_first_refresh()

    hass.data.setdefault(DOMAIN, {})[entry.entry_id] = coordinator

    await hass.config_entries.async_forward_entry_setups(
        entry,
        PLATFORMS,
    )

    entry.async_on_unload(
        entry.add_update_listener(async_reload_entry)
    )

    return True


async def async_unload_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
) -> bool:
    """Unload a Taaklog API config entry."""

    unload_ok = await hass.config_entries.async_unload_platforms(
        entry,
        PLATFORMS,
    )

    if unload_ok:
        hass.data[DOMAIN].pop(entry.entry_id, None)

    return unload_ok


async def async_reload_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
) -> None:
    """Reload the integration after option changes."""
    await hass.config_entries.async_reload(entry.entry_id)
