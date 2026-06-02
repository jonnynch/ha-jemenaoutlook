from datetime import timedelta
from homeassistant.helpers import device_registry as dr
from homeassistant.helpers import entity_registry as er
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator
from homeassistant.core import HomeAssistant, callback
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import (
    CONF_USERNAME, CONF_PASSWORD)
from aiohttp.client_exceptions import ClientConnectorError
from .PyJemenaOutlook.collector import Collector
from homeassistant.exceptions import ConfigEntryNotReady
from homeassistant.helpers import debounce
from homeassistant.helpers import config_validation as cv
import logging

from .const import (
    CONF_OTP_ENTITY, DOMAIN, COLLECTOR, COORDINATOR, UPDATE_LISTENER, CONF_GMID, CONF_BACKDAY, DEFAULT_BACKDAY
)

from functools import partial
from .helpers import get_otp_token

_LOGGER = logging.getLogger(__name__)

PLATFORMS = ["sensor"]

DEFAULT_SCAN_INTERVAL = timedelta(hours=1)
DEBOUNCE_TIME = 60  # in seconds


CONFIG_SCHEMA = cv.config_entry_only_config_schema(DOMAIN)


"""The Jemena Outlook integration."""
async def async_setup(hass: HomeAssistant, config: dict):
    """Set up the Jemena Outlook component."""
    hass.data.setdefault(DOMAIN, {})
    return True

async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    _LOGGER.info("async_setup_entry")
    """Set up Jemena Outlook from a config entry."""
    otp_entity = entry.data.get(CONF_OTP_ENTITY)
    otp_retriever = partial(
                get_otp_token,
                hass=hass,
                entity_id=otp_entity
            ) if otp_entity else None
    collector = Collector(hass, entry.data[CONF_USERNAME], entry.data[CONF_PASSWORD], entry.data.get(CONF_BACKDAY, DEFAULT_BACKDAY), entry.data[CONF_GMID], otp_retriever)

    try:
        await collector.async_update()
    except ClientConnectorError as ex:
        raise ConfigEntryNotReady from ex

    coordinator = JemenaOutlookDataUpdateCoordinator(hass=hass, collector=collector)
    await coordinator.async_refresh()

    hass_data = hass.data.setdefault(DOMAIN, {})
    hass_data[entry.entry_id] = {
        COLLECTOR: collector,
        COORDINATOR: coordinator,
    }

    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    entry.async_on_unload(entry.add_update_listener(async_update_options))

    return True
async def async_update_options(hass: HomeAssistant, entry: ConfigEntry):
    """Handle config entry updates."""
    _LOGGER.info("async_update_options")
    await hass.config_entries.async_reload(entry.entry_id)


async def async_unload_entry(hass, entry):
    _LOGGER.info("async_unload_entry")
    unload_ok = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
    if unload_ok:
        # Clean up data
        entry_data = hass.data[DOMAIN].pop(entry.entry_id, {})
        coordinator = entry_data.get(COORDINATOR)
        # Cancel any tasks if needed
        if coordinator:
            await coordinator.async_shutdown()
        _LOGGER.info("Successfully unloaded entry %s", entry.entry_id)
    else:
        _LOGGER.error("Failed to unload platforms for entry %s", entry.entry_id)
    return unload_ok

class JemenaOutlookDataUpdateCoordinator(DataUpdateCoordinator):
    """Data update coordinator for Jemena Outlook."""

    def __init__(self, hass: HomeAssistant, collector: Collector) -> None:
        """Initialise the data update coordinator."""
        _LOGGER.info("Initialise coordinator")
        self.collector = collector
        super().__init__(
            hass=hass,
            logger=_LOGGER,
            name=DOMAIN,
            update_method=self.collector.async_update,
            update_interval=DEFAULT_SCAN_INTERVAL,
            request_refresh_debouncer=debounce.Debouncer(
                hass, _LOGGER, cooldown=DEBOUNCE_TIME, immediate=True
            ),
        )

        self.entity_registry_updated_unsub = self.hass.bus.async_listen(
            er.EVENT_ENTITY_REGISTRY_UPDATED, self.entity_registry_updated
        )

    @callback
    def entity_registry_updated(self, event):
        """Handle entity registry update events."""
        _LOGGER.info("entity_registry_updated")
        if event.data["action"] == "remove":
            self.remove_empty_devices()

    def remove_empty_devices(self):
        """Remove devices with no entities."""
        _LOGGER.info("remove_empty_devices")
        entity_registry = er.async_get(self.hass)
        device_registry = dr.async_get(self.hass)
        device_list = dr.async_entries_for_config_entry(
            device_registry, self.config_entry.entry_id
        )

        for device_entry in device_list:
            entities = er.async_entries_for_device(
                entity_registry, device_entry.id, include_disabled_entities=True
            )

            if not entities:
                _LOGGER.debug("Removing orphaned device: %s", device_entry.name)
                device_registry.async_update_device(
                    device_entry.id, remove_config_entry_id=self.config_entry.entry_id
                )