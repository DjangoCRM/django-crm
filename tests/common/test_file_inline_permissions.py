"""Characterization tests for FileInline permission behaviour."""

from types import SimpleNamespace
from unittest.mock import MagicMock
from unittest.mock import patch

from django.contrib.admin.sites import AdminSite
from django.contrib.contenttypes.models import ContentType
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import tag

from common.models import TheFile
from sharedkernel.inlines import FileInline
from tasks.models import Memo
from tests.base_test_classes import BaseTestCase


_USER_COUNTER = 0


def _user(**kwargs):
    global _USER_COUNTER
    _USER_COUNTER += 1
    defaults = {
        'username': f'user-{_USER_COUNTER}',
        'is_chief': False,
        'is_operator': False,
        'is_superoperator': False,
        'is_task_operator': False,
        'is_superuser': False,
        'department_id': 1,
    }
    defaults.update(kwargs)
    return SimpleNamespace(**defaults)


def _request(user):
    return SimpleNamespace(user=user)


@tag('TestCase')
class FileInlineClarifyPermissionTests(BaseTestCase):
    def test_object_without_owner_returns_true(self):
        obj = SimpleNamespace(name='no-owner')
        self.assertTrue(FileInline.clarify_permission(_request(_user()), obj))

    def test_owner_user_pending_stage_returns_true(self):
        user = _user()
        obj = SimpleNamespace(owner=user, stage='pen', REVIEWED='rev')
        self.assertTrue(FileInline.clarify_permission(_request(user), obj))

    def test_owner_user_reviewed_stage_returns_false(self):
        user = _user()
        obj = SimpleNamespace(owner=user, stage='rev', REVIEWED='rev')
        self.assertFalse(FileInline.clarify_permission(_request(user), obj))

    def test_owner_user_incoming_returns_false(self):
        user = _user()
        obj = SimpleNamespace(owner=user, incoming=True)
        self.assertFalse(FileInline.clarify_permission(_request(user), obj))

    def test_owner_user_with_uid_returns_false(self):
        user = _user()
        obj = SimpleNamespace(owner=user, uid='imported-uid')
        self.assertFalse(FileInline.clarify_permission(_request(user), obj))

    def test_unowned_object_chief_returns_false(self):
        user = _user(is_chief=True)
        obj = SimpleNamespace(owner=None)
        self.assertFalse(FileInline.clarify_permission(_request(user), obj))

    def test_unowned_object_non_chief_returns_true(self):
        user = _user(is_chief=False)
        obj = SimpleNamespace(owner=None)
        self.assertTrue(FileInline.clarify_permission(_request(user), obj))

    def test_other_owner_co_owner_match_returns_true(self):
        owner = _user()
        co_owner = _user()
        obj = SimpleNamespace(owner=owner, co_owner=co_owner)
        self.assertTrue(FileInline.clarify_permission(_request(co_owner), obj))

    def test_other_owner_superuser_returns_true(self):
        owner = _user()
        superuser = _user(is_superuser=True)
        obj = SimpleNamespace(owner=owner)
        self.assertTrue(FileInline.clarify_permission(_request(superuser), obj))

    def test_other_owner_superoperator_returns_true(self):
        owner = _user()
        actor = _user(is_superoperator=True)
        obj = SimpleNamespace(owner=owner)
        self.assertTrue(FileInline.clarify_permission(_request(actor), obj))

    def test_other_owner_task_operator_returns_true(self):
        owner = _user()
        actor = _user(is_task_operator=True)
        obj = SimpleNamespace(owner=owner)
        self.assertTrue(FileInline.clarify_permission(_request(actor), obj))

    def test_other_owner_operator_same_department_returns_true(self):
        owner = _user(department_id=2)
        actor = _user(is_operator=True, department_id=2)
        obj = SimpleNamespace(owner=owner, department=True, department_id=2)
        self.assertTrue(FileInline.clarify_permission(_request(actor), obj))

    def test_other_owner_operator_other_department_returns_false(self):
        owner = _user(department_id=2)
        actor = _user(is_operator=True, department_id=3)
        obj = SimpleNamespace(owner=owner, department=True, department_id=2)
        self.assertFalse(FileInline.clarify_permission(_request(actor), obj))

    def test_other_owner_single_responsible_includes_user_returns_true(self):
        owner = _user()
        actor = _user()
        responsible = MagicMock()
        responsible.count.return_value = 1
        responsible.all.return_value = [actor]
        obj = SimpleNamespace(owner=owner, responsible=responsible)
        self.assertTrue(FileInline.clarify_permission(_request(actor), obj))

    def test_other_owner_multiple_responsible_returns_false(self):
        owner = _user()
        actor = _user()

        class Responsible:
            def count(self):
                return 2

            def all(self):
                return [actor, _user()]

        obj = SimpleNamespace(owner=owner, responsible=Responsible())
        self.assertFalse(FileInline.clarify_permission(_request(actor), obj))

    def test_other_owner_win_closing_date_chief_returns_true(self):
        owner = _user()
        chief = _user(is_chief=True)
        obj = SimpleNamespace(owner=owner, win_closing_date=True)
        self.assertTrue(FileInline.clarify_permission(_request(chief), obj))

    def test_other_owner_without_role_grants_returns_false(self):
        owner = _user()
        actor = _user()
        obj = SimpleNamespace(owner=owner)
        self.assertFalse(FileInline.clarify_permission(_request(actor), obj))


@tag('TestCase')
class FileInlinePermissionMethodTests(BaseTestCase):
    def setUp(self):
        super().setUp()
        self.inline = FileInline(Memo, AdminSite())
        self.request = _request(_user())

    @patch.object(FileInline, 'clarify_permission', return_value=True)
    @patch('django.contrib.contenttypes.admin.GenericStackedInline.has_change_permission', return_value=True)
    def test_has_change_delegates_to_clarify(self, _super_change, clarify):
        obj = SimpleNamespace(owner=self.request.user)
        self.assertTrue(self.inline.has_change_permission(self.request, obj))
        clarify.assert_called_once_with(self.request, obj)

    @patch.object(FileInline, 'clarify_permission', return_value=False)
    @patch('django.contrib.contenttypes.admin.GenericStackedInline.has_change_permission', return_value=True)
    def test_has_delete_follows_change_permission(self, _super_change, _clarify):
        obj = SimpleNamespace(owner=self.request.user)
        self.assertFalse(self.inline.has_delete_permission(self.request, obj))

    @patch.object(FileInline, 'has_change_permission', return_value=False)
    def test_unreviewed_memo_recipient_can_add_without_change(self, _change):
        recipient = _user()
        owner = _user()
        obj = SimpleNamespace(
            owner=owner,
            to=recipient,
            stage=Memo.PENDING,
            REVIEWED=Memo.REVIEWED,
        )
        self.assertTrue(self.inline.has_add_permission(_request(recipient), obj))


@tag('TestCase')
class FileInlineMetadataTests(BaseTestCase):
    def test_verbose_name_plural_includes_icon(self):
        icon = FileInline.icon
        name_plural = FileInline.model._meta.verbose_name_plural
        self.assertEqual(str(FileInline.verbose_name_plural), f'{icon} {name_plural}')

    def test_extra_and_fields_unchanged(self):
        self.assertEqual(FileInline.extra, 0)
        self.assertEqual(FileInline.fields, ('file',))


@tag('TestCase')
class FileInlineAdminIntegrationTests(BaseTestCase):
    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()
        from common.utils.helpers import USER_MODEL
        cls.staff_user = USER_MODEL.objects.get(username='Adam.Admin')
        memo = Memo.objects.create(
            name='Attachment memo',
            to=cls.staff_user,
            owner=cls.staff_user,
            stage=Memo.PENDING,
        )
        content_type = ContentType.objects.get_for_model(Memo)
        TheFile.objects.create(
            content_type=content_type,
            object_id=memo.id,
            file=SimpleUploadedFile('memo.txt', b'memo attachment'),
        )

    def test_deal_admin_includes_file_inline(self):
        from crm.site.dealadmin import DealAdmin
        from crm.models import Deal

        self.assertIn(FileInline, DealAdmin.inlines)

    def test_task_admin_includes_file_inline(self):
        from tasks.site.tasksbasemodeladmin import TasksBaseModelAdmin

        self.assertIn(FileInline, TasksBaseModelAdmin.inlines)

    def test_memo_admin_includes_file_inline(self):
        from tasks.site.memoadmin import MemoAdmin

        self.assertIn(FileInline, MemoAdmin.inlines)

    def test_request_admin_includes_file_inline(self):
        from crm.site.requestadmin import RequestAdmin

        self.assertIn(FileInline, RequestAdmin.inlines)
