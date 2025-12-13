import json
import logging
import aiohttp
import asyncio
from .const import BOOTSTRAP_URL, FIELDS, JEMENA_APIKEY, PROPERTIES_URL,REQUESTS_TIMEOUT, GIGYA_APIKEY, CONSUMPTION_URL, LOGIN_URL,JWT_URL
from datetime import datetime, timedelta

from tzlocal import get_localzone

_LOGGER = logging.getLogger(__name__)

class JemenaOutlookError(Exception):
    pass

class JemenaOutlookClient(object):

    def __init__(self, username, password, timeout=REQUESTS_TIMEOUT):
        """Initialize the client object."""
        self.username = username
        self.password = password
        self._data = {}
        self._raw_data = {}
        self._timeout = timeout
        self._session = None

    async def _get_login_page(self, session):
        _LOGGER.debug("_get_login_page")
        """Go to the login page."""
        params = {
            'apiKey': GIGYA_APIKEY,
            'pageURL': 'https://myportal.jemena.com.au/', 
            'format': 'json'
        }
        async with session.get(BOOTSTRAP_URL, params=params, timeout=REQUESTS_TIMEOUT) as raw_res:
            if raw_res.status == 200:
                data = json.loads(await raw_res.text())
                return data
            else:
                return None

    async def _post_login_page(self, session):
        _LOGGER.debug("_post_login_page")
        """Login to Jemena Electricity Outlook website."""
        form_data = {
            "loginID": self.username,
            "password": self.password,
            "APIKey": GIGYA_APIKEY,
            'pageURL': 'https://myportal.jemena.com.au/', 
            'format': 'json'
            }
        async with session.post(LOGIN_URL,
                                    data = form_data,
                                    timeout = REQUESTS_TIMEOUT) as raw_res:
            status_code = raw_res.status
            if status_code != 200:
                raise JemenaOutlookError("Login error: Bad HTTP status code. {}".format(status_code))
            try:
                data = json.loads(await raw_res.text())
                _LOGGER.debug("_post_login_page: %s", data)
                return data['sessionInfo'].get('login_token', data['sessionInfo']['cookieValue'])
            except Exception:
                _LOGGER.error("_post_login_page: %s", data)
                raise JemenaOutlookError("Login response format incorrect: {}".format(raw_res))

    async def _post_get_jwt(self, session, login_token):
        _LOGGER.debug("_post_get_jwt")
        """Login to Jemena Electricity Outlook website."""
        form_data = {
            'login_token': login_token,
            'fields': 'data.serviceCloudID',
            "APIKey": GIGYA_APIKEY,
            'pageURL': 'https://myportal.jemena.com.au/', 
            'format': 'json'
            }
        async with session.post(JWT_URL,
                                    data = form_data,
                                    timeout = REQUESTS_TIMEOUT) as raw_res:
            status_code = raw_res.status 
            if status_code != 200:
                raise JemenaOutlookError("Login error: Bad HTTP status code. {}".format(status_code))
            data = json.loads(await raw_res.text())
            _LOGGER.debug("_get_jwt: %s", data)
            return data['id_token']
    async def _get_properties(self, session, jwt):
        _LOGGER.debug("_get_properties")
        """Get properties data."""

        headers = {
            'Authorization': f'Bearer {jwt}',
            'Content-Type': 'application/json',
            'Apikey': JEMENA_APIKEY
        }
        async with session.get(PROPERTIES_URL, headers=headers, timeout = REQUESTS_TIMEOUT) as raw_res:
            try:
                json_output = await raw_res.json()
            except (OSError, json.decoder.JSONDecodeError):
                raise JemenaOutlookError("Could not get properties data: {}".format(raw_res))
            
            _LOGGER.debug("Jemena outlook properties data: %s", json_output)

            return json_output[0]['nmi'], json_output[0]['postcode'], json_output[0]['propertyType']
    async def _get_raw_data(self, session, jwt, nmi, post_code, property_type, date_from):
        _LOGGER.info("_get_raw_data")
        """Get hourly data for specific date."""

        date_string = date_from.strftime('%Y-%m-%d')
        headers = {
            'Authorization': f'Bearer {jwt}',
            'Content-Type': 'application/json',
            'Apikey': JEMENA_APIKEY
        }
        body = {
            "nmi": nmi,
            "channel":"Consumption",
            "postcode":post_code,
            "premiseType": property_type,
            "format":"json",
            "interval":"hourly",
            "dateFrom": date_string,
            "dateTo": date_string
        }
        async with session.post(CONSUMPTION_URL, headers=headers, json=body, timeout = REQUESTS_TIMEOUT) as raw_res:
            try:
                json_output = await raw_res.json()
            except (OSError, json.decoder.JSONDecodeError):
                raise JemenaOutlookError("Could not get daily data: {}".format(raw_res))
            
            _LOGGER.debug("Jemena outlook daily data - json: %s", json_output)
            period_data = self._extract_period_data(json_output)
            
            _LOGGER.debug("Jemena outlook daily data - extracted: %s", period_data)
            
        return period_data
               


    def _extract_period_data(self, json_data):
        _LOGGER.info("_extract_period_data")
        period_data = {}
        for field in FIELDS:
            period_data[field] = []
        
        date_from = json_data['dateFrom']
        tz = get_localzone()

        for i, interval in enumerate(json_data['interval']):
            time_from = interval.split("-")[0].strip()
            time_to = interval.split("-")[1].strip()
            for field in FIELDS:
                if len(json_data[field]) <= i:
                    continue
                entry = {
                    'from': datetime.strptime(date_from + ' ' + time_from, "%Y-%m-%d %H:%M").replace(tzinfo=tz),
                    'to': datetime.strptime(date_from + ' ' + time_to, "%Y-%m-%d %H:%M").replace(tzinfo=tz),
                    'value': json_data[field][i]
                }
                period_data[field].append(entry)
        return period_data

    async def fetch_data(self):
        _LOGGER.info("fetch_data")
        """Get the latest data from Jemena Outlook."""
        
        # setup requests session
        async with aiohttp.ClientSession() as session:
            # Get login page
            await self._get_login_page(session)
            
            # Post login page
            login_token = await self._post_login_page(session)
            _LOGGER.debug("login_token: %s", login_token)
            jwt = await self._post_get_jwt(session, login_token)
            _LOGGER.debug("jwt: %s", jwt)
            nmi, post_code, property_type = await self._get_properties(session, jwt)
            # Get Hourly Usage data
            today = datetime.today()
            date_from = today - timedelta(days=3)
            self._raw_data = {}
            for field in FIELDS:
                self._raw_data[field] = []
            tasks = []
            while date_from <= today:
                tasks.append(self._get_raw_data(session, jwt, nmi, post_code, property_type, date_from))
                date_from = date_from + timedelta(days=1)
            responses = await asyncio.gather(*tasks)
            for response in responses:
                for field in FIELDS:
                    self._raw_data[field] = self._raw_data[field] + response[field]
            self._data.update(self.extract_state_data())

    def extract_state_data(self):
        _LOGGER.info("extract_state_data")
        state_data = {}
        for field in FIELDS:
            state_data[field] = sum(item["value"] for item in self._raw_data[field])
        return state_data
    def get_data(self):
        return self._data
    def get_raw_data(self):
        return self._raw_data