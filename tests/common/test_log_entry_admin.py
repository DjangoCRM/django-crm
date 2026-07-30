"""Tests for LogEntryAdmin and related admin utilities.

LogEntry search parity contract
-------------------------------
The ``LogEntrySearchParityTests`` class captures the current behaviour of
``LogEntryAdmin.get_search_results`` against a committed fixture corpus.
These assertions are a **parity contract** for the planned database-side
rewrite and must **not** be relaxed or modified when the implementation is
replaced; only an intentional corpus revision may change expected primary keys.
"""

from common.site.crmsite import get_url
from django.urls import NoReverseMatch
from django.test import TestCase
from unittest.mock import Mock
from unittest.mock import patch
from django.contrib import admin
from django.contrib.admin.sites import AdminSite
from django.contrib.contenttypes.models import ContentType
from django.conf import settings
from django.test import RequestFactory
from django.test import tag

from common.admin import LogEntryAdmin
from common.utils.helpers import USER_MODEL
from tests.base_test_classes import BaseTestCase
from tests.common.log_entry_parity import assert_search_parity
from tests.common.log_entry_parity import capture_search_pks
from tests.common.log_entry_parity_seed import PARITY_LOG_ENTRY_PKS

# manage.py test tests.common.test_log_entry_admin --keepdb


@tag('TestCase')
class TestLogEntryAdmin(BaseTestCase):
    """Test LogEntryAdmin.get_search_results method"""

    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()
        cls.user = USER_MODEL.objects.first()
        cls.content_type = ContentType.objects.get_for_model(USER_MODEL)

    def setUp(self):
        print("Run Test Method:", self._testMethodName)
        self.model_admin = LogEntryAdmin(admin.models.LogEntry, AdminSite())
        self.factory = RequestFactory()

    def test_get_search_results_with_id_prefix_uppercase(self):
        """Test searching with 'ID123' format returns matching object."""
        request = self.factory.get('/')
        queryset = admin.models.LogEntry.objects.all()
        
        # Create a log entry to search for
        log_entry = admin.models.LogEntry.objects.create(
            user=self.user,
            content_type=self.content_type,
            object_id='42',
            action_flag=admin.models.CHANGE,
        )
        
        results, use_distinct = self.model_admin.get_search_results(
            request, queryset, f'ID{log_entry.id}'
        )
        
        self.assertTrue(use_distinct)
        self.assertIn(log_entry, results)

    def test_get_search_results_with_id_prefix_lowercase(self):
        """Test searching with 'id123' format returns matching object."""
        request = self.factory.get('/')
        queryset = admin.models.LogEntry.objects.all()
        
        log_entry = admin.models.LogEntry.objects.create(
            user=self.user,
            content_type=self.content_type,
            object_id='99',
            action_flag=admin.models.ADDITION,
        )
        
        results, use_distinct = self.model_admin.get_search_results(
            request, queryset, f'id{log_entry.id}'
        )
        
        self.assertTrue(use_distinct)
        self.assertIn(log_entry, results)

    def test_get_search_results_with_object_id(self):
        """Test searching with 'ID' prefix returns entries by object_id."""
        request = self.factory.get('/')
        queryset = admin.models.LogEntry.objects.all()
        
        object_id = '12345'
        log_entry = admin.models.LogEntry.objects.create(
            user=self.user,
            content_type=self.content_type,
            object_id=object_id,
            action_flag=admin.models.DELETION,
        )
        
        results, use_distinct = self.model_admin.get_search_results(
            request, queryset, f'ID{object_id}'
        )
        
        self.assertTrue(use_distinct)
        self.assertIn(log_entry, results)

    def test_get_search_results_with_change_message(self):
        """Test searching by change_message content."""
        request = self.factory.get('/')
        
        log_entry = admin.models.LogEntry.objects.create(
            user=self.user,
            content_type=self.content_type,
            object_id='1',
            action_flag=admin.models.CHANGE,
            change_message='Updated the email field',
        )
        queryset = admin.models.LogEntry.objects.filter(id=log_entry.id)
        
        results, use_distinct = self.model_admin.get_search_results(
            request, queryset, 'email'
        )
        
        self.assertTrue(use_distinct)
        self.assertIn(log_entry, results)

    def test_get_search_results_empty_term(self):
        """Test that empty search term calls parent method."""
        request = self.factory.get('/')
        queryset = admin.models.LogEntry.objects.all()
        
        with patch.object(
            admin.ModelAdmin,
            'get_search_results',
            return_value=(queryset, False)
        ) as mock_parent:
            results, use_distinct = self.model_admin.get_search_results(
                request, queryset, ''
            )
            mock_parent.assert_called_once_with(request, queryset, '')

    def test_get_search_results_no_match_in_change_message(self):
        """Test that non-matching change_message returns empty results."""
        request = self.factory.get('/')
        
        log_entry = admin.models.LogEntry.objects.create(
            user=self.user,
            content_type=self.content_type,
            object_id='1',
            action_flag=admin.models.CHANGE,
            change_message='Updated the name field',
        )
        queryset = admin.models.LogEntry.objects.filter(id=log_entry.id)
        
        results, use_distinct = self.model_admin.get_search_results(
            request, queryset, 'nonexistent_text'
        )
        
        self.assertTrue(use_distinct)
        self.assertEqual(list(results), [])


@tag('TestCase')
class LogEntrySearchParityTests(BaseTestCase):
    """Characterization harness for LogEntryAdmin.get_search_results."""

    fixtures = BaseTestCase.fixtures + ('log_entries_parity.json',)

    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()
        admin.models.LogEntry.objects.exclude(
            pk__in=PARITY_LOG_ENTRY_PKS,
        ).delete()
        cls.staff_user = USER_MODEL.objects.get(username='Adam.Admin')

    def setUp(self):
        self.model_admin = LogEntryAdmin(admin.models.LogEntry, AdminSite())
        self.factory = RequestFactory()

    def test_parity_object_repr_term_currently_matches_via_change_message_only(self):
        """Corpus row 9001: object_repr text is not searched today (expect no hits)."""
        request = self.factory.get('/')
        assert_search_parity(self, self.model_admin, request, 'Acme', [], True)

    def test_parity_json_change_message(self):
        request = self.factory.get('/')
        assert_search_parity(self, self.model_admin, request, 'Email', [9002], True)

    def test_parity_legacy_change_message(self):
        request = self.factory.get('/')
        assert_search_parity(self, self.model_admin, request, 'phone', [9003], True)

    def test_parity_id_prefix_branch(self):
        request = self.factory.get('/')
        assert_search_parity(self, self.model_admin, request, 'ID9009', [9009], True)

    def test_parity_multi_word_term(self):
        request = self.factory.get('/')
        assert_search_parity(
            self,
            self.model_admin,
            request,
            'North Region',
            [9008],
            True,
        )

    def test_parity_empty_search_term(self):
        request = self.factory.get('/')
        pks, may_have_duplicates = capture_search_pks(
            self.model_admin,
            request,
            '',
        )
        self.assertEqual(pks, sorted(PARITY_LOG_ENTRY_PKS))
        self.assertFalse(may_have_duplicates)

    def test_parity_no_match(self):
        request = self.factory.get('/')
        assert_search_parity(
            self,
            self.model_admin,
            request,
            'xyzzy_nonexistent',
            [],
            True,
        )

    def test_parity_sql_wildcard_characters_in_term(self):
        request = self.factory.get('/')
        assert_search_parity(self, self.model_admin, request, '100%', [9006], True)
        assert_search_parity(self, self.model_admin, request, 'field_name', [9007], True)

    def test_parity_unicode_and_accented_terms(self):
        request = self.factory.get('/')
        assert_search_parity(self, self.model_admin, request, 'café', [9005, 9012], True)
        assert_search_parity(self, self.model_admin, request, 'naïve', [9005, 9012], True)

    def test_parity_json_field_label_substring(self):
        request = self.factory.get('/')
        assert_search_parity(
            self,
            self.model_admin,
            request,
            'billing address',
            [9011],
            True,
        )

    def test_parity_admin_changelist_result_count(self):
        changelist_url = (
            f'/{settings.SECRET_ADMIN_PREFIX}admin/logentry/'
        )
        self.client.force_login(self.staff_user)
        expected_pks, _ = capture_search_pks(
            self.model_admin,
            self.factory.get('/'),
            'Email',
        )
        response = self.client.get(
            changelist_url,
            data={'q': 'Email'},
            HTTP_ACCEPT_LANGUAGE='en',
            follow=True,
        )
        self.assertEqual(response.status_code, 200)
        result_list = response.context['cl'].result_list
        rendered_pks = sorted(entry.pk for entry in result_list)
        self.assertEqual(rendered_pks, expected_pks)


class GetUrlTestCase(TestCase):
    """Tests for get_url function"""

    def test_get_url_with_valid_content_type_and_object_id(self):
        """Test get_admin_url returns correct URL when content_type and object_id exist"""
        get_admin_url = get_url('admin:%s_%s_change')

        log_entry = Mock()
        log_entry.content_type.app_label = 'crm'
        log_entry.content_type.model = 'request'
        log_entry.object_id = '123'

        with patch('common.site.crmsite.reverse', return_value='/admin/crm/request/123/change/'):
            result = get_admin_url(log_entry)
            self.assertEqual(result, '/admin/crm/request/123/change/')

    def test_get_url_with_no_content_type(self):
        """Test get_admin_url returns None when content_type is None"""
        get_admin_url = get_url('admin:%s_%s_change')

        log_entry = Mock()
        log_entry.content_type = None
        log_entry.object_id = '123'

        result = get_admin_url(log_entry)
        self.assertIsNone(result)

    def test_get_url_with_no_object_id(self):
        """Test get_admin_url returns None when object_id is None"""
        get_admin_url = get_url('admin:%s_%s_change')

        log_entry = Mock()
        log_entry.content_type = Mock()
        log_entry.object_id = None

        result = get_admin_url(log_entry)
        self.assertIsNone(result)

    def test_get_url_with_no_reverse_match(self):
        """Test get_admin_url returns None when NoReverseMatch is raised"""
        get_admin_url = get_url('admin:%s_%s_change')

        log_entry = Mock()
        log_entry.content_type.app_label = 'crm'
        log_entry.content_type.model = 'request'
        log_entry.object_id = '123'

        with patch('common.site.crmsite.reverse', side_effect=NoReverseMatch):
            result = get_admin_url(log_entry)
            self.assertIsNone(result)

    def test_get_url_different_name_format(self):
        """Test get_admin_url with different URL name format"""
        get_admin_url = get_url('site:%s_%s_change')

        log_entry = Mock()
        log_entry.content_type.app_label = 'tasks'
        log_entry.content_type.model = 'task'
        log_entry.object_id = '456'

        with patch('common.site.crmsite.reverse', return_value='/site/tasks/task/456/change/'):
            result = get_admin_url(log_entry)
            self.assertEqual(result, '/site/tasks/task/456/change/')
