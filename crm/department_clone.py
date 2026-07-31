"""Models cloned when copying a CRM department."""

from crm.models import ClientType
from crm.models import ClosingReason
from crm.models import Industry
from crm.models import LeadSource
from crm.models import Product
from crm.models import Stage

DEPARTMENT_CLONE_MODELS = [
    Product,
    Stage,
    ClosingReason,
    ClientType,
    Industry,
    LeadSource,
]


def get_department_clone_models():
    return DEPARTMENT_CLONE_MODELS
