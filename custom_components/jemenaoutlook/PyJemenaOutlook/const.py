from datetime import timedelta
GIGYA_APIKEY = '4_3S0sVR-vpGLuIi799q2cKA'
BOOTSTRAP_URL = 'https://accounts.au1.gigya.com/accounts.webSdkBootstrap'
LOGIN_URL = 'https://accounts.au1.gigya.com/accounts.login'
JWT_URL = 'https://accounts.au1.gigya.com/accounts.getJWT'

TFA_INIT_URL = 'https://accounts.au1.gigya.com/accounts.tfa.initTFA'
TFA_EMAIL_GET_URL = 'https://accounts.au1.gigya.com/accounts.tfa.email.getEmails'
TFA_EMAIL_SEND_URL = 'https://accounts.au1.gigya.com/accounts.tfa.email.sendVerificationCode'
TFA_EMAIL_COMPLETE_URL = 'https://accounts.au1.gigya.com/accounts.tfa.email.completeVerification'
TFA_FINALIZE_URL = 'https://accounts.au1.gigya.com/accounts.tfa.finalizeTFA'
FINALIZE_REG_URL = 'https://accounts.au1.gigya.com/accounts.finalizeRegistration'

JEMENA_APIKEY = 'jemk_FjOROo18mVPYop14ESEMeenKdkNr8uQ2JdH6b4nLdqGAoFyLiixwZs57CUoisNTo'
PROPERTIES_URL = 'https://api.jemena.com.au/customer/portal/v1/properties'
CONSUMPTION_URL = 'https://api.jemena.com.au/customer/portal/v1/consumption/nmi'

TFA_ERROR = 403101
REQUESTS_TIMEOUT = 60

MIN_TIME_BETWEEN_UPDATES = timedelta(hours=1)

FIELDS = ["consumptionUsage","postCodeAverage","generation"]

DOMAIN = "jemenaoutlook"