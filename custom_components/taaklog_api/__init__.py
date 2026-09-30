"""Taaklog API integration."""

from __future__ import annotations

from datetime import timedelta
import logging
from pathlib import Path
import ssl

import aiohttp

from homeassistant.config_entries import ConfigEntry
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
    CA_SOURCE_FILENAME,
    CA_PEM_FILENAME,
)

_LOGGER = logging.getLogger(__name__)
PLATFORMS = ["sensor"]


async def _async_write_bytes(
    hass: HomeAssistant,
    path: Path,
    content: bytes,
) -> None:
    """Write bytes without blocking the event loop."""

    def _write() -> None:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(content)

    await hass.async_add_executor_job(_write)


async def _async_download_ca_certificate(
    hass: HomeAssistant,
    ca_url: str,
    source_path: Path,
) -> bytes:
    """Download the CA certificate from GitHub."""
    session = async_get_clientsession(hass)

    try:
        async with session.get(
            ca_url,
            timeout=aiohttp.ClientTimeout(total=30),
        ) as response:
            if response.status != 200:
                body = await response.text()
                raise ConfigEntryNotReady(
                    f"CA-certificaat downloaden mislukt: "
                    f"HTTP {response.status}: {body[:300]}"
                )

            certificate = await response.read()

    except (aiohttp.ClientError, TimeoutError) as err:
        raise ConfigEntryNotReady(
            f"CA-certificaat downloaden mislukt: {err}"
        ) from err

    if not certificate:
        raise ConfigEntryNotReady(
            "Gedownload CA-certificaat is leeg"
        )

    await _async_write_bytes(
        hass,
        source_path,
        certificate,
    )

    return certificate


async def _async_convert_certificate_to_pem(
    hass: HomeAssistant,
    certificate: bytes,
    pem_path: Path,
) -> None:
    """Accept PEM or DER and store a normalized PEM certificate."""

    def _convert() -> bytes:
        # Already PEM?
        if b"-----BEGIN CERTIFICATE-----" in certificate:
            try:
                text = certificate.decode("ascii")
                ssl.PEM_cert_to_DER_cert(text)
            except (UnicodeDecodeError, ValueError) as err:
                raise ValueError(
                    f"PEM-certificaat is ongeldig: {err}"
                ) from err

            return certificate

        # Otherwise assume binary DER.
        try:
            pem_text = ssl.DER_cert_to_PEM_cert(certificate)
            # Validate the generated PEM as well.
            ssl.PEM_cert_to_DER_cert(pem_text)
        except (ValueError, ssl.SSLError) as err:
            raise ValueError(
                f"Bestand is geen geldig PEM- of DER-certificaat: {err}"
            ) from err

        return pem_text.encode("ascii")

    try:
        pem_bytes = await hass.async_add_executor_job(_convert)
    except ValueError as err:
        raise ConfigEntryNotReady(str(err)) from err

    await _async_write_bytes(
        hass,
        pem_path,
        pem_bytes,
    )


async def _async_create_ssl_context(
    hass: HomeAssistant,
    pem_path: Path,
) -> ssl.SSLContext:
    """Create a secure SSL context with the additional CA."""

    def _create() -> ssl.SSLContext:
        context = ssl.create_default_context()
        context.load_verify_locations(cafile=str(pem_path))
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
    """Set up Taaklog API."""

    data = {**entry.data, **entry.options}
    session = async_get_clientsession(hass)

    ca_dir = Path(hass.config.config_dir) / CA_DIRECTORY
    source_path = ca_dir / CA_SOURCE_FILENAME
    pem_path = ca_dir / CA_PEM_FILENAME

    ca_url = data.get(CONF_CA_URL, DEFAULT_CA_URL)

    certificate = await _async_download_ca_certificate(
        hass,
        ca_url,
        source_path,
    )

    await _async_convert_certificate_to_pem(
        hass,
        certificate,
        pem_path,
    )

    ssl_context = await _async_create_ssl_context(
        hass,
        pem_path,
    )

    async def async_post_taaklog():
        """Send one Taaklog heartbeat."""

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

                return {
                    "status": "OK",
                    "status_code": response.status,
                    "response": response_text[:1000],
                    "request": body,
                    "ca_source_file": str(source_path),
                    "ca_pem_file": str(pem_path),
                    "ca_url": ca_url,
                }

        except (
            ssl.SSLCertVerificationError,
            aiohttp.ClientConnectorCertificateError,
        ) as err:
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
    """Unload Taaklog API."""
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
    """Reload after option changes."""
    await hass.config_entries.async_reload(entry.entry_id)
