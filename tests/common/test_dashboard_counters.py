"""Dashboard counter registry and characterization tests."""

from types import SimpleNamespace
from unittest.mock import patch

from django.conf import settings
from django.contrib import admin
from django.contrib.admin.models import ADDITION
from django.contrib.admin.models import LogEntry
from django.contrib.contenttypes.models import ContentType
from django.test import RequestFactory
from django.test import SimpleTestCase
from django.test import tag
from django.urls import NoReverseMatch

from common.utils.helpers import USER_MODEL
from crm.models import CrmEmail
from crm.models import Request
from sharedkernel.admin_urls import resolve_log_entry_admin_url
from sharedkernel.dashboard import _reset_registry_for_tests
from sharedkernel.dashboard import apply_dashboard_counters
from sharedkernel.dashboard import iter_counter_registrations
from sharedkernel.dashboard import register_counter
from sharedkernel.dashboard import register_help_url_provider
from sharedkernel.dashboard import resolve_help_url
from tasks.models import Memo
from tasks.models import Task
from tasks.models import TaskStage
from tests.base_test_classes import BaseTestCase


@tag('TestCase')
class DashboardRegistryUnitTests(SimpleTestCase):
    def setUp(self):
        super().setUp()
        _reset_registry_for_tests()

    def tearDown(self):
        _reset_registry_for_tests()
        super().tearDown()

    def test_registration_order_is_deterministic(self):
        register_counter('beta', 20, 'crm', lambda request, models: None)
        register_counter('alpha', 10, 'crm', lambda request, models: None)
        names = [entry.name for entry in iter_counter_registrations()]
        self.assertEqual(names, ['alpha', 'beta'])

    def test_unregistered_app_contributes_nothing(self):
        register_counter('crm_only', 10, 'crm', lambda request, models: None)
        request = SimpleNamespace(user=SimpleNamespace())
        models = [{'name': 'Companies'}]
        apply_dashboard_counters(request, 'tasks', models)
        self.assertEqual(models[0]['name'], 'Companies')

    def test_raising_provider_is_omitted(self):
        def boom(request, models):
            raise RuntimeError('counter failed')

        register_counter('broken', 10, 'crm', boom)
        request = SimpleNamespace(user=SimpleNamespace())
        models = [{'name': 'Companies'}]
        with self.assertLogs('sharedkernel.dashboard', level='ERROR'):
            apply_dashboard_counters(request, 'crm', models)
        self.assertEqual(models[0]['name'], 'Companies')

    def test_help_url_provider_can_be_registered(self):
        register_help_url_provider(lambda request: '/help/page/')
        request = SimpleNamespace()
        self.assertEqual(resolve_help_url(request), '/help/page/')


@tag('TestCase')
class CrmSiteImportOrderTests(SimpleTestCase):
    def test_crmsite_module_does_not_monkeypatch_admin_site_index(self):
        original_index = admin.AdminSite.index
        import common.site.crmsite  # noqa: F401
        self.assertIs(admin.AdminSite.index, original_index)


@tag('TestCase')
class LogEntryAdminUrlTests(BaseTestCase):
    def test_resolve_log_entry_admin_url_for_site_prefix(self):
        user = USER_MODEL.objects.get(username='Adam.Admin')
        content_type = ContentType.objects.get_for_model(Request)
        entry = LogEntry.objects.create(
            user_id=user.id,
            content_type=content_type,
            object_id='42',
            object_repr='request',
            action_flag=ADDITION,
            change_message='updated',
        )
        url = resolve_log_entry_admin_url(entry, 'site:%s_%s_change')
        self.assertIn('/crm/request/42/change/', url)

    def test_resolve_log_entry_admin_url_returns_none_on_missing_reverse(self):
        user = USER_MODEL.objects.get(username='Adam.Admin')
        content_type = ContentType.objects.get_for_model(Request)
        entry = LogEntry.objects.create(
            user_id=user.id,
            content_type=content_type,
            object_id='42',
            object_repr='request',
            action_flag=ADDITION,
            change_message='updated',
        )
        with patch('sharedkernel.admin_urls.reverse', side_effect=NoReverseMatch):
            self.assertIsNone(resolve_log_entry_admin_url(entry))


@tag('TestCase')
class DashboardCounterCharacterizationTests(BaseTestCase):
    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()
        cls.factory = RequestFactory()
        cls.superuser = USER_MODEL.objects.get(username='Adam.Admin')
        cls.chief = USER_MODEL.objects.get(username='Garry.Chief')
        cls.manager = USER_MODEL.objects.get(username='Andrew.Manager.Global')
        cls.superoperator = USER_MODEL.objects.get(username='Ekaterina.Task_operator')

    def _login_request(self, user):
        request = self.factory.get('/')
        request.user = user
        for attr in (
            'is_manager', 'is_operator', 'is_superoperator',
            'is_superuser', 'is_chief', 'department_id',
        ):
            if not hasattr(request.user, attr):
                setattr(request.user, attr, getattr(user, attr, False))
        return request

    def _model_names(self, response, app_label):
        app = next(app for app in response.context['app_list'] if app['app_label'] == app_label)
        return [model['name'] for model in app['models']]

    def test_dashboard_renders_task_and_memo_badges_for_superuser(self):
        user = self.superuser
        stage = TaskStage.objects.get(default=True)
        Task.objects.filter(responsible=user).delete()
        Memo.objects.filter(to=user).delete()
        task = Task.objects.create(
            name='Counter task',
            owner=user,
            stage=stage,
        )
        task.responsible.add(user)
        Memo.objects.create(name='Counter memo', owner=user, to=user, stage=Memo.PENDING)

        self.client.force_login(user)
        response = self.client.get(
            '/' + settings.SECRET_CRM_PREFIX,
            HTTP_ACCEPT_LANGUAGE='en',
            follow=True,
        )
        self.assertEqual(response.status_code, 200)
        task_names = self._model_names(response, 'tasks')
        self.assertTrue(any('Memos' in name and 'color: var(--error-fg)' in name for name in task_names))
        self.assertTrue(any(name.startswith('Tasks') for name in task_names))

    def test_dashboard_renders_crm_outbox_for_manager(self):
        user = self.manager
        CrmEmail.objects.filter(owner=user, sent=False, incoming=False, trash=False).delete()
        CrmEmail.objects.create(
            subject='Outbox test',
            owner=user,
            sent=False,
            incoming=False,
            trash=False,
        )
        self.client.force_login(user)
        response = self.client.get(
            '/' + settings.SECRET_CRM_PREFIX,
            HTTP_ACCEPT_LANGUAGE='en',
            follow=True,
        )
        self.assertEqual(response.status_code, 200)
        crm_names = self._model_names(response, 'crm')
        self.assertTrue(any('outbox' in name for name in crm_names))

    def test_chief_and_superoperator_dashboards_render(self):
        for user in (self.chief, self.superoperator):
            with self.subTest(username=user.username):
                self.client.force_login(user)
                response = self.client.get(
                    '/' + settings.SECRET_CRM_PREFIX,
                    HTTP_ACCEPT_LANGUAGE='en',
                    follow=True,
                )
                self.assertEqual(response.status_code, 200)
                self.assertTrue(response.context['app_list'])
