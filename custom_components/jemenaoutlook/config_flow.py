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
)
from .const import DOMAIN

DATA_SCHEMA = vol.Schema({
    vol.Required(CONF_USERNAME): TextSelector(
        TextSelectorConfig(type=TextSelectorType.EMAIL)
    ),
    vol.Required(CONF_PASSWORD): TextSelector(
        TextSelectorConfig(
            type=TextSelectorType.PASSWORD
        )
    )
})

_LOGGER = logging.getLogger(__name__)


class ConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Jemena Outlook."""

    VERSION = 2
    CONNECTION_CLASS = config_entries.CONN_CLASS_CLOUD_POLL

    async def async_step_user(self, user_input=None):
        """Handle the initial step."""
        errors = {}
        if user_input is not None:
            try:
                # Save the user input into self.data so it's retained
                self.data = user_input
                return self.async_create_entry(
                        title=DOMAIN,
                        data=self.data,
                    )
            except Exception:
                _LOGGER.exception("Unexpected exception")
                errors["base"] = "unknown"

        # If there is no user input or there were errors, show the form again, including any errors that were found with the input.
        return self.async_show_form(
            step_id="user", data_schema=DATA_SCHEMA, errors=errors
        )
    async def async_step_reconfigure(self, user_input=None):
        """Handle the initial step."""
        errors = {}
        if user_input is not None:
            try:
                # Save the user input into self.data so it's retained
                self.data = user_input
                self.hass.config_entries.async_update_entry(
                    self._get_reconfigure_entry(), data=user_input
                )
                return self.async_abort(reason="reconfigure_successful")
            except Exception:
                _LOGGER.exception("Unexpected exception")
                errors["base"] = "unknown"

        # If there is no user input or there were errors, show the form again, including any errors that were found with the input.
        existing_data = self._get_reconfigure_entry().data
        prefilled_data_schema = vol.Schema(
            {
                vol.Required(
                    CONF_USERNAME,
                    default=existing_data.get(CONF_USERNAME),
                ): TextSelector(
                    TextSelectorConfig(type=TextSelectorType.EMAIL)
                ),
                vol.Required(
                    CONF_PASSWORD,
                    default=existing_data.get(CONF_PASSWORD),
                ): TextSelector(
                    TextSelectorConfig(
                        type=TextSelectorType.PASSWORD
                    )
                )
            }
        )
        return self.async_show_form(
            step_id="reconfigure", data_schema=prefilled_data_schema, errors=errors
        )
