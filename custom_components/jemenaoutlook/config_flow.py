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
    NumberSelectorMode
)
from .const import (DOMAIN, CONF_GMID, CONF_BACKDAY, DEFAULT_BACKDAY)
from .PyJemenaOutlook.collector import Collector
from .PyJemenaOutlook.jemena_client import JemenaOutlookClient as Client

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
        if user_input is not None:
            code = user_input["otp"]
            response = await self.client.submit_tfa(code)

            if response.success:
                self.data[CONF_GMID] = response.gmid
                _LOGGER.info("gmid: ", self.client.gmid)
                return await self._async_finish_login()
            else:
                _LOGGER.error("Login failed: %s - %s", response.error_code, response.error_message)
                _LOGGER.error("Details: %s", response.error_details)
                errors["base"] = f"{response.error_code} - {response.error_message}"

        return self.async_show_form(
            step_id="otp",
            data_schema=vol.Schema({
                vol.Required("otp"): str,
            }),
            errors=errors
        )

    
    async def _async_finish_login(self):
        if self._reauth_entry:
            self.hass.config_entries.async_update_entry(self._reauth_entry,data=self.data)
            return self.async_abort(reason="reconfigure_successful")

        return self.async_create_entry(title=DOMAIN,data=self.data)
