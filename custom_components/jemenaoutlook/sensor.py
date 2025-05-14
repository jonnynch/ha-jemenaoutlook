"""
Support for JemenaOutlook.

Get data from 'Jemena Energy Outlook - Your Electricity Use' page/s:
https://electricityoutlook.jemena.com.au/electricityView/index

For more details about this platform, please refer to the documentation at
https://github.com/mvandersteen/ha-jemenaoutlook
"""
from . import JemenaOutlookDataUpdateCoordinator

from homeassistant.components.sensor import (
    SensorDeviceClass,
    SensorEntity
)
from homeassistant.core import HomeAssistant, callback
from homeassistant.config_entries import ConfigEntry
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .PyJemenaOutlook.collector import Collector

from .const import (
    COLLECTOR,
    COORDINATOR,
    DOMAIN,
    KILOWATT_HOUR,
    SENSOR_TYPES
)
import logging
_LOGGER = logging.getLogger(__name__)

async def async_setup_entry(
    hass: HomeAssistant,
    config: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up the Jemena Outlook sensor."""
    name = DOMAIN

    """Add sensors for passed config_entry in HA."""
    hass_data = hass.data[DOMAIN][config.entry_id]

    sensors = []
    for key in SENSOR_TYPES.keys():
        sensors.append(JemenaOutlookSensor(hass, hass_data, key, name))

    async_add_entities(sensors)



class JemenaOutlookSensor(CoordinatorEntity[JemenaOutlookDataUpdateCoordinator], SensorEntity):
    """Implementation of a Jemena Outlook sensor."""

    def __init__(self, hass, hass_data, sensor_type, name):
        """Initialize the sensor."""
        super().__init__(hass_data[COORDINATOR])
        self._hass = hass
        self.collector: Collector = hass_data[COLLECTOR]
        self.coordinator: JemenaOutlookDataUpdateCoordinator = hass_data[COORDINATOR]
        self.client_name = name

        self.type = sensor_type
        self._name = SENSOR_TYPES[sensor_type][0]
        self._unit_of_measurement = SENSOR_TYPES[sensor_type][1]
        self._icon = SENSOR_TYPES[sensor_type][2]
        self._state = None
        self._state_class = SENSOR_TYPES[sensor_type][3]
        if self._unit_of_measurement == KILOWATT_HOUR:
            self.device_class = SensorDeviceClass.ENERGY
                
    async def async_added_to_hass(self) -> None:
        """Set up a listener and load data."""
        self.async_on_remove(self.coordinator.async_add_listener(self._update_callback))
        self.async_on_remove(self.coordinator.async_add_listener(self._update_callback))
        self._update_callback()

    @callback
    def _update_callback(self) -> None:
        self.async_write_ha_state()

    @property
    def should_poll(self) -> bool:
        """Entities do not individually poll."""
        return False

    async def async_update(self):
        _LOGGER.info("async_update")
        """Refresh the data on the collector object."""
        await self.collector.async_update()
        

    @property
    def name(self):
        """Return the name of the sensor."""
        return '{} {}'.format(self.client_name, self._name)

    @property
    def unique_id(self):
        """Return the unique of the sensor."""
        return '{}_{}'.format(self.client_name, self.type)

    @property
    def state(self):
        """Return the state of the sensor."""
        if type(self.collector.data[self.type]) == type(''):
            return self.collector.data[self.type]
        else:
            return round(self.collector.data[self.type], 2)

    @property
    def unit_of_measurement(self):
        """Return the unit of measurement of this entity, if any."""
        return self._unit_of_measurement

    @property
    def state_class(self):
        """Return the state_class of this entity, if any."""
        return self._state_class

    @property
    def icon(self):
        """Icon to use in the frontend, if any."""
        return self._icon




