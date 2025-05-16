"""Jemena Outlook data 'collector' that downloads the utilization data."""
import logging
from custom_components.jemenaoutlook.PyJemenaOutlook.jemena_client import JemenaOutlookClient, JemenaOutlookError
from custom_components.jemenaoutlook.const import SENSOR_TYPES
from homeassistant.util import Throttle

from .const import DOMAIN, REQUESTS_TIMEOUT, MIN_TIME_BETWEEN_UPDATES

from homeassistant.components.recorder import get_instance
from homeassistant.components.recorder.statistics import (
    async_add_external_statistics,
    statistics_during_period
)
from homeassistant.components.recorder.models import StatisticMetaData, StatisticData
from datetime import timedelta

_LOGGER = logging.getLogger(__name__)

class Collector:
    """Collector for PyJemenaOutlook."""

    def __init__(self, hass, username, password, options):
        """Init collector."""
        self.client = JemenaOutlookClient(
            username, password, options, REQUESTS_TIMEOUT)
        self._hass = hass
        self.data = {}

    async def _fetch_data(self):
        """Fetch latest data from Jemena Outlook."""
        try:
            _LOGGER.info("_fetch_data")
            await self.client.fetch_data()
        except JemenaOutlookError as exp:
            _LOGGER.error("Error on receive last Jemena Outlook data: %s", exp)
            return

    async def _process_data(self):
        """Processed latest data from Jemena Outlook and HA."""
        for field in SENSOR_TYPES.keys():
            statistic_id = f"{DOMAIN}:{SENSOR_TYPES[field][0]}".replace(" ","_").lower()
            try:
                raw_data =  self.client.get_raw_data()

                statistics = []
                sums = await self.get_last_sum(statistic_id, raw_data[field][0]["from"], SENSOR_TYPES[field][1])
                if sums == 0:
                    statistics.append(
                        StatisticData(
                            start=raw_data[field][0]["from"] -  timedelta(hours=1),
                            sum=0,
                            state=0
                        )
                    )
                for data in raw_data[field]:
                    start = data["from"]
                    sums = sums + data["value"]
                    statistics.append(
                        StatisticData(
                            start=start,
                            sum=sums,
                            state=sums
                        )
                    )
                self.data[field]=sums
                _LOGGER.info("async_add_external_statistics")
                _LOGGER.debug(statistic_id)
                _LOGGER.debug(statistics)
                async_add_external_statistics(
                    self._hass,
                    StatisticMetaData(
                        has_mean=False,
                        has_sum=True,
                        name=None,
                        source=DOMAIN,
                        statistic_id=statistic_id,
                        unit_of_measurement=SENSOR_TYPES[field][1],
                    ),
                    statistics
                )
            except Exception as ex:
                _LOGGER.error("Error on adding statistics: %s", ex)
                _LOGGER.exception("An error occurred")

    async def get_data(self):
        """Return the contract list."""
        # Fetch data
        _LOGGER.info("get_data")
        await self._fetch_data()
        await self._process_data()
        return self.data

    async def get_last_sum(self, statistics_id, from_date, unit):
        _LOGGER.info("get_last_sum")
        stat = await get_instance(self._hass).async_add_executor_job(
                        statistics_during_period,
                        self._hass,
                        from_date - timedelta(days=1),
                        from_date,
                        {
                            statistics_id
                        },
                        "hour",
                        unit,
                        {"change","state","sum"},
                    )
        _LOGGER.debug(stat)
        if len(stat) > 0:
            return stat[statistics_id][-1]["sum"]
        else:
            return 0
    @Throttle(MIN_TIME_BETWEEN_UPDATES)
    async def async_update(self):
        """Return the latest collected data from Jemena Outlook."""
        _LOGGER.info("async_update")
        await self._fetch_data()
        await self._process_data()

        
    


