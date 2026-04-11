import json
import logging
import aiohttp
import asyncio
import copy
from .const import BOOTSTRAP_URL, FIELDS, FINALIZE_REG_URL, JEMENA_APIKEY, PROPERTIES_URL,REQUESTS_TIMEOUT, GIGYA_APIKEY, CONSUMPTION_URL, LOGIN_URL,JWT_URL, TFA_EMAIL_COMPLETE_URL, TFA_EMAIL_GET_URL, TFA_EMAIL_SEND_URL, TFA_ERROR, TFA_FINALIZE_URL, TFA_INIT_URL
from datetime import datetime, timedelta
from types import SimpleNamespace

from tzlocal import get_localzone

_LOGGER = logging.getLogger(__name__)

class JemenaOutlookError(Exception):
    pass

class JemenaOutlookClient(object):

    def __init__(self, username, password, gmid = None, timeout=REQUESTS_TIMEOUT):
        """Initialize the client object."""
        self.username = username
        self.password = password
        self.gmid = gmid
        self._data = {}
        self._raw_data = {}
        self._timeout = timeout
        self._session = None
        self._tfa = {}

    async def login(self):
        async with aiohttp.ClientSession() as session:
            return await self.login_with_session(session)

    async def login_with_session(self, session):
        response, json = await self._post_login_page(session)
        error_code = json.get("errorCode",0)
        error_message = json.get("errorMessage",'')
        error_details = json.get("errorDetails",'')
        reg_token = json.get("regToken",0)

        login_token = json.get('sessionInfo',{}).get('cookieValue', '')
        if error_code == 0:
            response, json = await self._post_get_jwt(session, login_token)
            id_token = json.get("id_token")
            return SimpleNamespace(**{
                "id_token": id_token,
                "login_token": login_token,
                "success": True
            })
        elif error_code == TFA_ERROR:
            self.tfa = SimpleNamespace()
            self.tfa.reg_token = reg_token
            return SimpleNamespace(**{
                "error_code": error_code,
                "error_message": error_message,
                "error_details": error_details,
                "tfa": True,
                "success": False
            })
        else:
            return SimpleNamespace(**{
                "error_code": error_code,
                "error_message": error_message,
                "error_details": error_details,
                "tfa": False,
                "success": False
            })
    
    async def send_tfa(self):
        async with aiohttp.ClientSession() as session:
            return await self.send_tfa_with_session(session)
        
    async def send_tfa_with_session(self, session):
        reg_token = self.tfa.reg_token

        response, json = await self._get_login_page(session)
        gmid = response.cookies.get('gmid').value
        self.tfa.cookies = response.cookies
        self.tfa.gmid = gmid

        response, json = await self._tfa_init(session, reg_token)
        gigya_assertion = json.get("gigyaAssertion","")
        self.tfa.gigya_assertion = gigya_assertion

        response, json = await self._tfa_email_get(session, gigya_assertion)
        email_id = json.get("emails",[{}])[0].get("id","")
        self.tfa.email_id = email_id

        response, json = await self._tfa_email_send(session, email_id, reg_token, gigya_assertion)
        phv_token = json.get("phvToken","")
        self.tfa.phv_token = phv_token

    async def submit_tfa(self, code):
        async with aiohttp.ClientSession(cookies = self.tfa.cookies) as session:
            return await self.submit_tfa_with_session(session, code)
        
    async def submit_tfa_with_session(self, session, code):
        reg_token = self.tfa.reg_token
        gigya_assertion = self.tfa.gigya_assertion
        phv_token = self.tfa.phv_token
        gmid = self.tfa.gmid

        response, json = await self._tfa_email_complete(session, code, reg_token, gigya_assertion, phv_token)
        provider_assertion = json.get("providerAssertion","")
        self.tfa.provider_assertion = provider_assertion

        response, json = await self._tfa_finalize(session, reg_token, gigya_assertion, provider_assertion)

        response, json = await self._final_registration(session, reg_token)
        error_code = json.get("errorCode",0)
        error_message = json.get("errorMessage",'')
        error_details = json.get("errorDetails",'')
        login_token = json.get('sessionInfo',{}).get('login_token', '')
        
        if error_code == 0:
            return SimpleNamespace(**{
                "gmid": gmid,
                "login_token": login_token,
                "success": True
            })
        else:
            return SimpleNamespace(**{
                "error_code": error_code,
                "error_message": error_message,
                "error_details": error_details,
                "success": False
            })

    async def _final_registration(self, session, reg_token):
        params  = {
            "regToken": reg_token,
            "APIKey": GIGYA_APIKEY,
            'pageURL': 'https://myportal.jemena.com.au/', 
            'format': 'json'
            }
        return await self._get(session, FINALIZE_REG_URL, params)
    
    async def _tfa_finalize(self, session, reg_token, gigya_assertion, provider_assertion):
        params  = {
            "gigyaAssertion": gigya_assertion,
            "providerAssertion": provider_assertion,
            "tempDevice": "false",
            "regToken": reg_token,
            "APIKey": GIGYA_APIKEY,
            'pageURL': 'https://myportal.jemena.com.au/', 
            'format': 'json'
            }
        return await self._get(session, TFA_FINALIZE_URL, params)
    
    async def _tfa_email_complete(self, session, code, reg_token, gigya_assertion, phv_token):
        params  = {
            "gigyaAssertion": gigya_assertion,
            "phvToken": phv_token,
            "code": code,
            "regToken": reg_token,
            "APIKey": GIGYA_APIKEY,
            'pageURL': 'https://myportal.jemena.com.au/', 
            'format': 'json'
            }
        return await self._get(session, TFA_EMAIL_COMPLETE_URL, params)

    async def _tfa_email_get(self, session, gigya_assertion):
        params  = {
            "gigyaAssertion": gigya_assertion,
            "APIKey": GIGYA_APIKEY,
            'pageURL': 'https://myportal.jemena.com.au/', 
            'format': 'json'
            }
        return await self._get(session, TFA_EMAIL_GET_URL, params)
    
    async def _tfa_email_send(self, session, email_id, reg_token, gigya_assertion):
        params  = {
            "emailID": email_id,
            "gigyaAssertion": gigya_assertion,
            "mode": 'verify',
            "regToken": reg_token,
            "APIKey": GIGYA_APIKEY,
            'pageURL': 'https://myportal.jemena.com.au/', 
            'format': 'json'
            }
        return await self._get(session, TFA_EMAIL_SEND_URL, params)
    async def _get(self, session, url, params):
        _LOGGER.info("Request URL: %s", url)
        _LOGGER.debug("Request params: %s", params)
        async with session.get(url,
                                    params=params, 
                                    timeout = REQUESTS_TIMEOUT) as raw_res:
            status_code = raw_res.status
            if status_code != 200:
                raise JemenaOutlookError("Error: Bad HTTP status code. {}".format(status_code))
            try:
                data = json.loads(await raw_res.text())
                _LOGGER.debug("Response Body: %s", data)
                return raw_res, data
            except Exception:
                _LOGGER.error("Response Body: %s", data)
                raise JemenaOutlookError("Response format incorrect: {}".format(raw_res))
            
    async def _tfa_init(self, session, reg_token):
        params  = {
            "provider": 'gigyaEmail',
            "mode": 'verify',
            "regToken": reg_token,
            "APIKey": GIGYA_APIKEY,
            'pageURL': 'https://myportal.jemena.com.au/', 
            'format': 'json'
            }
        return await self._get(session, TFA_INIT_URL, params)

    async def _get_login_page(self, session):
        """Go to the login page."""
        params = {
            'apiKey': GIGYA_APIKEY,
            'pageURL': 'https://myportal.jemena.com.au/', 
            'format': 'json'
        }
        return await self._get(session, BOOTSTRAP_URL, params)

    def redact(self,data):
        sensitive_keys = ['password']
        redacted = copy.deepcopy(data)
        def redact_dict(d):
            if not isinstance(d, dict):
                return d
            for key in d:
                # Check if key matches sensitive field (case-insensitive)
                if any(sensitive.lower() in key.lower() for sensitive in sensitive_keys):
                    d[key] = '***REDACTED***'
                elif isinstance(d[key], dict):
                    redact_dict(d[key])
                elif isinstance(d[key], list):
                    for item in d[key]:
                        if isinstance(item, dict):
                            redact_dict(item)
            return d
        return redact_dict(redacted)
    async def _post(self, session, url, data):
        _LOGGER.info("Request URL: %s", url)
        _LOGGER.debug("Request data: %s", self.redact(data))
        async with session.post(url,
                                    data=data, 
                                    timeout = REQUESTS_TIMEOUT) as raw_res:
            status_code = raw_res.status
            if status_code != 200:
                raise JemenaOutlookError("Error: Bad HTTP status code. {}".format(status_code))
            try:
                data = json.loads(await raw_res.text())
                _LOGGER.debug("Response Body: %s", data)
                return raw_res, data
            except Exception:
                _LOGGER.error("Response Body: %s", data)
                raise JemenaOutlookError("Response format incorrect: {}".format(raw_res))
            
    async def _post_login_page(self, session):
        """Login to Jemena Electricity Outlook website."""
        form_data = {
            "loginID": self.username,
            "password": self.password,
            "APIKey": GIGYA_APIKEY,
            'pageURL': 'https://myportal.jemena.com.au/', 
            'gmid': self.gmid,
            'format': 'json'
            }
        return await self._post(session, LOGIN_URL, form_data)

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
        return await self._post(session, JWT_URL, form_data)
        
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
        
    async def _get_raw_data(self, semaphore, session, jwt, nmi, post_code, property_type, date_from):
        _LOGGER.info("_get_raw_data - %s", date_from)
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

        async with semaphore:
            async with session.post(CONSUMPTION_URL, headers=headers, json=body, timeout = REQUESTS_TIMEOUT) as raw_res:
                try:
                    json_output = await raw_res.json()
                except (OSError, json.decoder.JSONDecodeError):
                    raise JemenaOutlookError("Could not get daily data: {}".format(raw_res))
                
                _LOGGER.debug("Jemena outlook daily data - json: %s", json_output)
                period_data = self._extract_period_data(json_output, date_from)
                
                _LOGGER.debug("Jemena outlook daily data - extracted: %s", period_data)
                
            return period_data

    def _extract_period_data(self, json_data, date_from):
        _LOGGER.info("_extract_period_data - %s", date_from)
        period_data = {}
        for field in FIELDS:
            period_data[field] = []
        
        date_from = json_data.get('dateFrom','')

        if date_from:
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
        else:
            _LOGGER.warning("_extract_period_data - %s - skipped - %s", date_from, json_data)
        return period_data

    async def fetch_data(self, backday = 3):
        _LOGGER.info("fetch_data")
        """Get the latest data from Jemena Outlook."""
        
        max_concurrent = 3  # Set your limit
        semaphore = asyncio.Semaphore(max_concurrent)

        # setup requests session
        async with aiohttp.ClientSession() as session:
            # Get login page
            response = await self.login_with_session(session)
            if response.success:
                jwt = response.id_token
                _LOGGER.debug("jwt: %s", jwt)
                nmi, post_code, property_type = await self._get_properties(session, jwt)
                # Get Hourly Usage data
                today = datetime.today()
                date_from = today - timedelta(days=backday)
                self._raw_data = {}
                for field in FIELDS:
                    self._raw_data[field] = []
                tasks = []
                while date_from <= today:
                    tasks.append(self._get_raw_data(semaphore, session, jwt, nmi, post_code, property_type, date_from))
                    date_from = date_from + timedelta(days=1)
                responses = await asyncio.gather(*tasks)
                for response in responses:
                    for field in FIELDS:
                        self._raw_data[field] = self._raw_data[field] + response[field]
                self._data.update(self.extract_state_data())
            elif response.tfa:
                _LOGGER.error("Login failed: %s-%s", response.error_code, response.error_message)
                _LOGGER.error("Details: %s", response.error_details)
                _LOGGER.error("Jemena Portal asked for TFA again, please try to reconfigure the entity")
            else:
                _LOGGER.error("Login failed: %s-%s", response.error_code, response.error_message)
                _LOGGER.error("Details: %s", response.error_details)
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