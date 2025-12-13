from typing import Final
from homeassistant.components.sensor import (
    SensorStateClass,
)
from datetime import timedelta

DOMAIN: Final = "jemenaoutlook"
COORDINATOR: Final = "coordinator"
COLLECTOR: Final = "collector"
UPDATE_LISTENER: Final = "update_listener"

REQUESTS_TIMEOUT = 15

KILOWATT_HOUR = 'kWh'  # type: str
PRICE = 'AUD'  # type: str
DAYS = 'days'  # type: str
PERCENT = '%'  

DEFAULT_NAME = 'JemenaOutlook'

SCAN_INTERVAL = timedelta(hours=1)

SENSOR_TYPES = {
    'consumptionUsage': ['Consumption Usage', KILOWATT_HOUR, 'mdi:flash', SensorStateClass.TOTAL],
    'generation': ['Generation', KILOWATT_HOUR, 'mdi:flash', SensorStateClass.TOTAL]
}

