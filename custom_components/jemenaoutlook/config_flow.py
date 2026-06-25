"""Config flow for Jemena Outlook."""
from __future__ import annotations
import logging
import voluptuous as vol
from homeassistant import config_entries
from homeassistant.core import callback
from homeassistant.const import (
    CONF_USERNAME, CONF_PASSWORD)

from homeassistant.helpers.selector import (
    TextSelector,
    TextSelectorConfig,
    TextSelectorType,
    NumberSelector,
    NumberSelectorConfig,
    NumberSelectorMode,
    EntitySelector,
    EntitySelectorConfig
)
from .const import (CONF_OTP, CONF_OTP_ENTITY, DOMAIN, CONF_GMID, CONF_BACKDAY, DEFAULT_BACKDAY)
from .PyJemenaOutlook.collector import Collector
from .PyJemenaOutlook.jemena_client import JemenaOutlookClient as Client

from functools import partial
from .helpers import get_otp_token

_LOGGER = logging.getLogger(__name__)


class ConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Jemena Outlook."""

    VERSION = 2
    CONNECTION_CLASS = config_entries.CONN_CLASS_CLOUD_POLL

    
    def __init__(self):
        self.client = None
        self.data = None
        self._reauth_entry = None

    
    async def async_step_user(self, user_input = None):
        return await self._async_handle_login(user_input)
    
    async def async_step_reconfigure(self, user_input = None):
        self._reauth_entry = self.hass.config_entries.async_get_entry(self.context["entry_id"])
        return await self._async_handle_login(user_input)

    async def _async_handle_login(self, user_input = None):
        """Handle the initial step."""
        errors = {}
        entry_data = self._reauth_entry.data if self._reauth_entry else {}

        if user_input is not None:
            try:
                # Save the user input into self.data so it's retained
                self.data = user_input
                client = Client(self.data[CONF_USERNAME], self.data[CONF_PASSWORD], entry_data.get(CONF_GMID))
                self.client = client
                response = await client.login()
                if not response.success:
                    _LOGGER.error("Login failed: %s - %s", response.error_code, response.error_message)
                    _LOGGER.error("Details: %s", response.error_details)
                    if response.tfa:
                        await client.send_tfa()
                        return await self.async_step_otp()
                    else:
                        _LOGGER.exception("Unexpected exception")
                        errors["base"] = f"{response.error_code} - {response.error_message}"
                else:
                    if entry_data.get(CONF_OTP_ENTITY):
                        self.data[CONF_OTP_ENTITY] = entry_data.get(CONF_OTP_ENTITY)    
                    self.data[CONF_GMID] = entry_data.get(CONF_GMID)
                    return await self._async_finish_login()
            except Exception:
                _LOGGER.exception("Unexpected exception")
                errors["base"] = "unknown"

        # If there is no user input or there were errors, show the form again, including any errors that were found with the input.
        return self.async_show_form(
            step_id="user", 
            data_schema=vol.Schema({
                vol.Required(CONF_USERNAME, default=entry_data.get(CONF_USERNAME, "")): TextSelector(
                    TextSelectorConfig(type=TextSelectorType.EMAIL)
                ),
                vol.Required(CONF_PASSWORD, default=entry_data.get(CONF_PASSWORD, "")): TextSelector(
                    TextSelectorConfig(type=TextSelectorType.PASSWORD)
                ),
                vol.Optional(CONF_BACKDAY, default=entry_data.get(CONF_BACKDAY, DEFAULT_BACKDAY)): NumberSelector(
                    NumberSelectorConfig(min=1, max=30, mode=NumberSelectorMode.BOX)
                )
            }), 
            errors=errors
        )
    async def async_step_otp(self, user_input=None):
        errors = {}
        entry_data = self._reauth_entry.data if self._reauth_entry else {}
        
        if user_input is not None:
            input_code = user_input.get(CONF_OTP)
            otp_entity = user_input.get(CONF_OTP_ENTITY)
            code = await get_otp_token(self.hass, otp_entity, input_code)
            response = await self.client.submit_tfa(code)

            if response.success:
                self.data[CONF_GMID] = response.gmid
                self.data[CONF_OTP_ENTITY] = otp_entity
                return await self._async_finish_login()
            else:
                _LOGGER.error("Login failed: %s - %s", response.error_code, response.error_message)
                _LOGGER.error("Details: %s", response.error_details)
                errors["base"] = f"{response.error_code} - {response.error_message}"

        return self.async_show_form(
            step_id="otp",
            data_schema=vol.Schema({
                vol.Optional(CONF_OTP): TextSelector(
                    TextSelectorConfig(type=TextSelectorType.TEXT, autocomplete="one-time-code, leave blank if you use otp entity")
                ),
                vol.Optional(CONF_OTP_ENTITY, default=entry_data.get(CONF_OTP_ENTITY)): EntitySelector(
                    EntitySelectorConfig(domain=["sensor"])
                )
            }),
            errors=errors
        )

    
    async def _async_finish_login(self):
        if self._reauth_entry:
            self.hass.config_entries.async_update_entry(self._reauth_entry,data=self.data)
            await self.hass.config_entries.async_reload(self._reauth_entry.entry_id)
            return self.async_abort(reason="reconfigure_successful")
        
        return self.async_create_entry(title=DOMAIN,data=self.data)
