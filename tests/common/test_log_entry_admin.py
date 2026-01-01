from common.site.crmsite import get_url
from django.urls import NoReverseMatch
from django.test import TestCase
from unittest.mock import Mock
from unittest.mock import patch
from django.contrib import admin
from django.contrib.admin.sites import AdminSite
from django.contrib.contenttypes.models import ContentType
from django.test import RequestFactory
from django.test import tag

from common.admin import LogEntryAdmin
from common.utils.helpers import USER_MODEL
from tests.base_test_classes import BaseTestCase

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
