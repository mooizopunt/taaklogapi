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
    DEFAULT_URL,
    DEFAULT_NAAM,
    DEFAULT_SOORT,
    DEFAULT_RESULTAAT,
    DEFAULT_SERVER_NAME,
    DEFAULT_TASK_ID,
    DEFAULT_INTERVAL,
)


class TaaklogApiConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    VERSION = 1

    async def async_step_user(self, user_input=None):
        errors = {}

        if user_input is not None:
            await self.async_set_unique_id(
                f"{user_input[CONF_SERVER_NAME]}_{user_input[CONF_TASK_ID]}"
            )
            self._abort_if_unique_id_configured()

            return self.async_create_entry(
                title=f"Taaklog {user_input[CONF_SERVER_NAME]} / {user_input[CONF_TASK_ID]}",
                data=user_input,
            )

        schema = vol.Schema({
            vol.Required(CONF_URL, default=DEFAULT_URL): str,
            vol.Required(CONF_API_USER): str,
            vol.Required(CONF_API_KEY): str,
            vol.Required(CONF_NAAM, default=DEFAULT_NAAM): str,
            vol.Required(CONF_SOORT, default=DEFAULT_SOORT): str,
            vol.Required(CONF_RESULTAAT, default=DEFAULT_RESULTAAT): str,
            vol.Required(CONF_SERVER_NAME, default=DEFAULT_SERVER_NAME): str,
            vol.Required(CONF_TASK_ID, default=DEFAULT_TASK_ID): int,
            vol.Required(CONF_INTERVAL, default=DEFAULT_INTERVAL): vol.All(
                int, vol.Range(min=1, max=1440)
            ),
        })

        return self.async_show_form(
            step_id="user",
            data_schema=schema,
            errors=errors,
        )

    @staticmethod
    @callback
    def async_get_options_flow(config_entry):
        return TaaklogApiOptionsFlow(config_entry)


class TaaklogApiOptionsFlow(config_entries.OptionsFlow):
    def __init__(self, config_entry):
        self.config_entry = config_entry

    async def async_step_init(self, user_input=None):
        if user_input is not None:
            return self.async_create_entry(title="", data=user_input)

        current = {**self.config_entry.data, **self.config_entry.options}

        schema = vol.Schema({
            vol.Required(CONF_URL, default=current[CONF_URL]): str,
            vol.Required(CONF_API_USER, default=current[CONF_API_USER]): str,
            vol.Required(CONF_API_KEY, default=current[CONF_API_KEY]): str,
            vol.Required(CONF_NAAM, default=current[CONF_NAAM]): str,
            vol.Required(CONF_SOORT, default=current[CONF_SOORT]): str,
            vol.Required(CONF_RESULTAAT, default=current[CONF_RESULTAAT]): str,
            vol.Required(CONF_SERVER_NAME, default=current[CONF_SERVER_NAME]): str,
            vol.Required(CONF_TASK_ID, default=current[CONF_TASK_ID]): int,
            vol.Required(CONF_INTERVAL, default=current.get(CONF_INTERVAL, DEFAULT_INTERVAL)): vol.All(
                int, vol.Range(min=1, max=1440)
            ),
        })

        return self.async_show_form(
            step_id="init",
            data_schema=schema,
        )
