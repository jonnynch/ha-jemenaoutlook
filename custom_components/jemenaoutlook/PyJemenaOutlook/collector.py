"""BOM data 'collector' that downloads the observation data."""
import logging
from bs4 import BeautifulSoup
import json
import re
import aiohttp
from homeassistant.util import Throttle

from .const import (
    HOST, HOME_URL, PERIOD_URL, REQUESTS_TIMEOUT, MIN_TIME_BETWEEN_UPDATES
)

_LOGGER = logging.getLogger(__name__)

class Collector:
    """Collector for PyBoM."""

    def __init__(self, username, password):
        """Init collector."""
        self.client = JemenaOutlookClient(
            username, password, REQUESTS_TIMEOUT)
        self.data = {}

    async def _fetch_data(self):
        """Fetch latest data from Jemena Outlook."""
        try:
            await self.client.fetch_data()
        except JemenaOutlookError as exp:
            _LOGGER.error("Error on receive last Jemena Outlook data: %s", exp)
            return

    async def get_data(self):
        """Return the contract list."""
        # Fetch data
        await self._fetch_data()
        self.data = self.client.get_data()
        return self.data

    @Throttle(MIN_TIME_BETWEEN_UPDATES)
    async def async_update(self):
        """Return the latest collected data from Jemena Outlook."""
        await self._fetch_data()
        self.data = self.client.get_data()


class JemenaOutlookError(Exception):
    pass

class JemenaOutlookClient(object):

    def __init__(self, username, password, timeout=REQUESTS_TIMEOUT):
        """Initialize the client object."""
        self.username = username
        self.password = password
        self._data = {}
        self._timeout = timeout
        self._session = None


    async def _get_login_page(self, session):
        """Go to the login page."""
        async with session.get(HOME_URL, timeout=REQUESTS_TIMEOUT) as raw_res:
            # Get login url
            soup = BeautifulSoup(await raw_res.text(), 'html.parser')

            form_node = soup.find('form', {'id': 'loginForm'})
            if form_node is None:
                raise JemenaOutlookError("No login form found")

            login_url = form_node.attrs.get('action')
            if login_url is None:
                raise JemenaOutlookError("Cannot find login url")

            return login_url


    async def _post_login_page(self, session, login_url):
        """Login to Jemena Electricity Outlook website."""
        form_data = {"login_email": self.username,
                "login_password": self.password,
                "submit": "Sign In"}
        async with session.post('{}/login_security_check'.format(HOST),
                                    data = form_data,
                                    timeout = REQUESTS_TIMEOUT) as raw_res:
            status_code = raw_res.status 
            if status_code != 200:
                raise JemenaOutlookError("Login error: Bad HTTP status code. {}".format(status_code))
            return True

    
    async def _get_tariffs(self, session):
        """Get tariff data. This data must be setup by the user first and is not automatically available."""
        url = '{}/electricityView/index'.format(HOST)
        async with session.get(url, timeout=REQUESTS_TIMEOUT) as raw_res:
            # Get login url
            soup = BeautifulSoup(await raw_res.text(), 'html.parser')
            tariff_script = soup.find('script', text=re.compile('var tariff = '))

            if tariff_script is not None:
                
                json_text = re.search(r'^\s*var tariff =\s*({.*?})\s*;\s*$', tariff_script.string, flags=re.DOTALL | re.MULTILINE).group(1)
                data = json.loads(json_text)
            
                tariff_data = {
                    "supply_charge": self._strip_currency(data["supplyCharge"]),
                    "weekday_peak_cost": self._strip_currency(data["weekdayPeakCost"]),
                    "weekday_offpeak_cost": self._strip_currency(data["weekdayOffpeakCost"]),
                    "weekday_shoulder_cost": self._strip_currency(data["weekdayShoulderCost"]),
                    "controlled_load_cost": self._strip_currency(data["controlledLoadCost"]),
                    "weekend_offpeak_cost": self._strip_currency(data["weekendOffpeakCost"]),            
                    "single_rate_cost": self._strip_currency(data["singleRateCost"]),
                    "generation_cost": self._strip_currency(data["generationCost"]),
                    }

            return tariff_data
    
    
    async def _get_daily_data(self, session, days_ago):
        """Get daily data."""
        url = '{}/{}/{}'.format(PERIOD_URL, 'day', days_ago)
        async with session.get(url, timeout = REQUESTS_TIMEOUT) as raw_res:
            try:
                json_output = await raw_res.json()
            except (OSError, json.decoder.JSONDecodeError):
                raise JemenaOutlookError("Could not get daily data: {}".format(raw_res))

            if not json_output.get('selectedPeriod'):
                raise JemenaOutlookError("Could not get daily data for selectedPeriod")

            _LOGGER.debug("Jemena outlook daily data: %s", json_output)

            daily_data = self._extract_period_data(json_output , 'yesterday', 'previous_day')

            return daily_data      



    async def _get_weekly_data(self, session, weeks_ago):
        """Get weekly data."""
        #PERIOD_URL
        url = '{}/{}/{}'.format(PERIOD_URL, 'week', weeks_ago)
        async with session.get(url, timeout = REQUESTS_TIMEOUT) as raw_res:
            try:
                json_output = await raw_res.json()

            except (OSError, json.decoder.JSONDecodeError):
                raise JemenaOutlookError("Could not get weekly data: {}".format(raw_res))

            if not json_output.get('selectedPeriod'):
                raise JemenaOutlookError("Could not get weekly data for selectedPeriod")

            _LOGGER.debug("Jemena outlook weekly data: %s", json_output)
            
            weekly_data = self._extract_period_data(json_output, 'this_week', 'last_week')

            return weekly_data


    async def _get_monthly_data(self, session, months_ago):
        """Get Monthly data."""
        #PERIOD_URL
        url = '{}/{}/{}'.format(PERIOD_URL, 'month', months_ago)
        async with session.get(url, timeout = REQUESTS_TIMEOUT) as raw_res:
        
            try:
                json_output = await raw_res.json()

            except (OSError, json.decoder.JSONDecodeError):
                raise JemenaOutlookError("Could not get monthly data: {}".format(raw_res))

            if not json_output.get('selectedPeriod'):
                raise JemenaOutlookError("Could not get monthly data for selectedPeriod")

            _LOGGER.debug("Jemena outlook monthly data: %s", json_output)
            
            monthly_data = self._extract_period_data(json_output, 'this_month', 'last_month')

            return monthly_data


    def _extract_period_data(self, json_data, current, previous):

        costDifference = json_data.get('costDifference')
        costDifferenceMessage = json_data.get('costDifferenceMessage')
        kwhPercentageDifference = json_data.get('kwhPercentageDifference')

        consumptionDifference = json_data.get('consumptionDifferenceMessage')
        
        selectedPeriod = json_data.get('selectedPeriod')        	
        
        netConsumption = selectedPeriod['netConsumption']
        averageNetConsumptionPerSubPeriod = selectedPeriod['averageNetConsumptionPerSubPeriod']
        peakConsumption = self._sum_period_array(selectedPeriod['consumptionData']['peak'], 3)
        offPeakConsumption = self._sum_period_array(selectedPeriod['consumptionData']['offpeak'], 3)
        shoulderConsumption = self._sum_period_array(selectedPeriod['consumptionData']['shoulder'], 3)
        controlledLoadConsumption = self._sum_period_array(selectedPeriod['consumptionData']['controlledLoad'], 3)
        generation = self._sum_period_array(selectedPeriod['consumptionData']['generation'], 3)
        suburbAverage = self._sum_period_array(selectedPeriod['consumptionData']['suburbAverage'], 3)

        costDataPeak = self._sum_period_array(selectedPeriod['costData']['peak'], 2)
        costDataOffPeak = self._sum_period_array(selectedPeriod['costData']['offpeak'], 2)
        costDataShoulder = self._sum_period_array(selectedPeriod['costData']['shoulder'], 2)
        costDataControlledLoad = self._sum_period_array(selectedPeriod['costData']['controlledLoad'], 2)
        costDataGeneration = self._sum_period_array(selectedPeriod['costData']['generation'], 2)

        previousPeriod = json_data.get('comparisonPeriod')

        previousPeriodNetConsumption = previousPeriod['netConsumption']
        previousPeriodPeakConsumption = self._sum_period_array(previousPeriod['consumptionData']['peak'], 3)
        previousPeriodOffPeakConsumption = self._sum_period_array(previousPeriod['consumptionData']['offpeak'], 3)
        previousPeriodShoulderConsumption = self._sum_period_array(previousPeriod['consumptionData']['shoulder'], 3)
        previousPeriodControlledLoadConsumption = self._sum_period_array(previousPeriod['consumptionData']['controlledLoad'], 3)
        previousPeriodGeneration = self._sum_period_array(previousPeriod['consumptionData']['generation'], 3)
        previousPeriodSuburbAverage = self._sum_period_array(previousPeriod['consumptionData']['suburbAverage'], 3)

        period_data = {
            current + "_user_type": "consumer" if netConsumption > 0 else "generator",
            current + "_usage": netConsumption,
            current + "_average_net_usage_per_sub_period": averageNetConsumptionPerSubPeriod,
            current + "_consumption": round(peakConsumption + offPeakConsumption + shoulderConsumption + controlledLoadConsumption, 3),
            current + "_consumption_peak": peakConsumption,
            current + "_consumption_offpeak": offPeakConsumption,
            current + "_consumption_shoulder": shoulderConsumption,
            current + "_consumption_controlled_load": controlledLoadConsumption,
            current + "_generation": generation,
            current + "_cost_total": round(costDataPeak + costDataOffPeak + costDataShoulder + costDataControlledLoad + costDataGeneration, 2),
            current + "_cost_consumption": round(costDataPeak + costDataOffPeak + costDataShoulder + costDataControlledLoad, 2),
            current + "_cost_generation": abs(costDataGeneration),
            current + "_suburb_average": suburbAverage,
            current + "_cost_difference": costDifference,
            current + "_difference_message": costDifferenceMessage['text'],
            current + "_percentage_difference": kwhPercentageDifference,
            current + "_consumption_difference": round(netConsumption - previousPeriodNetConsumption, 3),
            current + "_consumption_change": costDifferenceMessage['change'],

            previous + "_usage": round(previousPeriodPeakConsumption + previousPeriodOffPeakConsumption + previousPeriodShoulderConsumption + previousPeriodControlledLoadConsumption - previousPeriodGeneration, 3),
            previous + "_consumption": round(previousPeriodPeakConsumption + previousPeriodOffPeakConsumption + previousPeriodShoulderConsumption + previousPeriodControlledLoadConsumption, 3),
            previous + "_generation": previousPeriodGeneration
            }
        return period_data


    def _sum_period_array(self, json_array_of_value, rounding_digits):
        total_value = 0.0
        for value in json_array_of_value:
            if value is not None:
                total_value += value
        return round(total_value, rounding_digits)


    def _strip_currency(self, amount):
        import locale
        return locale.atof(amount.strip('$'))


    async def fetch_data(self):
        """Get the latest data from Jemena Outlook."""
        
        # setup requests session
        async with aiohttp.ClientSession() as session:
            # Get login page
            login_url = await self._get_login_page(session)
            
            # Post login page
            await self._post_login_page(session, login_url)

            # self._data.update(await self._get_tariffs(session))

            # Get Daily Usage data
            self._data.update(await self._get_daily_data(session, 1))

            # Get Daily Usage data
            self._data.update(await self._get_weekly_data(session, 0))

            # Get Daily Usage data
            self._data.update(await self._get_monthly_data(session, 0))


    def get_data(self):
        return self._data