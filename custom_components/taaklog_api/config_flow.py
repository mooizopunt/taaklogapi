"""Config flow for Taaklog API."""

from __future__ import annotations
import voluptuous as vol

from homeassistant import config_entries
from homeassistant.core import callback

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
    DEFAULT_URL,
    DEFAULT_NAAM,
    DEFAULT_SOORT,
    DEFAULT_RESULTAAT,
    DEFAULT_SERVER_NAME,
    DEFAULT_TASK_ID,
    DEFAULT_INTERVAL,
    DEFAULT_CA_URL,
)


def _schema(values=None):
    values = values or {}

    return vol.Schema({
        vol.Required(CONF_URL, default=values.get(CONF_URL, DEFAULT_URL)): str,
        vol.Required(CONF_API_USER, default=values.get(CONF_API_USER, "")): str,
        vol.Required(CONF_API_KEY, default=values.get(CONF_API_KEY, "")): str,
        vol.Required(CONF_NAAM, default=values.get(CONF_NAAM, DEFAULT_NAAM)): str,
        vol.Required(CONF_SOORT, default=values.get(CONF_SOORT, DEFAULT_SOORT)): str,
        vol.Required(
            CONF_RESULTAAT,
            default=values.get(CONF_RESULTAAT, DEFAULT_RESULTAAT),
        ): str,
        vol.Required(
            CONF_SERVER_NAME,
            default=values.get(CONF_SERVER_NAME, DEFAULT_SERVER_NAME),
        ): str,
        vol.Required(
            CONF_TASK_ID,
            default=values.get(CONF_TASK_ID, DEFAULT_TASK_ID),
        ): int,
        vol.Required(
            CONF_INTERVAL,
            default=values.get(CONF_INTERVAL, DEFAULT_INTERVAL),
        ): vol.All(int, vol.Range(min=1, max=1440)),
        vol.Required(
            CONF_CA_URL,
            default=values.get(CONF_CA_URL, DEFAULT_CA_URL),
        ): str,
    })


class TaaklogApiConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    VERSION = 1

    async def async_step_user(self, user_input=None):
        if user_input is not None:
            await self.async_set_unique_id(
                f"{user_input[CONF_SERVER_NAME]}_{user_input[CONF_TASK_ID]}"
            )
            self._abort_if_unique_id_configured()

            return self.async_create_entry(
                title=(
                    f"Taaklog {user_input[CONF_SERVER_NAME]} / "
                    f"{user_input[CONF_TASK_ID]}"
                ),
                data=user_input,
            )

        return self.async_show_form(
            step_id="user",
            data_schema=_schema(),
        )

    @staticmethod
    @callback
    def async_get_options_flow(config_entry):
        return TaaklogApiOptionsFlow()


class TaaklogApiOptionsFlow(config_entries.OptionsFlow):
    async def async_step_init(self, user_input=None):
        if user_input is not None:
            return self.async_create_entry(
                title="",
                data=user_input,
            )

        current = {
            **self.config_entry.data,
            **self.config_entry.options,
        }

        return self.async_show_form(
            step_id="init",
            data_schema=_schema(current),
        )
