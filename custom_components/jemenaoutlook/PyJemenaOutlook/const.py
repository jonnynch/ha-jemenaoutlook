from datetime import timedelta
GIGYA_APIKEY = '4_3S0sVR-vpGLuIi799q2cKA'
BOOTSTRAP_URL = 'https://accounts.au1.gigya.com/accounts.webSdkBootstrap'
LOGIN_URL = 'https://accounts.au1.gigya.com/accounts.login'
JWT_URL = 'https://accounts.au1.gigya.com/accounts.getJWT'


JEMENA_APIKEY = 'jemk_FjOROo18mVPYop14ESEMeenKdkNr8uQ2JdH6b4nLdqGAoFyLiixwZs57CUoisNTo'
PROPERTIES_URL = 'https://api.jemena.com.au/customer/portal/v1/properties'
CONSUMPTION_URL = 'https://api.jemena.com.au/customer/portal/v1/consumption/nmi'


REQUESTS_TIMEOUT = 60

CONF_COST = "CONF_COST"
CONF_TODAY = "CONF_TODAY"
CONF_DAILY = "CONF_DAILY"
CONF_WEEKLY = "CONF_WEEKLY"
CONF_MONTHLY = "CONF_MONTHLY"

MIN_TIME_BETWEEN_UPDATES = timedelta(hours=1)

FIELDS = ["consumptionUsage","postCodeAverage","generation"]

DOMAIN = "jemenaoutlook"