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

CONF_COST = "CONF_COST"
CONF_TODAY = "CONF_TODAY"
CONF_DAILY = "CONF_DAILY"
CONF_WEEKLY = "CONF_WEEKLY"
CONF_MONTHLY = "CONF_MONTHLY"

SCAN_INTERVAL = timedelta(hours=1)

SENSOR_TYPES = {
    'consumptionUsage': ['Consumption Usage', KILOWATT_HOUR, 'mdi:flash', SensorStateClass.TOTAL]
}
SENSOR_TYPES_OLD = {
    'today_user_type': ['Today user type', None, 'mdi:home-account', None],
    'today_usage': ['Today usage', KILOWATT_HOUR, 'mdi:flash', SensorStateClass.TOTAL],
    'today_consumption': ['Today consumption', KILOWATT_HOUR, 'mdi:flash', SensorStateClass.TOTAL],
    'today_consumption_peak': ['Today consumption peak', KILOWATT_HOUR, 'mdi:flash', SensorStateClass.TOTAL],
    'today_consumption_offpeak': ['Today consumption offpeak', KILOWATT_HOUR, 'mdi:flash', SensorStateClass.TOTAL],
    'today_consumption_shoulder': ['Today consumption shoulder', KILOWATT_HOUR, 'mdi:flash', SensorStateClass.TOTAL],
    'today_consumption_controlled_load': ['Today consumption controlled load', KILOWATT_HOUR, 'mdi:flash', SensorStateClass.TOTAL],
    'today_generation': ['Today generation', KILOWATT_HOUR, 'mdi:flash', SensorStateClass.TOTAL],
    'today_cost_total': ['Today cost total', PRICE, 'mdi:currency-usd', None],
    'today_cost_consumption': ['Today cost consumption', PRICE, 'mdi:currency-usd', None],
    'today_cost_generation': ['Today cost generation', PRICE, 'mdi:currency-usd', None],
    'today_cost_difference': ['Today cost difference', PRICE, 'mdi:currency-usd', None],
    'today_percentage_difference': ['Today percentage difference', PERCENT, 'mdi:percent', SensorStateClass.TOTAL],
    'today_difference_message': ['Today difference message', None, 'mdi:clipboard-text', None],
    'today_consumption_difference': ['Today consumption difference', KILOWATT_HOUR, 'mdi:flash', SensorStateClass.TOTAL],
    'today_consumption_change': ['Today consumption change', None, 'mdi:swap-vertical', SensorStateClass.TOTAL],
    'today_suburb_average': ['Today suburb average', KILOWATT_HOUR, 'mdi:flash', SensorStateClass.TOTAL],

    'yesterday_user_type': ['Yesterday user type', None, 'mdi:home-account', None],
    'yesterday_usage': ['Yesterday usage', KILOWATT_HOUR, 'mdi:flash', SensorStateClass.TOTAL],
    'yesterday_consumption': ['Yesterday consumption', KILOWATT_HOUR, 'mdi:flash', SensorStateClass.TOTAL],
    'yesterday_consumption_peak': ['Yesterday consumption peak', KILOWATT_HOUR, 'mdi:flash', SensorStateClass.TOTAL],
    'yesterday_consumption_offpeak': ['Yesterday consumption offpeak', KILOWATT_HOUR, 'mdi:flash', SensorStateClass.TOTAL],
    'yesterday_consumption_shoulder': ['Yesterday consumption shoulder', KILOWATT_HOUR, 'mdi:flash', SensorStateClass.TOTAL],
    'yesterday_consumption_controlled_load': ['Yesterday consumption controlled load', KILOWATT_HOUR, 'mdi:flash', SensorStateClass.TOTAL],
    'yesterday_generation': ['Yesterday generation', KILOWATT_HOUR, 'mdi:flash', SensorStateClass.TOTAL],
    'yesterday_cost_total': ['Yesterday cost total', PRICE, 'mdi:currency-usd', None],
    'yesterday_cost_consumption': ['Yesterday cost consumption', PRICE, 'mdi:currency-usd', None],
    'yesterday_cost_generation': ['Yesterday cost generation', PRICE, 'mdi:currency-usd', None],
    'yesterday_cost_difference': ['Yesterday cost difference', PRICE, 'mdi:currency-usd', None],
    'yesterday_percentage_difference': ['Yesterday percentage difference', PERCENT, 'mdi:percent', SensorStateClass.TOTAL],
    'yesterday_difference_message': ['Yesterday difference message', None, 'mdi:clipboard-text', None],
    'yesterday_consumption_difference': ['Yesterday consumption difference', KILOWATT_HOUR, 'mdi:flash', SensorStateClass.TOTAL],
    'yesterday_consumption_change': ['Yesterday consumption change', None, 'mdi:swap-vertical', SensorStateClass.TOTAL],
    'yesterday_suburb_average': ['Yesterday suburb average', KILOWATT_HOUR, 'mdi:flash', SensorStateClass.TOTAL],

    'previous_day_usage': ['Previous day usage', KILOWATT_HOUR, 'mdi:flash', SensorStateClass.TOTAL],
    'previous_day_consumption': ['Previous day consumption', KILOWATT_HOUR, 'mdi:flash', SensorStateClass.TOTAL],
    'previous_day_generation': ['Previous day generation', KILOWATT_HOUR, 'mdi:flash', SensorStateClass.TOTAL],
    
    'supply_charge': ['Supply charge', PRICE, 'mdi:currency-usd', None],
    'weekday_peak_cost': ['Weekday peak cost', PRICE, 'mdi:currency-usd', None],
    'weekday_offpeak_cost': ['Weekday offpeak cost', PRICE, 'mdi:currency-usd', None],
    'weekday_shoulder_cost': ['Weekday shoulder cost', PRICE, 'mdi:currency-usd', None],
    'controlled_load_cost': ['Controlled load cost', PRICE, 'mdi:currency-usd', None],
    'weekend_offpeak_cost': ['Weekend offpeak cost', PRICE, 'mdi:currency-usd', None],
    'single_rate_cost': ['Single rate cost', PRICE, 'mdi:currency-usd', None],
    'generation_cost': ['Generation cost', PRICE, 'mdi:currency-usd', None],
    
    'this_week_user_type': ['This week user type', None, 'mdi:home-account', None],
    'this_week_usage': ['This week usage', KILOWATT_HOUR, 'mdi:flash', SensorStateClass.TOTAL_INCREASING],
    'this_week_consumption': ['This week consumption', KILOWATT_HOUR, 'mdi:flash', SensorStateClass.TOTAL_INCREASING],
    'this_week_consumption_peak': ['This week consumption peak', KILOWATT_HOUR, 'mdi:flash', SensorStateClass.TOTAL_INCREASING],
    'this_week_consumption_offpeak': ['This week consumption offpeak', KILOWATT_HOUR, 'mdi:flash', SensorStateClass.TOTAL_INCREASING],
    'this_week_consumption_shoulder': ['This week consumption shoulder', KILOWATT_HOUR, 'mdi:flash', SensorStateClass.TOTAL_INCREASING],
    'this_week_consumption_controlled_load': ['This week consumption controlled load', KILOWATT_HOUR, 'mdi:flash', SensorStateClass.TOTAL_INCREASING],
    'this_week_generation': ['This week generation', KILOWATT_HOUR, 'mdi:flash', SensorStateClass.TOTAL_INCREASING],
    'this_week_cost_total': ['This week cost total', PRICE, 'mdi:currency-usd', None],
    'this_week_cost_consumption': ['This week cost consumption', PRICE, 'mdi:currency-usd', None],
    'this_week_cost_generation': ['This week cost generation', PRICE, 'mdi:currency-usd', None],
    'this_week_cost_difference': ['This week cost difference', PRICE, 'mdi:currency-usd', None],
    'this_week_percentage_difference': ['This week percentage difference', PERCENT, 'mdi:percent', SensorStateClass.TOTAL],
    'this_week_difference_message': ['This week difference message', None, 'mdi:clipboard-text', None],
    'this_week_consumption_difference': ['This week consumption difference', KILOWATT_HOUR, 'mdi:flash', SensorStateClass.TOTAL],
    'this_week_consumption_change': ['This week consumption change', None, 'mdi:swap-vertical', SensorStateClass.TOTAL],
    'this_week_suburb_average': ['This week suburb average', KILOWATT_HOUR, 'mdi:flash', SensorStateClass.TOTAL_INCREASING],
    
    'last_week_usage': ['Last week usage', KILOWATT_HOUR, 'mdi:flash', SensorStateClass.TOTAL],
    'last_week_consumption': ['Last week consumption', KILOWATT_HOUR, 'mdi:flash', SensorStateClass.TOTAL],
    'last_week_generation': ['Last week generation', KILOWATT_HOUR, 'mdi:flash', SensorStateClass.TOTAL],
    
    'this_month_user_type': ['This month user type', None, 'mdi:home-account', None],
    'this_month_usage': ['This month usage', KILOWATT_HOUR, 'mdi:flash', SensorStateClass.TOTAL_INCREASING],
    'this_month_consumption': ['This month consumption', KILOWATT_HOUR, 'mdi:flash', SensorStateClass.TOTAL_INCREASING],
    'this_month_consumption_peak': ['This month consumption peak', KILOWATT_HOUR, 'mdi:flash', SensorStateClass.TOTAL_INCREASING],
    'this_month_consumption_offpeak': ['This month consumption offpeak', KILOWATT_HOUR, 'mdi:flash', SensorStateClass.TOTAL_INCREASING],
    'this_month_consumption_shoulder': ['This month consumption shoulder', KILOWATT_HOUR, 'mdi:flash', SensorStateClass.TOTAL_INCREASING],
    'this_month_consumption_controlled_load': ['This month consumption controlled load', KILOWATT_HOUR, 'mdi:flash', SensorStateClass.TOTAL_INCREASING],
    'this_month_generation': ['This month generation', KILOWATT_HOUR, 'mdi:flash', SensorStateClass.TOTAL_INCREASING],
    'this_month_cost_total': ['This month cost total', PRICE, 'mdi:currency-usd', None],
    'this_month_cost_consumption': ['This month cost consumption', PRICE, 'mdi:currency-usd', None],
    'this_month_cost_generation': ['This month cost generation', PRICE, 'mdi:currency-usd', None],
    'this_month_cost_difference': ['This month cost difference', PRICE, 'mdi:currency-usd', None],
    'this_month_percentage_difference': ['This month percentage difference', PERCENT, 'mdi:percent', SensorStateClass.TOTAL],
    'this_month_difference_message': ['This month difference message', None, 'mdi:clipboard-text', None],
    'this_month_consumption_difference': ['This month consumption difference', KILOWATT_HOUR, 'mdi:flash', SensorStateClass.TOTAL],
    'this_month_consumption_change': ['This month consumption change', None, 'mdi:swap-vertical', SensorStateClass.TOTAL],
    'this_month_suburb_average': ['This month suburb average', KILOWATT_HOUR, 'mdi:flash', SensorStateClass.TOTAL_INCREASING],

    'last_month_usage': ['Last month usage', KILOWATT_HOUR, 'mdi:flash', SensorStateClass.TOTAL],
    'last_month_consumption': ['Last month consumption', KILOWATT_HOUR, 'mdi:flash', SensorStateClass.TOTAL],
    'last_month_generation': ['Last month generation', KILOWATT_HOUR, 'mdi:flash', SensorStateClass.TOTAL],
}
