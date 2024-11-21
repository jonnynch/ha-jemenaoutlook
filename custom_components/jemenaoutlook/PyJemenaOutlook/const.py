from datetime import timedelta

HOST = 'https://electricityoutlook.jemena.com.au'
HOME_URL = '{}/login/index'.format(HOST)
PERIOD_URL = ('{}/electricityView/period'.format(HOST))

REQUESTS_TIMEOUT = 15

MIN_TIME_BETWEEN_UPDATES = timedelta(hours=1)