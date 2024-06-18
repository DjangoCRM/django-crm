from django.contrib.auth.models import Group
from django.core.management import call_command
from django.test import TransactionTestCase

from common.models import Department
from crm.models import ClientType
from crm.models import ClosingReason
from crm.models import Country
from crm.models import Currency
from crm.models import Industry
from crm.models import LeadSource
from crm.models import Stage
from tasks.models import ProjectStage
from tasks.models import TaskStage
from tasks.models import Resolution

# manage.py test tests.common.management.test_setupdata --noinput


class TestSetupData(TransactionTestCase):

    def setUp(self):
        print("Run Test Method:", self._testMethodName)

    def test_setupdata(self):
        call_command("setupdata")
        self.assertTrue(Country.objects.filter(name="Ukraine").exists())
        self.assertTrue(Currency.objects.filter(name="USD").exists())
        self.assertTrue(Group.objects.filter(name="managers").exists())
        self.assertTrue(Resolution.objects.filter(name="on approval").exists())
        self.assertTrue(Department.objects.filter(name="Global sales").exists())
        self.assertTrue(Stage.objects.filter(name="analysis of request").exists())
        self.assertTrue(ProjectStage.objects.filter(name="in progress").exists())
        self.assertTrue(TaskStage.objects.filter(name="in progress").exists())
        self.assertTrue(ClientType.objects.filter(name="reseller").exists())
        self.assertTrue(ClosingReason.objects.filter(name="The deal was closed successfully").exists())
        self.assertTrue(Industry.objects.filter(name="metallurgy").exists())
        self.assertTrue(LeadSource.objects.filter(name="website form").exists())
