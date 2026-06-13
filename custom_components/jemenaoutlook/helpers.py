import asyncio
import logging
from homeassistant.util import dt as dt_util
_LOGGER = logging.getLogger(__name__)

async def get_otp_token(hass, entity_id, manual_input = None, max_age_seconds = 60, retry_delay_seconds = 10, max_retries = 7):
    for attempt in range(max_retries):
        _LOGGER.debug(f"Get OTP attempts: {attempt}")
        if manual_input:
            return manual_input
        elif not entity_id:
            return None
        else:
            state = hass.states.get(entity_id)
            if state is not None:
                _LOGGER.debug(f"Got OTP: {state.state}")
                now = dt_util.utcnow()
                age = (now - state.last_updated).total_seconds()
                _LOGGER.debug(f"OTP age: {age}")
                if age <= max_age_seconds:
                    return state.state
            else:
                _LOGGER.debug(f"OTP entity state is empty")
            if attempt < max_retries - 1:
                _LOGGER.debug(f"Sleep for otp checking")
                await asyncio.sleep(retry_delay_seconds)
    return manual_input