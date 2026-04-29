
from django.utils.translation import gettext_lazy as _

# Do not reformat this document to avoid extra line breaks in the translated strings!

ERROR_CREATED_BEFORE = _(
    "Error: The date you set as 'Created before' has to be later than the date of 'Created after'."
)

THIS_IS_TEAM_TASK = _("""This is a team task.
Please create a sub-task for yourself for work.
Or press the next button when you have done your job.""")

USE_HTML = _(
    "Use HTML. To specify the address of the embedded image, use {% cid_media `path/to/pic.png` %}.<br>You can embed files uploaded to the CRM server in the `media/pics/` folder."
)

DATA_WARNING_MESSAGE = _(
"""Attention! Data for filters such as: 
transaction stages, reasons for closing, tags, etc. 
will be transferred only if the new department has data with the same name.
Also Output, Payment and Product will not be affected."""
)
