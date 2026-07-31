"""Characterization and unit tests for BaseModelAdmin raw-id label hook."""

from django.contrib import admin
from django.test import RequestFactory
from django.test import tag

from common.site.basemodeladmin import BaseModelAdmin
from crm.models import Contact
from crm.models import Deal
from crm.site.contactadmin import ContactAdmin
from crm.site.crmadminsite import crm_site
from crm.site.crmmodeladmin import CrmModelAdmin
from crm.site.dealadmin import DealAdmin
from crm.utils.helpers import add_id_to_raw_id_field_label
from massmail.models import MailingOut
from massmail.site.mailingoutadmin import MailingOutAdmin
from sharedkernel.admin_labels import append_id_to_raw_id_field_labels
from sharedkernel.admin_labels import noop_raw_id_label_decorator
from tasks.models import Memo
from tasks.models import Task
from tasks.site.memoadmin import MemoAdmin
from tasks.site.taskadmin import TaskAdmin
from tasks.site.tasksbasemodeladmin import TasksBaseModelAdmin
from tests.base_test_classes import BaseTestCase
from common.utils.helpers import USER_MODEL


def _raw_id_labels(model_admin, request, obj=None):
    form = model_admin.get_form(request, obj=obj)
    return {
        field: str(form.base_fields[field].label)
        for field in model_admin.raw_id_fields
        if field in form.base_fields
    }


@tag('TestCase')
class RawIdLabelHookUnitTests(BaseTestCase):
    def test_default_hook_is_noop(self):
        self.assertIs(BaseModelAdmin.raw_id_label_decorator, noop_raw_id_label_decorator)

    def test_crm_model_admin_overrides_hook(self):
        self.assertIs(CrmModelAdmin.raw_id_label_decorator, add_id_to_raw_id_field_label)

    def test_subclass_inherits_crm_hook(self):
        self.assertIs(DealAdmin.raw_id_label_decorator, add_id_to_raw_id_field_label)

    def test_tasks_base_model_admin_uses_shared_decorator(self):
        self.assertIs(
            TasksBaseModelAdmin.raw_id_label_decorator,
            append_id_to_raw_id_field_labels,
        )
        self.assertIs(MemoAdmin.raw_id_label_decorator, append_id_to_raw_id_field_labels)

    def test_noop_hook_leaves_labels_unchanged(self):
        from django import forms

        class SampleForm(forms.Form):
            owner = forms.CharField(label='Owner')

        form = SampleForm()
        noop_raw_id_label_decorator(
            type('Admin', (), {'raw_id_fields': ('owner',)})(),
            form,
        )
        self.assertEqual(form.fields['owner'].label, 'Owner')


@tag('TestCase')
class RawIdLabelCharacterizationTests(BaseTestCase):
    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()
        cls.user = USER_MODEL.objects.get(username='Adam.Admin')
        cls.factory = RequestFactory()

    def _request(self):
        request = self.factory.get('/')
        request.user = self.user
        request.user.is_superuser = True
        request.user.is_superoperator = True
        request.user.is_chief = True
        request.user.is_task_operator = True
        request.user.is_operator = True
        request.user.department_id = self.user.groups.first().id
        return request

    def test_deal_admin_appends_id_suffix(self):
        deal = Deal.objects.first()
        if deal is None:
            self.skipTest('Deal fixtures unavailable')
        labels = _raw_id_labels(DealAdmin(Deal, crm_site), self._request(), deal)
        self.assertTrue(labels)
        for label in labels.values():
            self.assertTrue(label.endswith(', ID'), msg=label)

    def test_contact_admin_appends_id_suffix(self):
        contact = Contact.objects.first()
        if contact is None:
            self.skipTest('Contact fixtures unavailable')
        labels = _raw_id_labels(
            ContactAdmin(Contact, crm_site),
            self._request(),
            contact,
        )
        self.assertTrue(labels)
        for label in labels.values():
            self.assertTrue(label.endswith(', ID'), msg=label)

    def test_task_admin_appends_id_suffix(self):
        task = Task.objects.first()
        if task is None:
            self.skipTest('Task fixtures unavailable')
        labels = _raw_id_labels(TaskAdmin(Task, admin.site), self._request(), task)
        self.assertTrue(labels)
        for label in labels.values():
            self.assertTrue(label.endswith(', ID'), msg=label)

    def test_memo_admin_appends_id_suffix(self):
        memo = Memo.objects.first()
        if memo is None:
            memo = Memo.objects.create(
                name='Label test memo',
                to=self.user,
                owner=self.user,
            )
        labels = _raw_id_labels(MemoAdmin(Memo, admin.site), self._request(), memo)
        self.assertTrue(labels)
        for label in labels.values():
            self.assertTrue(label.endswith(', ID'), msg=label)

    def test_mailing_out_admin_appends_id_suffix(self):
        mailing_out = MailingOut.objects.first()
        if mailing_out is None:
            self.skipTest('MailingOut fixtures unavailable')
        labels = _raw_id_labels(
            MailingOutAdmin(MailingOut, admin.site),
            self._request(),
            mailing_out,
        )
        self.assertIn('message', labels)
        self.assertTrue(labels['message'].endswith(', ID'))

    def test_shared_and_crm_decorators_behave_identically(self):
        from django import forms

        class SampleForm(forms.Form):
            company = forms.CharField(label='Company')
            contact = forms.CharField(label='Contact')

        admin_obj = type('Admin', (), {'raw_id_fields': ('company', 'contact')})()
        crm_form = SampleForm()
        shared_form = SampleForm()
        add_id_to_raw_id_field_label(admin_obj, crm_form)
        append_id_to_raw_id_field_labels(admin_obj, shared_form)
        self.assertEqual(
            {name: field.label for name, field in crm_form.fields.items()},
            {name: field.label for name, field in shared_form.fields.items()},
        )
