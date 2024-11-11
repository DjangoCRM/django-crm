from django.test import tag

from crm.models import Contact
from crm.models import Company
from crm.models import CrmEmail
from crm.models import Lead
from crm.utils.counterparty_name import get_counterparty_name
from tests.base_test_classes import BaseTestCase

# manage.py test tests.crm.utils.test_get_counterparty_name --keepdb


@tag('TestCase')
class TesttestGetCounterpartyName(BaseTestCase):

    def setUp(self):
        print(" Run Test Method:", self._testMethodName)

    def test_get_counterparty_name(self):
        company = Company.objects.create(
            full_name='Test Company',
            email='info@company.com'
        )
        Contact.objects.create(
            first_name='Tom',
            last_name='Lee',
            secondary_email='info@company.com',
            company=company
        )
        Lead.objects.create(
            first_name='Lu',
            last_name='Lee',
            secondary_email='Lu@company.com'
        )
        eml = CrmEmail.objects.create(
            to='info@company.com',
            content="Some text",
            sent=True
        )
        name = get_counterparty_name(eml)
        self.assertEqual("Tom Lee <info@company.com>", name)

        eml.from_field = 'Lu@company.com'
        eml.sent = False
        eml.incoming =True
        eml.save()
        name = get_counterparty_name(eml)
        self.assertEqual("Lu Lee <Lu@company.com>", name)
