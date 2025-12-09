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
    CONF_COST, CONF_DAILY, CONF_MONTHLY, CONF_TODAY, CONF_WEEKLY, DOMAIN, COLLECTOR, COORDINATOR, UPDATE_LISTENER
)

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
    """Set up Jemena Outlook from a config entry."""
    collector = Collector(hass, entry.data[CONF_USERNAME], entry.data[CONF_PASSWORD]
                          ,options = {
                            CONF_COST: entry.data.get(CONF_COST,True),
                            CONF_TODAY: entry.data.get(CONF_TODAY,True),
                            CONF_DAILY: entry.data.get(CONF_DAILY,True),
                            CONF_WEEKLY: entry.data.get(CONF_WEEKLY,True),
                            CONF_MONTHLY: entry.data.get(CONF_MONTHLY,True),
                        })

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

    update_listener = entry.add_update_listener(async_update_options)
    hass.data[DOMAIN][entry.entry_id][UPDATE_LISTENER] = update_listener

    return True
async def async_update_options(hass: HomeAssistant, entry: ConfigEntry):
    """Handle config entry updates."""
    await hass.config_entries.async_reload(entry.entry_id)

class JemenaOutlookDataUpdateCoordinator(DataUpdateCoordinator):
    """Data update coordinator for Jemena Outlook."""

    def __init__(self, hass: HomeAssistant, collector: Collector) -> None:
        """Initialise the data update coordinator."""
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
        if event.data["action"] == "remove":
            self.remove_empty_devices()

    def remove_empty_devices(self):
        """Remove devices with no entities."""
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