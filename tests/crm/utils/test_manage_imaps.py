"""
Unit tests for CrmImapManager class using mocks.

Tests the creation, management, and lifecycle of CrmIMAP objects
for handling IMAP email account connections.
"""
import os
import queue
import threading
from datetime import datetime as dt
from datetime import timedelta
from unittest.mock import MagicMock, patch, PropertyMock

from django.test import override_settings, tag

from crm.utils.manage_imaps import CrmImapManager, delta_period
from crm.settings import IMAP_NOOP_PERIOD
from massmail.models import EmailAccount
from tests.base_test_classes import BaseTestCase


# manage.py test tests.crm.utils.test_manage_imaps --keepdb


@tag('TestCase')
class TestCrmImapManagerInitialization(BaseTestCase):
    """Test CrmImapManager initialization."""

    def setUp(self):
        print(" Run Test Method:", self._testMethodName)

    def test_initialization(self):
        """Test that manager initializes with correct attributes."""
        ea_queue = queue.Queue()
        manager = CrmImapManager(ea_queue)

        self.assertEqual(manager.boxes_storage, {})
        self.assertEqual(manager.crmimap_storage, {})
        self.assertEqual(manager.close, False)
        self.assertIs(manager.ea_queue, ea_queue)
        self.assertTrue(manager.daemon)

    def test_manager_is_thread(self):
        """Test that manager is a Thread subclass."""
        ea_queue = queue.Queue()
        manager = CrmImapManager(ea_queue)

        self.assertIsInstance(manager, threading.Thread)


@tag('TestCase')
class TestCrmImapManagerCreateCrmImap(BaseTestCase):
    """Test CrmImapManager._create_crmimap method."""

    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()
        from common.utils.helpers import USER_MODEL
        
        user, _ = USER_MODEL.objects.get_or_create(
            username="test_owner_create",
            defaults={'email': 'test_owner_create@test.com'}
        )
        cls.owner = user

    def setUp(self):
        print(" Run Test Method:", self._testMethodName)

        self.ea_queue = queue.Queue()
        self.manager = CrmImapManager(self.ea_queue)
        self.email_account = EmailAccount.objects.create(
            name='Test Email Account',
            email_host='imap.example.com',
            email_port=993,
            email_host_user='test@example.com',
            email_host_password='password',
            from_email='test@example.com',
            main=True,
            owner=self.owner,
        )

    @patch('crm.utils.manage_imaps.CrmIMAP')
    @override_settings(REUSE_IMAP_CONNECTION=True)
    def test_create_crmimap_stores_in_storage(self, mock_crmimap_class):
        """Test that _create_crmimap stores the object in storage."""
        mock_crmimap = MagicMock()
        mock_crmimap.email_host_user = self.email_account.email_host_user
        mock_crmimap.error = False
        mock_crmimap.boxes = {'INBOX': {'name on server': 'INBOX'}}
        mock_crmimap.last_request_time = dt.now()
        mock_crmimap_class.return_value = mock_crmimap

        result = self.manager._create_crmimap(self.email_account)

        self.assertIs(result, mock_crmimap)
        self.assertIn(self.email_account.email_host_user, 
                      self.manager.crmimap_storage)
        self.assertEqual(
            self.manager.crmimap_storage[self.email_account.email_host_user],
            mock_crmimap
        )

    @patch('crm.utils.manage_imaps.CrmIMAP')
    @override_settings(REUSE_IMAP_CONNECTION=True)
    def test_create_crmimap_calls_get_in(self, mock_crmimap_class):
        """Test that _create_crmimap calls get_in on CrmIMAP."""
        mock_crmimap = MagicMock()
        mock_crmimap.email_host_user = self.email_account.email_host_user
        mock_crmimap.error = False
        mock_crmimap.boxes = {'INBOX': {'name on server': 'INBOX'}}
        mock_crmimap_class.return_value = mock_crmimap

        self.manager._create_crmimap(self.email_account)

        mock_crmimap.get_in.assert_called_once_with(None, self.email_account)

    @patch('crm.utils.manage_imaps.CrmIMAP')
    @override_settings(REUSE_IMAP_CONNECTION=True)
    def test_create_crmimap_stores_boxes(self, mock_crmimap_class):
        """Test that _create_crmimap stores boxes in boxes_storage."""
        mock_crmimap = MagicMock()
        mock_crmimap.email_host_user = self.email_account.email_host_user
        mock_crmimap.error = False
        mock_crmimap.boxes = {'INBOX': {}, 'SENT': {}}
        mock_crmimap_class.return_value = mock_crmimap

        self.manager._create_crmimap(self.email_account)

        self.assertIn(self.email_account.email_host_user, 
                      self.manager.boxes_storage)
        self.assertEqual(self.manager.boxes_storage[self.email_account.email_host_user],
                         mock_crmimap.boxes)

    @patch('crm.utils.manage_imaps.CrmIMAP')
    @override_settings(REUSE_IMAP_CONNECTION=False)
    def test_create_crmimap_without_reuse_connection(self, mock_crmimap_class):
        """Test _create_crmimap when REUSE_IMAP_CONNECTION is False."""
        mock_crmimap = MagicMock()
        mock_crmimap.email_host_user = self.email_account.email_host_user
        mock_crmimap.error = False
        mock_crmimap_class.return_value = mock_crmimap

        result = self.manager._create_crmimap(self.email_account)

        # Should not store in storage when REUSE_IMAP_CONNECTION is False
        self.assertNotIn(self.email_account.email_host_user, 
                         self.manager.crmimap_storage)
        self.assertIsNotNone(result)

    @patch('crm.utils.manage_imaps.CrmIMAP')
    @override_settings(REUSE_IMAP_CONNECTION=True)
    def test_create_crmimap_with_error(self, mock_crmimap_class):
        """Test _create_crmimap when CrmIMAP has an error."""
        mock_crmimap = MagicMock()
        mock_crmimap.email_host_user = self.email_account.email_host_user
        mock_crmimap.error = True
        mock_crmimap_class.return_value = mock_crmimap

        result = self.manager._create_crmimap(self.email_account)

        # Should still return the object even with error
        self.assertIs(result, mock_crmimap)


@tag('TestCase')
class TestCrmImapManagerDelCrmImap(BaseTestCase):
    """Test CrmImapManager._del_crmimap method."""

    def setUp(self):
        print(" Run Test Method:", self._testMethodName)

        self.ea_queue = queue.Queue()
        self.manager = CrmImapManager(self.ea_queue)

    def test_del_crmimap_removes_from_storage(self):
        """Test that _del_crmimap removes object from storage."""
        mock_crmimap = MagicMock()
        mock_crmimap.email_host_user = 'test@example.com'
        self.manager.crmimap_storage['test@example.com'] = mock_crmimap

        self.manager._del_crmimap(mock_crmimap)

        self.assertNotIn('test@example.com', self.manager.crmimap_storage)

    def test_del_crmimap_closes_connection(self):
        """Test that _del_crmimap calls close_and_logout."""
        mock_crmimap = MagicMock()
        mock_crmimap.email_host_user = 'test@example.com'
        self.manager.crmimap_storage['test@example.com'] = mock_crmimap

        self.manager._del_crmimap(mock_crmimap)

        mock_crmimap.close_and_logout.assert_called_once()


@tag('TestCase')
class TestCrmImapManagerGetCrmImap(BaseTestCase):
    """Test CrmImapManager._get_crmimap method."""

    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()
        from common.utils.helpers import USER_MODEL
        
        user, _ = USER_MODEL.objects.get_or_create(
            username="test_owner_get",
            defaults={'email': 'test_owner_get@test.com'}
        )
        cls.owner = user

    def setUp(self):
        print(" Run Test Method:", self._testMethodName)

        self.ea_queue = queue.Queue()
        self.manager = CrmImapManager(self.ea_queue)
        self.email_account = EmailAccount.objects.create(
            name='Test Email Account',
            email_host='imap.example.com',
            email_port=993,
            email_host_user='test@example.com',
            email_host_password='password',
            from_email='test@example.com',
            main=True,
            owner=self.owner,
        )

    @override_settings(REUSE_IMAP_CONNECTION=False)
    def test_get_crmimap_returns_none_without_reuse(self):
        """Test _get_crmimap returns None when REUSE_IMAP_CONNECTION is False."""
        result = self.manager._get_crmimap(self.email_account)

        self.assertIsNone(result)

    @override_settings(REUSE_IMAP_CONNECTION=True)
    def test_get_crmimap_returns_none_when_not_in_storage(self):
        """Test _get_crmimap returns None when object not in storage."""
        result = self.manager._get_crmimap(self.email_account)

        self.assertIsNone(result)

    @override_settings(REUSE_IMAP_CONNECTION=True)
    def test_get_crmimap_locks_and_validates(self):
        """Test _get_crmimap locks object and validates connection."""
        mock_crmimap = MagicMock()
        mock_crmimap.email_host_user = self.email_account.email_host_user
        mock_crmimap.error = False
        mock_crmimap.noop.return_value = 'OK'
        mock_crmimap.last_request_time = dt.now()
        self.manager.crmimap_storage[self.email_account.email_host_user] = mock_crmimap

        result = self.manager._get_crmimap(self.email_account)

        mock_crmimap.lock.assert_called_once()
        mock_crmimap.noop.assert_called_once()
        self.assertIs(result, mock_crmimap)

    @override_settings(REUSE_IMAP_CONNECTION=True)
    def test_get_crmimap_deletes_on_noop_failure(self):
        """Test _get_crmimap deletes object when noop fails."""
        mock_crmimap = MagicMock()
        mock_crmimap.email_host_user = self.email_account.email_host_user
        mock_crmimap.error = False
        mock_crmimap.noop.return_value = 'NO'
        mock_crmimap.last_request_time = dt.now()
        self.manager.crmimap_storage[self.email_account.email_host_user] = mock_crmimap

        with patch.object(self.manager, '_del_crmimap') as mock_del:
            result = self.manager._get_crmimap(self.email_account)

            mock_del.assert_called_once_with(mock_crmimap)
            self.assertIsNone(result)

    @override_settings(REUSE_IMAP_CONNECTION=True)
    def test_get_crmimap_deletes_on_error(self):
        """Test _get_crmimap deletes object when error flag is set."""
        mock_crmimap = MagicMock()
        mock_crmimap.email_host_user = self.email_account.email_host_user
        mock_crmimap.error = True
        mock_crmimap.last_request_time = dt.now()
        self.manager.crmimap_storage[self.email_account.email_host_user] = mock_crmimap

        with patch.object(self.manager, '_del_crmimap') as mock_del:
            result = self.manager._get_crmimap(self.email_account)

            mock_del.assert_called_once_with(mock_crmimap)
            self.assertIsNone(result)


@tag('TestCase')
class TestCrmImapManagerGetOrCreateCrmImap(BaseTestCase):
    """Test CrmImapManager._get_or_create_crmimap method."""

    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()
        from common.utils.helpers import USER_MODEL
        
        user, _ = USER_MODEL.objects.get_or_create(
            username="test_owner_get_or_create",
            defaults={'email': 'test_owner_get_or_create@test.com'}
        )
        cls.owner = user

    def setUp(self):
        print(" Run Test Method:", self._testMethodName)

        self.ea_queue = queue.Queue()
        self.manager = CrmImapManager(self.ea_queue)
        self.email_account = EmailAccount.objects.create(
            name='Test Email Account',
            email_host='imap.example.com',
            email_port=993,
            email_host_user='test@example.com',
            email_host_password='password',
            from_email='test@example.com',
            main=True,
            owner=self.owner,
        )

    def test_get_or_create_crmimap_gets_existing(self):
        """Test _get_or_create_crmimap returns existing object."""
        mock_crmimap = MagicMock()
        mock_crmimap.email_host_user = self.email_account.email_host_user
        mock_crmimap.error = False

        with patch.object(self.manager, '_get_crmimap', return_value=mock_crmimap):
            result = self.manager._get_or_create_crmimap(self.email_account, None)

            self.assertIs(result, mock_crmimap)

    def test_get_or_create_crmimap_creates_new(self):
        """Test _get_or_create_crmimap creates new object when none exists."""
        mock_crmimap = MagicMock()
        mock_crmimap.email_host_user = self.email_account.email_host_user
        mock_crmimap.error = False

        with patch.object(self.manager, '_get_crmimap', return_value=None):
            with patch.object(self.manager, '_create_crmimap', 
                            return_value=mock_crmimap):
                result = self.manager._get_or_create_crmimap(self.email_account, None)

                self.assertIs(result, mock_crmimap)

    def test_get_or_create_crmimap_selects_box(self):
        """Test _get_or_create_crmimap selects box when provided."""
        mock_crmimap = MagicMock()
        mock_crmimap.email_host_user = self.email_account.email_host_user
        mock_crmimap.error = False

        with patch.object(self.manager, '_get_crmimap', return_value=mock_crmimap):
            self.manager._get_or_create_crmimap(self.email_account, 'INBOX')

            mock_crmimap.select_box.assert_called_once_with('INBOX')

    def test_get_or_create_crmimap_no_select_when_error(self):
        """Test _get_or_create_crmimap doesn't select box when error exists."""
        mock_crmimap = MagicMock()
        mock_crmimap.email_host_user = self.email_account.email_host_user
        mock_crmimap.error = True

        with patch.object(self.manager, '_get_crmimap', return_value=mock_crmimap):
            self.manager._get_or_create_crmimap(self.email_account, 'INBOX')

            mock_crmimap.select_box.assert_not_called()

    def test_get_or_create_crmimap_no_select_when_none(self):
        """Test _get_or_create_crmimap doesn't select box when None returned."""
        with patch.object(self.manager, '_get_crmimap', return_value=None):
            with patch.object(self.manager, '_create_crmimap', return_value=None):
                result = self.manager._get_or_create_crmimap(self.email_account, 'INBOX')

                self.assertIsNone(result)


@tag('TestCase')
class TestCrmImapManagerGetCrmImapPublic(BaseTestCase):
    """Test CrmImapManager.get_crmimap public method."""

    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()
        from common.utils.helpers import USER_MODEL
        
        user, _ = USER_MODEL.objects.get_or_create(
            username="test_owner_public",
            defaults={'email': 'test_owner_public@test.com'}
        )
        cls.owner = user

    def setUp(self):
        print(" Run Test Method:", self._testMethodName)

        self.ea_queue = queue.Queue()
        self.manager = CrmImapManager(self.ea_queue)
        self.email_account = EmailAccount.objects.create(
            name='Test Email Account',
            email_host='imap.example.com',
            email_port=993,
            email_host_user='test@example.com',
            email_host_password='password',
            from_email='test@example.com',
            main=True,
            owner=self.owner,
        )

    @override_settings(TESTING=True)
    def test_get_crmimap_returns_none_when_testing(self):
        """Test get_crmimap returns None when TESTING is True."""
        result = self.manager.get_crmimap(self.email_account, 'INBOX')

        self.assertIsNone(result)

    @override_settings(TESTING=False)
    def test_get_crmimap_calls_get_or_create(self):
        """Test get_crmimap calls _get_or_create_crmimap when not testing."""
        mock_crmimap = MagicMock()

        with patch.object(self.manager, '_get_or_create_crmimap', 
                         return_value=mock_crmimap):
            result = self.manager.get_crmimap(self.email_account, 'INBOX')

            self.assertIs(result, mock_crmimap)
            self.manager._get_or_create_crmimap.assert_called_once_with(
                self.email_account, 'INBOX'
            )


@tag('TestCase')
class TestCrmImapManagerSaveCrmImap(BaseTestCase):
    """Test CrmImapManager._serve_crmimap method."""

    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()
        from common.utils.helpers import USER_MODEL
        
        user, _ = USER_MODEL.objects.get_or_create(
            username="test_owner_serve",
            defaults={'email': 'test_owner_serve@test.com'}
        )
        cls.owner = user

    def setUp(self):
        print(" Run Test Method:", self._testMethodName)

        self.ea_queue = queue.Queue()
        self.manager = CrmImapManager(self.ea_queue)
        self.email_account = EmailAccount.objects.create(
            name='Test Email Account',
            email_host='imap.example.com',
            email_port=993,
            email_host_user='test@example.com',
            email_host_password='password',
            from_email='test@example.com',
            main=True,
            owner=self.owner,
        )

    def test_serve_crmimap_noop_success(self):
        """Test _serve_crmimap executes noop and adds to queue."""
        mock_crmimap = MagicMock()
        mock_crmimap.email_host_user = 'test@example.com'
        mock_crmimap.last_request_time = dt.now() - timedelta(seconds=60)
        mock_crmimap.noop_time = None
        mock_crmimap.noop.return_value = 'OK'
        mock_crmimap.ea = self.email_account

        self.manager.crmimap_storage['test@example.com'] = mock_crmimap

        self.manager._serve_crmimap('test@example.com')

        mock_crmimap.noop.assert_called_once()
        mock_crmimap.release.assert_called_once()
        self.assertEqual(self.ea_queue.qsize(), 1)

    def test_serve_crmimap_noop_failure_recreates(self):
        """Test _serve_crmimap recreates connection on noop failure."""
        mock_crmimap = MagicMock()
        mock_crmimap.email_host_user = 'test@example.com'
        mock_crmimap.last_request_time = dt.now() - timedelta(seconds=60)
        mock_crmimap.noop_time = None
        mock_crmimap.noop.return_value = 'NO'
        mock_crmimap.ea = self.email_account

        self.manager.crmimap_storage['test@example.com'] = mock_crmimap

        mock_new_crmimap = MagicMock()
        with patch.object(self.manager, '_del_crmimap'):
            with patch.object(self.manager, '_create_crmimap', 
                            return_value=mock_new_crmimap):
                self.manager._serve_crmimap('test@example.com')

                self.manager._del_crmimap.assert_called_once()
                self.manager._create_crmimap.assert_called_once()

    def test_serve_crmimap_no_noop_within_delta_period(self):
        """Test _serve_crmimap doesn't execute noop within delta_period."""
        mock_crmimap = MagicMock()
        mock_crmimap.email_host_user = 'test@example.com'
        mock_crmimap.last_request_time = dt.now()
        mock_crmimap.noop_time = None
        mock_crmimap.ea = self.email_account

        self.manager.crmimap_storage['test@example.com'] = mock_crmimap

        self.manager._serve_crmimap('test@example.com')

        # noop should not be called since not enough time has passed
        mock_crmimap.noop.assert_not_called()
        mock_crmimap.release.assert_called_once()

    @patch('crm.utils.manage_imaps.mail_admins')
    @patch('crm.utils.manage_imaps.Site')
    def test_serve_crmimap_exception_handling(self, mock_site, mock_mail_admins):
        """Test _serve_crmimap handles exceptions and sends admin mail."""
        mock_crmimap = MagicMock()
        mock_crmimap.email_host_user = 'test@example.com'
        
        # Configure the mock to raise an exception when accessing certain attributes
        type(mock_crmimap).last_request_time = PropertyMock(
            side_effect=Exception("Test exception")
        )
        
        self.manager.crmimap_storage['test@example.com'] = mock_crmimap
        mock_site.objects.get_current.return_value.domain = 'example.com'

        # The method should catch the exception and send admin mail
        self.manager._serve_crmimap('test@example.com')
        
        # Verify that mail_admins was called
        mock_mail_admins.assert_called_once()
        call_args = mock_mail_admins.call_args
        self.assertIn("Exception CrmImapManager._serve_crmimap()", call_args[0][0])


@tag('TestCase')
class TestCrmImapManagerRun(BaseTestCase):
    """Test CrmImapManager.run method."""

    def setUp(self):
        print(" Run Test Method:", self._testMethodName)

        self.ea_queue = queue.Queue()
        self.manager = CrmImapManager(self.ea_queue)

    @override_settings(REUSE_IMAP_CONNECTION=False)
    def test_run_without_reuse_connection(self):
        """Test run does nothing when REUSE_IMAP_CONNECTION is False."""
        with patch.object(self.manager, '_keep_in_touch') as mock_keep:
            with patch('crm.utils.manage_imaps.sleep'):
                self.manager.run()

            mock_keep.assert_not_called()

    @override_settings(REUSE_IMAP_CONNECTION=True, TESTING=True)
    def test_run_without_testing_flag(self):
        """Test run does nothing when TESTING is True."""
        with patch.object(self.manager, '_keep_in_touch') as mock_keep:
            with patch('crm.utils.manage_imaps.sleep'):
                self.manager.run()

            mock_keep.assert_not_called()

    @override_settings(REUSE_IMAP_CONNECTION=True, TESTING=False)
    @patch('crm.utils.manage_imaps.IMAP_NOOP_PERIOD', 60)
    def test_run_calls_keep_in_touch(self):
        """Test run sleeps and calls _keep_in_touch."""
        with patch.object(self.manager, '_keep_in_touch') as mock_keep:
            with patch('crm.utils.manage_imaps.sleep') as mock_sleep:
                with patch('crm.utils.manage_imaps.random', return_value=0.5):
                    self.manager.run()

                    mock_sleep.assert_called_once()
                    mock_keep.assert_called_once()


@tag('TestCase')
class TestCrmImapManagerKeepInTouch(BaseTestCase):
    """Test CrmImapManager._keep_in_touch method (limited)."""

    def setUp(self):
        print(" Run Test Method:", self._testMethodName)

        self.ea_queue = queue.Queue()
        self.manager = CrmImapManager(self.ea_queue)

    @patch('crm.utils.manage_imaps.sleep')
    def test_keep_in_touch_loop_iteration(self, mock_sleep):
        """Test _keep_in_touch iterates through storage."""
        mock_crmimap1 = MagicMock()
        mock_crmimap1.locked = False

        mock_crmimap2 = MagicMock()
        mock_crmimap2.locked = True

        self.manager.crmimap_storage = {
            'test1@example.com': mock_crmimap1,
            'test2@example.com': mock_crmimap2,
        }

        # Mock sleep to break the loop after first iteration
        mock_sleep.side_effect = [None, KeyboardInterrupt()]

        with patch.object(self.manager, '_serve_crmimap'):
            try:
                self.manager._keep_in_touch()
            except KeyboardInterrupt:
                pass

            # _serve_crmimap should be called for unlocked item
            self.manager._serve_crmimap.assert_called_with('test1@example.com')
