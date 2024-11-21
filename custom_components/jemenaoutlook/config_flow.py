"""Config flow for Jemena Outlook."""
import logging

import homeassistant.helpers.config_validation as cv
import voluptuous as vol
from homeassistant import config_entries, exceptions
from homeassistant.const import CONF_LATITUDE, CONF_LONGITUDE
from homeassistant.core import HomeAssistant, callback
from homeassistant.const import (
    CONF_USERNAME, CONF_PASSWORD)
from homeassistant.helpers.selector import (
    TextSelector,
    TextSelectorConfig,
    TextSelectorType,
)
from .const import (
    DOMAIN
)
from .PyJemenaOutlook.collector import Collector

_LOGGER = logging.getLogger(__name__)


class ConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Jemena Outlook."""

    VERSION = 2
    CONNECTION_CLASS = config_entries.CONN_CLASS_CLOUD_POLL

    @staticmethod
    @callback
    def async_get_options_flow(
        config_entry: config_entries.ConfigEntry,
    ) -> config_entries.OptionsFlow:
        return JemenaOutlookOptionsFlow(config_entry)

    async def async_step_user(self, user_input=None):
        """Handle the initial step."""
        data_schema = vol.Schema(
            {
                vol.Required(CONF_USERNAME): TextSelector(
                    TextSelectorConfig(type=TextSelectorType.EMAIL)
                ),
                vol.Required(CONF_PASSWORD): TextSelector(
                    TextSelectorConfig(
                        type=TextSelectorType.PASSWORD
                    )
                ),
            }
        )

        errors = {}
        if user_input is not None:
            try:
                # Create the collector object with the given long. and lat.
                self.collector = Collector(
                    user_input[CONF_USERNAME],
                    user_input[CONF_PASSWORD],
                )

                # Save the user input into self.data so it's retained
                self.data = user_input
                
                # Populate observations and daily forecasts data
                await self.collector.async_update()
                return self.async_create_entry(
                        title=DOMAIN,
                        data=self.data,
                    )
            except Exception:
                _LOGGER.exception("Unexpected exception")
                errors["base"] = "unknown"

        # If there is no user input or there were errors, show the form again, including any errors that were found with the input.
        return self.async_show_form(
            step_id="user", data_schema=data_schema, errors=errors
        )


class JemenaOutlookOptionsFlow(config_entries.OptionsFlow):
    """Handle options."""

    def __init__(self, config_entry: config_entries.ConfigEntry) -> None:
        """Initialise the options flow."""
        self.config_entry = config_entry
        self.data = {}

    async def async_step_init(self, user_input=None):
        """Handle the initial step."""
        data_schema = vol.Schema(
            {
                vol.Required(
                    CONF_USERNAME,
                    default=self.config_entry.options.get(
                        CONF_USERNAME,
                        self.config_entry.data.get(
                            CONF_USERNAME
                        ),
                    ),
                ): TextSelector(
                    TextSelectorConfig(type=TextSelectorType.EMAIL)
                ),
                vol.Required(
                    CONF_PASSWORD,
                    default=self.config_entry.options.get(
                        CONF_PASSWORD,
                        self.config_entry.data.get(
                            CONF_PASSWORD
                        ),
                    ),
                ): TextSelector(
                    TextSelectorConfig(
                        type=TextSelectorType.PASSWORD
                    )
                ),
            }
        )

        errors = {}
        if user_input is not None:
            try:
                # Create the collector object with the given long. and lat.
                self.collector = Collector(
                    user_input[CONF_USERNAME],
                    user_input[CONF_PASSWORD],
                )

                # Save the user input into self.data so it's retained
                self.data = user_input
                
                # Populate observations and daily forecasts data
                await self.collector.async_update()

                return self.async_create_entry(
                        title=DOMAIN,
                        data=self.data,
                    )

            except Exception:
                _LOGGER.exception("Unexpected exception")
                errors["base"] = "unknown"

        # If there is no user input or there were errors, show the form again, including any errors that were found with the input.
        return self.async_show_form(
            step_id="init", data_schema=data_schema, errors=errors
        )

   