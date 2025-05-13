from django.utils.translation import gettext_lazy as _
from django.utils.safestring import mark_safe


SHIPMENT_DATE_CHECK = True

# List of fields, the value of which will be saved
# to the Excel file when exporting contact persons.
CONTACT_COLUMNS = [
    'first_name', 'last_name', 'title', 'sex', 'birth_date',
    'was_in_touch', 'phone', 'other_phone', 'mobile', 
    'email', 'secondary_email', 'city_name', 'address',
    'country', 'description', 'birth_date', 'owner',
    'company', 'department', 'disqualified', 'massmail'
]

# List of fields, the value of which will be saved
# to the Excel file when exporting companies.
COMPANY_COLUMNS = [
    'full_name', 'website', 'phone', 'city_name', 'address',
    'email', 'description', 'lead_source', 'was_in_touch',
    'country',  'owner', 'type', 'industry', 'department',
    'disqualified', 'massmail'
]

# List of fields, the value of which will be saved
# to the Excel file when exporting leads.
LEAD_COLUMNS = [
    'first_name', 'last_name', 'title', 'sex', 'birth_date',
    'was_in_touch', 'email', 'secondary_email', 'phone',
    'other_phone', 'mobile', 'city_name', 'country',
    'address', 'description', 'lead_source', 'website',
    'company_phone', 'city_name', 'company_address',
    'company_email', 'owner', 'company_name', 'department',
    'disqualified', 'massmail'
]

# List of fields, the value of which will be saved
# to the Excel file when exporting deals.
DEAL_COLUMNS = [
    'request', 'contact', 'contact__email', 'contact__phone',
    'company', 'lead', 'lead__email', 'lead__phone',
    'ticket', 'creation_date'
]

FIRST_STEP = _('Establish the first contact with the client.')


CONVERT_REQUIRED_FIELDS = (
    'first_name', 'email',      # 'last_name'
    'company_name', 'company_email'
)

KEEP_TICKET = mark_safe(
    '<br><br><br><font size="1" color="#003366">'
    'Your request is assigned a [ticket:%s].<br>'
    'Please keep it in correspondence.</font>'
)

# For IMAP connection
REUSE_IMAP_CONNECTION = False   # True - a little faster but less stable (with some IMAP servers)
IMAP_CONNECTION_IDLE = 4320     # minutes (3 days)
IMAP_NOOP_PERIOD = 4 * 60       # seconds
IMAP_DEBUG_LEVEL = 0
