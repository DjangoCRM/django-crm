from datetime import timedelta
from django.conf import settings
from django.contrib.auth.models import Group
from django.contrib.contenttypes.models import ContentType
from django.core import mail
from django.test import tag
from django.urls import reverse
from django.utils.formats import date_format

from common.models import Reminder
from common.utils.helpers import get_delta_date
from common.utils.helpers import USER_MODEL
from common.utils.helpers import get_department_id
from common.utils.helpers import get_now
from crm.models import Currency
from crm.models import Deal
from crm.models import CrmEmail
from crm.models import Output
from crm.models import Payment
from crm.models import Product
from crm.models import Request
from crm.models import Stage
from crm.models.others import ClosingReason
from tests.crm.test_request_methods import populate_db
from tests.base_test_classes import BaseTestCase
from tests.utils.helpers import get_adminform_initials


# python manage.py test tests.crm.test_deal --keepdb


@tag('TestCase')
class TestDeal(BaseTestCase):
    """Test edit Deal instance"""

    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()
        populate_db(cls)
        cls.contact_request = get_contact_request()
        username_list = ("Adam.Admin", "Garry.Chief", "Nadia.Storekeeper",
                         "Darian.Manager.Co-worker.Head.Global")
        users = USER_MODEL.objects.filter(
            username__in=username_list)
        cls.co_owner = users.get(
            username="Darian.Manager.Co-worker.Head.Global")
        cls.chief = users.get(username="Garry.Chief")
        cls.admin = users.get(username="Adam.Admin")
        cls.storekeeper = users.get(
            username="Nadia.Storekeeper")
        cls.deal_changelist_url = reverse("site:crm_deal_changelist")
        cls.department = Group.objects.get(id=get_department_id(cls.owner))
        cls.now = get_now()
        cls.currency = Currency.objects.first()

    def setUp(self):
        print("Run Test Method:", self._testMethodName)
        self.deal = get_test_deal(self)
        CrmEmail.objects.create(
            to='sale@crm.com',
            from_field='',
            subject='test inquiry',
            content='',
            incoming=True,
            inquiry=True,
            department=self.department,
            owner=self.owner,
            deal=self.deal,
            is_html=False,
            creation_date=self.now - timedelta(days=7)
        )
        Payment.objects.create(
            deal=self.deal,
            status=Payment.RECEIVED,
            amount=100,
            currency=self.currency
        )
        product = Product.objects.create(
            name="Product for deal tes",
            department=self.department,
        )
        self.output = Output.objects.create(
            deal=self.deal,
            product=product,
            currency=self.currency,
            shipping_date=self.now.date()
        )
        self.client.force_login(self.owner)
        self.deal_change_url = reverse(
            "site:crm_deal_change", args=(self.deal.id,)
        )

    def test_unreceived_payments_deletion_of_deactivated_deal(self):
        payment = Payment.objects.create(
            amount=500,
            currency=self.currency,
            payment_date=self.now.date(),
            status=Payment.LOW_PROBABILITY,
            deal=self.deal,
        )
        payment_id = payment.id
        response = self.client.get(self.deal_change_url, follow=True)
        self.assertEqual(response.status_code, 200, response.reason_phrase)
        closing_reason = ClosingReason.objects.filter(
            success_reason=False,
            department=self.deal.department
        ).first()
        data = get_adminform_initials(response)
        data['closing_reason'] = str(closing_reason.id)
        data['_save'] = ''
        response = self.client.post(self.deal_change_url, data, follow=True)
        self.assertNoFormErrors(response)
        self.assertEqual(response.status_code, 200, response.reason_phrase)
        self.assertTrue(Payment.objects.filter(
            deal=self.deal,
            status=Payment.RECEIVED,
            amount=100,
            currency=self.currency
        ).exists())
        self.assertFalse(Payment.objects.filter(
            id=payment_id,
        ).exists())

    def test_deal_changelist(self):
        response = self.client.get(self.deal_changelist_url, follow=True)
        self.assertEqual(response.status_code, 200, response.reason_phrase)
        self.assertIn('admin/crm/deal/change_list.html',
                      response.template_name)
        self.assertIn(self.deal_change_url, response.rendered_content)
        response = self.client.get(self.deal_change_url, follow=True)
        self.assertEqual(response.status_code, 200, response.reason_phrase)

    def test_for_chief(self):
        """
        Test the availability of the fields 'important' and 'translation' for the chief.
        """
        self.client.force_login(self.chief)
        response = self.client.get(self.deal_change_url, follow=True)
        self.assertEqual(response.status_code, 200, response.reason_phrase)
        self.assertNotIn(
            'important', response.context['adminform'].readonly_fields)
        fields = []
        for item in response.context['adminform'].fieldsets:
            for i in item[1]['fields']:
                if type(i) is str:
                    fields.append(i)
                else:
                    fields.extend([*i])
        self.assertIn('translation', fields)
        data = get_adminform_initials(response)
        data['important'] = True
        del data['co_owner']
        response = self.client.post(
            self.deal_change_url + "?_changelist_filters=department%3D9",
            data, follow=True
        )
        self.assertNoFormErrors(response)
        self.assertEqual(response.status_code, 200, response.reason_phrase)

    def test_fix_deal_by_admin(self):
        """
        Test the ability to edit a deal by an administrator.
        """
        self.client.force_login(self.admin)
        deal_change_url = reverse(
            "admin:crm_deal_change", args=(self.deal.id,)
        )
        response = self.client.get(deal_change_url, follow=True)
        self.assertEqual(response.status_code, 200, response.reason_phrase)
        self.assertNotIn(
            'important', response.context['adminform'].readonly_fields)
        data = get_adminform_initials(response)
        del data['co_owner']
        data['payment_set-TOTAL_FORMS'] = '0'
        data['output_set-TOTAL_FORMS'] = '0'
        response = self.client.post(
            deal_change_url + "?_changelist_filters=department%3D9",
            data, follow=True
        )
        self.assertNoFormErrors(response)
        self.assertEqual(response.status_code, 200, response.reason_phrase)

    def test_product_is_shipped(self):
        self.client.force_login(self.storekeeper)
        shipment_change_url = reverse(
            "site:crm_shipment_change", args=(self.output.id,)
        )
        response = self.client.get(shipment_change_url, follow=True)
        self.assertEqual(response.status_code, 200, response.reason_phrase)

        data = get_adminform_initials(response)
        date = self.now.date()
        data['actual_shipping_date'] = date_format(
            date, format='SHORT_DATE_FORMAT', use_l10n=True)
        data['product_is_shipped'] = True
        with self.settings(DEBUG=False):
            response = self.client.post(shipment_change_url, data, follow=True)
            self.assertNoFormErrors(response)
            self.assertEqual(response.status_code, 200, response.reason_phrase)
            self.assertEqual(len(mail.outbox), 2)  # NOQA
            mail.outbox = []
        stage = Stage.objects.get(
            goods_shipped=True,
            department=self.deal.department,
        )
        self.deal.refresh_from_db()
        self.assertEqual(self.deal.stage, stage)
        self.assertEqual(self.deal.next_step_date, self.now.date())

    def test_change_next_step(self):
        self.change_next_step()

    def test_co_owner_changes_next_step(self):
        self.client.force_login(self.co_owner)
        self.change_next_step()

    def change_next_step(self):
        date = self.now.date()
        # open deal in change view
        response = self.client.get(self.deal_change_url, follow=True)
        self.assertEqual(response.status_code, 200, response.reason_phrase)
        data = get_adminform_initials(response)
        data['next_step'] = "next step"
        data['next_step_date'] = date_format(
            date, format='SHORT_DATE_FORMAT', use_l10n=True)
        data['payment_set-TOTAL_FORMS'] = '0'
        data['output_set-TOTAL_FORMS'] = '0'
        # submit form
        response = self.client.post(self.deal_change_url, data, follow=True)
        self.assertNoFormErrors(response)
        self.assertEqual(response.status_code, 200, response.reason_phrase)
        self.assertEqual(
            response.redirect_chain[0][0], self.deal_changelist_url)

    def test_deal_doesnt_exists(self):
        self.obj_doesnt_exists(Deal)

    def test_remind_me(self):
        # test setting on "remind me" field
        # open deal in change view
        response = self.client.get(self.deal_change_url, follow=True)
        self.assertEqual(response.status_code, 200, response.reason_phrase)
        data = get_adminform_initials(response)
        data['remind_me'] = True
        data['payment_set-TOTAL_FORMS'] = '0'
        data['output_set-TOTAL_FORMS'] = '0'
        data['_continue'] = ''
        # submit form
        response = self.client.post(self.deal_change_url, data, follow=True)
        self.assertNoFormErrors(response)
        self.assertEqual(response.status_code, 200, response.reason_phrase)
        # The Reminder obj has been created?
        self.assertTrue(Reminder.objects.filter(
            content_type=ContentType.objects.get_for_model(self.deal),
            object_id=self.deal.id,
            description=self.deal.next_step,
            owner=self.deal.owner,
            active=True,
            reminder_date__contains=self.deal.next_step_date
        ).exists())

        # test changing "next_step_date" field
        next_step_date = self.deal.next_step_date + timedelta(days=1)
        data = get_adminform_initials(response)
        data['next_step_date'] = next_step_date
        data['payment_set-TOTAL_FORMS'] = '0'
        data['output_set-TOTAL_FORMS'] = '0'
        data['_continue'] = ''
        # submit form
        response = self.client.post(self.deal_change_url, data, follow=True)
        self.assertNoFormErrors(response)
        self.assertEqual(response.status_code, 200, response.reason_phrase)

        # The Reminder obj has been changed?
        self.assertTrue(Reminder.objects.filter(
            content_type=ContentType.objects.get_for_model(self.deal),
            object_id=self.deal.id,
            description=self.deal.next_step,
            owner=self.deal.owner,
            active=True,
            reminder_date__contains=next_step_date
        ).exists())

        # test changing "next_step" field
        next_step = self.deal.next_step + ' changing1'
        data = get_adminform_initials(response)
        data['next_step'] = next_step
        data['payment_set-TOTAL_FORMS'] = '0'
        data['output_set-TOTAL_FORMS'] = '0'
        data['_continue'] = ''
        # submit form
        response = self.client.post(self.deal_change_url, data, follow=True)
        self.assertNoFormErrors(response)
        self.assertEqual(response.status_code, 200, response.reason_phrase)
        # The Reminder obj has been changed?
        self.assertTrue(Reminder.objects.filter(
            content_type=ContentType.objects.get_for_model(self.deal),
            object_id=self.deal.id,
            description=next_step,
            owner=self.deal.owner,
            active=True,
            reminder_date__contains=next_step_date
        ).exists())

        # test changing "next_step" & "next_step_date" fields
        next_step_date = next_step_date + timedelta(days=2)
        next_step = next_step + ' changing2'
        data = get_adminform_initials(response)
        data['next_step'] = next_step
        data['next_step_date'] = next_step_date
        data['payment_set-TOTAL_FORMS'] = '0'
        data['output_set-TOTAL_FORMS'] = '0'
        data['_continue'] = ''
        # submit form
        response = self.client.post(self.deal_change_url, data, follow=True)
        self.assertNoFormErrors(response)
        self.assertEqual(response.status_code, 200, response.reason_phrase)
        # The Reminder obj has been changed?
        self.assertTrue(Reminder.objects.filter(
            content_type=ContentType.objects.get_for_model(self.deal),
            object_id=self.deal.id,
            description=next_step,
            owner=self.deal.owner,
            active=True,
            reminder_date__contains=next_step_date
        ).exists())

        # test setting off "remind me" field
        data = get_adminform_initials(response)
        data['remind_me'] = False
        data['payment_set-TOTAL_FORMS'] = '0'
        data['output_set-TOTAL_FORMS'] = '0'
        # submit form
        response = self.client.post(self.deal_change_url, data, follow=True)
        self.assertNoFormErrors(response)
        self.assertEqual(response.status_code, 200, response.reason_phrase)
        self.assertEqual(
            response.redirect_chain[0][0], self.deal_changelist_url)
        # The Reminder obj has been deleted?
        self.assertFalse(Reminder.objects.filter(
            content_type=ContentType.objects.get_for_model(self.deal),
            object_id=self.deal.id,
            description=next_step,
            owner=self.deal.owner,
            active=True,
            reminder_date__contains=next_step_date
        ).exists())


def get_contact_request() -> Request:
    return Request.objects.create(
        request_for='test inquiry',
        first_name='Tom',
        email='Tom@testcompany.com',
        phone='+1234567890',
        company_name='Test Company LLC',
        description="Description",
        translation="Translated text"
    )


def get_test_deal(obj) -> Deal:
    stage = Stage.objects.filter(
        department_id=obj.department,
        default=True
    ).first()
    return Deal.objects.create(
        name=obj.contact_request.request_for,
        request=obj.contact_request,
        department_id=get_department_id(obj.owner),
        ticket=obj.contact_request.ticket,
        description=obj.contact_request.remark,
        next_step=settings.FIRST_STEP,
        next_step_date=get_delta_date(1),
        stage=stage,
        owner=obj.owner,
        co_owner=obj.co_owner,
        stages_dates='{date} - {stage}\n',
        workflow='{date} - {msg}\n',
        contact=obj.contact,
        company=obj.contact.company,
        amount=31700.00,
        country=obj.contact.company.country
    )
