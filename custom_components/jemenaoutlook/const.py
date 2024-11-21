from typing import Final
from homeassistant.const import (
    CONF_USERNAME, CONF_PASSWORD,
    CONF_NAME, CONF_MONITORED_VARIABLES)
from homeassistant.components.sensor import (
    PLATFORM_SCHEMA,
    SensorStateClass,
)
import voluptuous as vol
import homeassistant.helpers.config_validation as cv
from datetime import timedelta

DOMAIN: Final = "jemenaoutlook"
COORDINATOR: Final = "coordinator"
COLLECTOR: Final = "collector"
UPDATE_LISTENER: Final = "update_listener"

REQUESTS_TIMEOUT = 15

KILOWATT_HOUR = 'kWh'  # type: str
PRICE = 'AUD'  # type: str
DAYS = 'days'  # type: str

DEFAULT_NAME = 'JemenaOutlook'


SCAN_INTERVAL = timedelta(hours=1)

SENSOR_TYPES = {
    # 'yesterday_user_type': ['Yesterday user type', 'type', 'mdi:home-account'],
    'yesterday_usage': ['Yesterday usage', KILOWATT_HOUR, 'mdi:flash', SensorStateClass.TOTAL],
    'yesterday_consumption': ['Yesterday consumption', KILOWATT_HOUR, 'mdi:flash', SensorStateClass.TOTAL],
    'yesterday_consumption_peak': ['Yesterday consumption peak', KILOWATT_HOUR, 'mdi:flash', SensorStateClass.TOTAL],
    'yesterday_consumption_offpeak': ['Yesterday consumption offpeak', KILOWATT_HOUR, 'mdi:flash', SensorStateClass.TOTAL],
    'yesterday_consumption_shoulder': ['Yesterday consumption shoulder', KILOWATT_HOUR, 'mdi:flash', SensorStateClass.TOTAL],
    'yesterday_consumption_controlled_load': ['Yesterday consumption controlled load', KILOWATT_HOUR, 'mdi:flash', SensorStateClass.TOTAL],
    'yesterday_generation': ['Yesterday generation', KILOWATT_HOUR, 'mdi:flash', SensorStateClass.TOTAL],
    # 'yesterday_cost_total': ['Yesterday cost total', PRICE, 'mdi:currency-usd'],
    # 'yesterday_cost_consumption': ['Yesterday cost consumption', PRICE, 'mdi:currency-usd'],
    # 'yesterday_cost_generation': ['Yesterday cost generation', PRICE, 'mdi:currency-usd'],
    # 'yesterday_cost_difference': ['Yesterday cost difference', PRICE, 'mdi:currency-usd'],
    'yesterday_percentage_difference': ['Yesterday percentage difference', KILOWATT_HOUR, 'mdi:percent', SensorStateClass.TOTAL],
    # 'yesterday_difference_message': ['Yesterday difference message', 'text', 'mdi:clipboard-text'],
    'yesterday_consumption_difference': ['Yesterday consumption difference', KILOWATT_HOUR, 'mdi:flash', SensorStateClass.TOTAL],
    'yesterday_consumption_change': ['Yesterday consumption change', KILOWATT_HOUR, 'mdi:swap-vertical', SensorStateClass.TOTAL],
    'yesterday_suburb_average': ['Yesterday suburb average', KILOWATT_HOUR, 'mdi:flash', SensorStateClass.TOTAL],
    'previous_day_usage': ['Previous day usage', KILOWATT_HOUR, 'mdi:flash', SensorStateClass.TOTAL],
    'previous_day_consumption': ['Previous day consumption', KILOWATT_HOUR, 'mdi:flash', SensorStateClass.TOTAL],
    'previous_day_generation': ['Previous day generation', KILOWATT_HOUR, 'mdi:flash', SensorStateClass.TOTAL],
    # 'supply_charge': ['Supply charge', PRICE, 'mdi:currency-usd'],
    # 'weekday_peak_cost': ['Weekday peak cost', PRICE, 'mdi:currency-usd'],
    # 'weekday_offpeak_cost': ['Weekday offpeak cost', PRICE, 'mdi:currency-usd'],
    # 'weekday_shoulder_cost': ['Weekday shoulder cost', PRICE, 'mdi:currency-usd'],
    # 'controlled_load_cost': ['Controlled load cost', PRICE, 'mdi:currency-usd'],
    # 'weekend_offpeak_cost': ['Weekend offpeak cost', PRICE, 'mdi:currency-usd'],
    # 'single_rate_cost': ['Single rate cost', PRICE, 'mdi:currency-usd'],
    # 'generation_cost': ['Generation cost', PRICE, 'mdi:currency-usd'],
    # 'this_week_user_type': ['This week user type', 'type', 'mdi:home-account'],
    'this_week_usage': ['This week usage', KILOWATT_HOUR, 'mdi:flash', SensorStateClass.TOTAL_INCREASING],
    'this_week_consumption': ['This week consumption', KILOWATT_HOUR, 'mdi:flash', SensorStateClass.TOTAL_INCREASING],
    'this_week_consumption_peak': ['This week consumption peak', KILOWATT_HOUR, 'mdi:flash', SensorStateClass.TOTAL_INCREASING],
    'this_week_consumption_offpeak': ['This week consumption offpeak', KILOWATT_HOUR, 'mdi:flash', SensorStateClass.TOTAL_INCREASING],
    'this_week_consumption_shoulder': ['This week consumption shoulder', KILOWATT_HOUR, 'mdi:flash', SensorStateClass.TOTAL_INCREASING],
    'this_week_consumption_controlled_load': ['This week consumption controlled load', KILOWATT_HOUR, 'mdi:flash', SensorStateClass.TOTAL_INCREASING],
    'this_week_generation': ['This week generation', KILOWATT_HOUR, 'mdi:flash', SensorStateClass.TOTAL_INCREASING],
    # 'this_week_cost_total': ['This week cost total', PRICE, 'mdi:currency-usd'],
    # 'this_week_cost_consumption': ['This week cost consumption', PRICE, 'mdi:currency-usd'],
    # 'this_week_cost_generation': ['This week cost generation', PRICE, 'mdi:currency-usd'],
    # 'this_week_cost_difference': ['This week cost difference', PRICE, 'mdi:currency-usd'],
    'this_week_percentage_difference': ['This week percentage difference', KILOWATT_HOUR, 'mdi:percent', SensorStateClass.TOTAL],
    # 'this_week_difference_message': ['This week difference message', 'text', 'mdi:clipboard-text'],
    'this_week_consumption_difference': ['This week consumption difference', KILOWATT_HOUR, 'mdi:flash', SensorStateClass.TOTAL],
    'this_week_consumption_change': ['This week consumption change', KILOWATT_HOUR, 'mdi:swap-vertical', SensorStateClass.TOTAL],
    'this_week_suburb_average': ['This week suburb average', KILOWATT_HOUR, 'mdi:flash', SensorStateClass.TOTAL_INCREASING],
    'last_week_usage': ['Last week usage', KILOWATT_HOUR, 'mdi:flash', SensorStateClass.TOTAL],
    'last_week_consumption': ['Last week consumption', KILOWATT_HOUR, 'mdi:flash', SensorStateClass.TOTAL],
    'last_week_generation': ['Last week generation', KILOWATT_HOUR, 'mdi:flash', SensorStateClass.TOTAL],
    # 'this_month_user_type': ['This month user type', 'type', 'mdi:home-account'],
    'this_month_usage': ['This month usage', KILOWATT_HOUR, 'mdi:flash', SensorStateClass.TOTAL_INCREASING],
    'this_month_consumption': ['This month consumption', KILOWATT_HOUR, 'mdi:flash', SensorStateClass.TOTAL_INCREASING],
    'this_month_consumption_peak': ['This month consumption peak', KILOWATT_HOUR, 'mdi:flash', SensorStateClass.TOTAL_INCREASING],
    'this_month_consumption_offpeak': ['This month consumption offpeak', KILOWATT_HOUR, 'mdi:flash', SensorStateClass.TOTAL_INCREASING],
    'this_month_consumption_shoulder': ['This month consumption shoulder', KILOWATT_HOUR, 'mdi:flash', SensorStateClass.TOTAL_INCREASING],
    'this_month_consumption_controlled_load': ['This month consumption controlled load', KILOWATT_HOUR, 'mdi:flash', SensorStateClass.TOTAL_INCREASING],
    'this_month_generation': ['This month generation', KILOWATT_HOUR, 'mdi:flash', SensorStateClass.TOTAL_INCREASING],
    # 'this_month_cost_total': ['This month cost total', PRICE, 'mdi:currency-usd'],
    # 'this_month_cost_consumption': ['This month cost consumption', PRICE, 'mdi:currency-usd'],
    # 'this_month_cost_generation': ['This month cost generation', PRICE, 'mdi:currency-usd'],
    # 'this_month_cost_difference': ['This month cost difference', PRICE, 'mdi:currency-usd'],
    'this_month_percentage_difference': ['This month percentage difference', KILOWATT_HOUR, 'mdi:percent', SensorStateClass.TOTAL],
    # 'this_month_difference_message': ['This month difference message', 'text', 'mdi:clipboard-text'],
    'this_month_consumption_difference': ['This month consumption difference', KILOWATT_HOUR, 'mdi:flash', SensorStateClass.TOTAL],
    'this_month_consumption_change': ['This month consumption change', KILOWATT_HOUR, 'mdi:swap-vertical', SensorStateClass.TOTAL],
    'this_month_suburb_average': ['This month suburb average', KILOWATT_HOUR, 'mdi:flash', SensorStateClass.TOTAL_INCREASING],

    'last_month_usage': ['Last month usage', KILOWATT_HOUR, 'mdi:flash', SensorStateClass.TOTAL],
    'last_month_consumption': ['Last month consumption', KILOWATT_HOUR, 'mdi:flash', SensorStateClass.TOTAL],
    'last_month_generation': ['Last month generation', KILOWATT_HOUR, 'mdi:flash', SensorStateClass.TOTAL],
}

PLATFORM_SCHEMA = PLATFORM_SCHEMA.extend({
    vol.Required(CONF_MONITORED_VARIABLES):
        vol.All(cv.ensure_list, [vol.In(SENSOR_TYPES)]),
    vol.Required(CONF_USERNAME): cv.string,
    vol.Required(CONF_PASSWORD): cv.string,
    vol.Optional(CONF_NAME, default=DEFAULT_NAME): cv.string,
})

