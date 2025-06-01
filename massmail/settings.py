
MAILING = True  # allow mailing

EMAILS_PER_DAY = 94

# Newsletter distribution may only be carried out during working hours.

USE_BUSINESS_TIME = False

BUSINESS_TIME_START = {
    'hour': 8,
    'minute': 30
    }

BUSINESS_TIME_END = {
    'hour': 17,
    'minute': 30
    }

# In order not to show customers the CRM address, create a page on your website where 
# customers will be redirected after unsubscribing.
UNSUBSCRIBE_URL = 'https://www.example.com/unsubscribe'
