"""Config flow: chiede host/porta dell'add-on (pre-compilati) e verifica la connessione."""
from __future__ import annotations

import voluptuous as vol

from homeassistant import config_entries
from homeassistant.core import callback
from homeassistant.helpers.aiohttp_client import async_get_clientsession

from .const import CONF_HOST, CONF_PORT, DEFAULT_HOST, DEFAULT_PORT, DOMAIN


async def _test_conn(hass, host: str, port: int) -> bool:
    session = async_get_clientsession(hass)
    try:
        async with session.get(f"http://{host}:{port}/state", timeout=10) as resp:
            return resp.status == 200
    except Exception:  # noqa: BLE001
        return False


class BticinoConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Flusso di configurazione in un solo passo."""

    VERSION = 1

    @staticmethod
    @callback
    def async_get_options_flow(config_entry):
        return BticinoOptionsFlow(config_entry)

    async def async_step_user(self, user_input=None):
        errors = {}
        if user_input is not None:
            host = user_input[CONF_HOST].strip()
            port = user_input[CONF_PORT]
            ok = await self._test(host, port)
            if ok:
                await self.async_set_unique_id(f"{host}:{port}")
                self._abort_if_unique_id_configured()
                return self.async_create_entry(title="Door Entry BTicino C300X",
                                               data={CONF_HOST: host, CONF_PORT: port})
            errors["base"] = "cannot_connect"

        schema = vol.Schema({
            vol.Required(CONF_HOST, default=DEFAULT_HOST): str,
            vol.Required(CONF_PORT, default=DEFAULT_PORT): int,
        })
        return self.async_show_form(step_id="user", data_schema=schema, errors=errors)

    async def _test(self, host: str, port: int) -> bool:
        return await _test_conn(self.hass, host, port)


class BticinoOptionsFlow(config_entries.OptionsFlow):
    """Permette di modificare host/porta dopo l'installazione (es. mettere l'IP di HA)."""

    def __init__(self, config_entry):
        self.config_entry = config_entry

    async def async_step_init(self, user_input=None):
        errors = {}
        cur = {**self.config_entry.data, **self.config_entry.options}
        if user_input is not None:
            host = user_input[CONF_HOST].strip()
            port = user_input[CONF_PORT]
            if await _test_conn(self.hass, host, port):
                # aggiorna i dati dell'entry e ricarica l'integrazione
                self.hass.config_entries.async_update_entry(
                    self.config_entry, data={CONF_HOST: host, CONF_PORT: port})
                await self.hass.config_entries.async_reload(self.config_entry.entry_id)
                return self.async_create_entry(title="", data={})
            errors["base"] = "cannot_connect"

        schema = vol.Schema({
            vol.Required(CONF_HOST, default=cur.get(CONF_HOST, DEFAULT_HOST)): str,
            vol.Required(CONF_PORT, default=cur.get(CONF_PORT, DEFAULT_PORT)): int,
        })
        return self.async_show_form(step_id="init", data_schema=schema, errors=errors)
