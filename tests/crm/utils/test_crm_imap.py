"""
Unit tests for CrmIMAP class using mocks.

Tests IMAP connection management, mailbox operations, and email 
manipulation functionality.
"""
import imaplib
from datetime import datetime as dt
from time import sleep
from unittest.mock import MagicMock, patch

from django.test import override_settings, tag

from crm.utils.crm_imap import CrmIMAP, _get_box_initial_data
from massmail.models import EmailAccount
from tests.base_test_classes import BaseTestCase


# manage.py test tests.crm.utils.test_crm_imap --keepdb


@tag('TestCase')
class TestCrmImapInitialization(BaseTestCase):
    """Test CrmIMAP initialization."""

    def setUp(self):
        print(" Run Test Method:", self._testMethodName)

    def test_initialization(self):
        """Test CrmIMAP initializes with correct attributes."""
        email_user = 'test@example.com'
        crmimap = CrmIMAP(email_user)

        self.assertEqual(crmimap.email_host_user, email_user)
        self.assertTrue(crmimap.locked)

    def test_initialization_sets_email_host_user(self):
        """Test email_host_user is set correctly."""
        email_user = 'user@domain.com'
        crmimap = CrmIMAP(email_user)

        self.assertEqual(crmimap.email_host_user, email_user)


@tag('TestCase')
class TestCrmImapCompleteInit(BaseTestCase):
    """Test CrmIMAP._complete_init method."""

    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()
        from common.utils.helpers import USER_MODEL

        user, _ = USER_MODEL.objects.get_or_create(
            username="test_owner_crmimap",
            defaults={'email': 'test_owner_crmimap@test.com'}
        )
        cls.owner = user

    def setUp(self):
        print(" Run Test Method:", self._testMethodName)

        self.crmimap = CrmIMAP('test@example.com')
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

    def test_complete_init_sets_attributes(self):
        """Test _complete_init sets all required attributes."""
        boxes = {'INBOX': {'name': 'INBOX', 'name on server': b'INBOX'}}

        self.crmimap._complete_init(boxes, self.email_account)

        self.assertEqual(self.crmimap.boxes, boxes)
        self.assertIsNone(self.crmimap.connection)
        self.assertIsNone(self.crmimap.error)
        self.assertEqual(self.crmimap.ea, self.email_account)
        self.assertIsNone(self.crmimap.selected_box)
        self.assertIsNone(self.crmimap.noop_time)
        self.assertIsNotNone(self.crmimap.create_time)
        self.assertIsNotNone(self.crmimap.last_request_time)

    def test_complete_init_sets_lockfile_path(self):
        """Test _complete_init sets lockfile path."""
        self.crmimap._complete_init({}, self.email_account)

        self.assertIsNotNone(self.crmimap.lockfile)
        self.assertIn(self.email_account.imap_host, str(self.crmimap.lockfile))


@tag('TestCase')
class TestCrmImapConnect(BaseTestCase):
    """Test CrmIMAP connection methods."""

    def setUp(self):
        print(" Run Test Method:", self._testMethodName)

        self.crmimap = CrmIMAP('test@example.com')

    @patch('crm.utils.crm_imap.imaplib.IMAP4_SSL')
    def test_connect_success(self, mock_imap4_ssl):
        """Test successful IMAP connection."""
        mock_connection = MagicMock()
        mock_imap4_ssl.return_value = mock_connection

        self.crmimap.ea = MagicMock()
        self.crmimap.ea.imap_host = 'imap.example.com'
        self.crmimap.error = None

        self.crmimap._connect()

        mock_imap4_ssl.assert_called_once_with('imap.example.com')
        self.assertEqual(self.crmimap.connection, mock_connection)

    @patch('crm.utils.crm_imap.mail_admins')
    @patch('crm.utils.crm_imap.imaplib.IMAP4_SSL')
    def test_connect_failure(self, mock_imap4_ssl, mock_mail_admins):
        """Test handling of connection failure."""
        mock_imap4_ssl.side_effect = Exception("Connection failed")

        self.crmimap.ea = MagicMock()
        self.crmimap.ea.imap_host = 'imap.example.com'

        self.crmimap._connect()

        self.assertIsNotNone(self.crmimap.error)
        mock_mail_admins.assert_called_once()


@tag('TestCase')
class TestCrmImapLogin(BaseTestCase):
    """Test CrmIMAP login method."""

    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()
        from common.utils.helpers import USER_MODEL

        user, _ = USER_MODEL.objects.get_or_create(
            username="test_owner_login",
            defaults={'email': 'test_owner_login@test.com'}
        )
        cls.owner = user

    def setUp(self):
        print(" Run Test Method:", self._testMethodName)

        self.crmimap = CrmIMAP('test@example.com')
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
        self.crmimap.ea = self.email_account
        self.crmimap.error = None
        self.crmimap.connection = MagicMock()

    @patch('crm.utils.crm_imap.CrmIMAP._execute')
    def test_login_success(self, mock_execute):
        """Test successful login."""
        mock_execute.return_value = ('OK', None, None)

        self.crmimap._log_in()

        mock_execute.assert_called_once()
        call_args = mock_execute.call_args
        self.assertIn('login', str(call_args).lower())
        self.assertIsNone(self.crmimap.error)

    @patch('crm.utils.crm_imap.mail_admins')
    @patch('crm.utils.crm_imap.CrmIMAP._execute')
    def test_login_with_app_password(self, mock_execute, mock_mail_admins):
        """Test login uses app password if available."""
        self.email_account.email_app_password = 'app_password'
        mock_execute.return_value = ('OK', None, None)

        self.crmimap._log_in()

        call_args = mock_execute.call_args
        # The password should be in the params
        params = call_args[0][1]
        self.assertEqual(params[1], 'app_password')


@tag('TestCase')
class TestCrmImapCloseAndLogout(BaseTestCase):
    """Test CrmIMAP close and logout."""

    def setUp(self):
        print(" Run Test Method:", self._testMethodName)

        self.crmimap = CrmIMAP('test@example.com')

    def test_close_and_logout_with_connection(self):
        """Test close_and_logout closes and logs out."""
        mock_connection = MagicMock()
        mock_connection.state = 'NONAUTH'  # Not AUTH, so close will be called
        self.crmimap.connection = mock_connection

        self.crmimap.close_and_logout()

        mock_connection.close.assert_called_once()
        mock_connection.logout.assert_called_once()

    def test_close_and_logout_without_connection(self):
        """Test close_and_logout handles None connection."""
        self.crmimap.connection = None

        # Should not raise exception
        self.crmimap.close_and_logout()

    def test_close_and_logout_handles_imap_error(self):
        """Test close_and_logout handles IMAP errors."""
        mock_connection = MagicMock()
        mock_connection.state = 'AUTH'
        mock_connection.logout.side_effect = imaplib.IMAP4.error(
            "Logout failed")
        self.crmimap.connection = mock_connection

        # Should not raise exception
        self.crmimap.close_and_logout()


@tag('TestCase')
class TestCrmImapLock(BaseTestCase):
    """Test CrmIMAP lock mechanism."""

    def setUp(self):
        print(" Run Test Method:", self._testMethodName)

        self.crmimap = CrmIMAP('test@example.com')
        self.crmimap.create_time = dt.now()
        self.crmimap.noop_time = None
        self.crmimap.last_request_time = dt.now()
        self.crmimap.debug = 0

    def test_lock_when_unlocked(self):
        """Test lock when instance is unlocked."""
        self.crmimap.locked = False

        self.crmimap.lock()

        self.assertTrue(self.crmimap.locked)

    @patch('crm.utils.crm_imap.mail_admins')
    @patch('crm.utils.crm_imap.Site')
    @patch('crm.utils.crm_imap.release_limit', 1)
    @patch('crm.utils.crm_imap.sleep')
    def test_lock_timeout_raises_error(self, mock_sleep, mock_site, mock_mail_admins):
        """Test lock raises RuntimeError on timeout."""
        self.crmimap.locked = True
        self.crmimap.ea = MagicMock()
        mock_site.objects.get_current.return_value.domain = 'example.com'

        with self.assertRaises(RuntimeError):
            self.crmimap.lock()

        mock_mail_admins.assert_called_once()


@tag('TestCase')
class TestCrmImapRelease(BaseTestCase):
    """Test CrmIMAP release mechanism."""

    def setUp(self):
        print(" Run Test Method:", self._testMethodName)

        self.crmimap = CrmIMAP('test@example.com')
        self.crmimap.connection = MagicMock()

    @override_settings(REUSE_IMAP_CONNECTION=True)
    def test_release_with_reuse_connection(self):
        """Test release unlocks when REUSE_IMAP_CONNECTION is True."""
        self.crmimap.locked = True

        self.crmimap.release()

        self.assertFalse(self.crmimap.locked)

    @override_settings(REUSE_IMAP_CONNECTION=False)
    def test_release_without_reuse_connection(self):
        """Test release closes connection when REUSE_IMAP_CONNECTION is False."""
        self.crmimap.locked = True

        with patch.object(self.crmimap, 'close_and_logout') as mock_close:
            self.crmimap.release()

            mock_close.assert_called_once()


@tag('TestCase')
class TestCrmImapNoop(BaseTestCase):
    """Test CrmIMAP NOOP (keep-alive) method."""

    def setUp(self):
        print(" Run Test Method:", self._testMethodName)

        self.crmimap = CrmIMAP('test@example.com')
        self.crmimap.connection = MagicMock()
        self.crmimap.error = None

    @patch('crm.utils.crm_imap.CrmIMAP._execute')
    def test_noop_success(self, mock_execute):
        """Test successful NOOP."""
        mock_execute.return_value = ('OK', None, None)
        self.crmimap.ea = MagicMock()

        result = self.crmimap.noop()

        self.assertEqual(result, 'OK')
        mock_execute.assert_called_once()

    def test_noop_with_error_returns_no(self):
        """Test NOOP returns NO when error exists."""
        self.crmimap.error = Exception("Test error")

        result = self.crmimap.noop()

        self.assertEqual(result, 'NO')


@tag('TestCase')
class TestCrmImapSelectBox(BaseTestCase):
    """Test CrmIMAP select_box method."""

    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()
        from common.utils.helpers import USER_MODEL

        user, _ = USER_MODEL.objects.get_or_create(
            username="test_owner_select",
            defaults={'email': 'test_owner_select@test.com'}
        )
        cls.owner = user

    def setUp(self):
        print(" Run Test Method:", self._testMethodName)

        self.crmimap = CrmIMAP('test@example.com')
        self.crmimap.connection = MagicMock()
        self.crmimap.boxes = {
            'INBOX': {'name': 'INBOX', 'name on server': b'INBOX'},
            'Sent': {'name': 'Sent', 'name on server': b'Sent'}
        }
        self.crmimap.selected_box = None

    @patch('crm.utils.crm_imap.CrmIMAP._execute')
    def test_select_box_success(self, mock_execute):
        """Test successful box selection."""
        mock_execute.return_value = ('OK', None, None)

        result = self.crmimap.select_box('INBOX')

        self.assertEqual(result, 'OK')
        self.assertEqual(self.crmimap.selected_box['name'], 'INBOX')
        mock_execute.assert_called_once()

    def test_select_box_already_selected(self):
        """Test select_box skips if already selected."""
        self.crmimap.selected_box = self.crmimap.boxes['INBOX']
        self.crmimap.connection.state = 'SELECTED'

        with patch('crm.utils.crm_imap.CrmIMAP._execute') as mock_execute:
            result = self.crmimap.select_box('INBOX')

            mock_execute.assert_not_called()
            self.assertEqual(result, 'OK')

    @patch('crm.utils.crm_imap.CrmIMAP._execute')
    def test_select_box_failure(self, mock_execute):
        """Test select_box handles failure."""
        mock_execute.return_value = ('NO', None, None)

        result = self.crmimap.select_box('INBOX')

        self.assertEqual(result, 'NO')


@tag('TestCase')
class TestCrmImapSearch(BaseTestCase):
    """Test CrmIMAP search method."""

    def setUp(self):
        print(" Run Test Method:", self._testMethodName)

        self.crmimap = CrmIMAP('test@example.com')
        self.crmimap.connection = MagicMock()

    @patch('crm.utils.crm_imap.CrmIMAP._execute')
    def test_search_success(self, mock_execute):
        """Test successful email search."""
        mock_execute.return_value = ('OK', [b'1 2 3'], None)

        result, data, error = self.crmimap.search('ALL')

        self.assertEqual(result, 'OK')
        self.assertEqual(data, [b'1 2 3'])


@tag('TestCase')
class TestCrmImapGetEmailsByMessageId(BaseTestCase):
    """Test CrmIMAP get_emails_by_message_id method."""

    def setUp(self):
        print(" Run Test Method:", self._testMethodName)

        self.crmimap = CrmIMAP('test@example.com')
        self.crmimap.connection = MagicMock()

    @patch('crm.utils.crm_imap.CrmIMAP._execute')
    def test_get_emails_by_message_id_success(self, mock_execute):
        """Test getting emails by message ID."""
        mock_execute.return_value = ('OK', [b'1 2'], None)

        result, data = self.crmimap.get_emails_by_message_id(
            'message-id@example.com')

        self.assertEqual(result, 'OK')
        self.assertEqual(data, [b'1 2'])


@tag('TestCase')
class TestCrmImapUidFetch(BaseTestCase):
    """Test CrmIMAP uid_fetch method."""

    def setUp(self):
        print(" Run Test Method:", self._testMethodName)

        self.crmimap = CrmIMAP('test@example.com')
        self.crmimap.connection = MagicMock()

    @patch('crm.utils.crm_imap.CrmIMAP._execute')
    def test_uid_fetch_success(self, mock_execute):
        """Test successful UID fetch."""
        email_data = b'From: test@example.com\nSubject: Test'
        mock_execute.return_value = ('OK', [email_data], None)

        result, data, error = self.crmimap.uid_fetch(b'1')

        self.assertEqual(result, 'OK')
        self.assertEqual(data, [email_data])


@tag('TestCase')
class TestCrmImapDeleteEmails(BaseTestCase):
    """Test CrmIMAP delete_emails method."""

    def setUp(self):
        print(" Run Test Method:", self._testMethodName)

        self.crmimap = CrmIMAP('test@example.com')
        self.crmimap.connection = MagicMock()
        self.crmimap.boxes = {
            'INBOX': {'name': 'INBOX', 'name on server': b'INBOX'},
            'Trash': {'name': 'Trash', 'name on server': b'Trash'}
        }
        self.crmimap.selected_box = None

    @patch('crm.utils.crm_imap.CrmIMAP._uid_delete')
    @patch('crm.utils.crm_imap.CrmIMAP._uid_copy')
    @patch('crm.utils.crm_imap.CrmIMAP.select_box')
    def test_delete_emails_success(self, mock_select, mock_copy, mock_delete):
        """Test successful email deletion."""
        mock_select.return_value = 'OK'

        self.crmimap.delete_emails('1 2 3')

        mock_select.assert_called_once_with('INBOX')
        mock_copy.assert_called_once_with('1 2 3', 'Trash')
        mock_delete.assert_called_once_with('1 2 3')

    @patch('crm.utils.crm_imap.CrmIMAP.select_box')
    def test_delete_emails_select_failed(self, mock_select):
        """Test delete_emails when select_box fails."""
        mock_select.return_value = 'NO'

        with patch('crm.utils.crm_imap.CrmIMAP._uid_copy') as mock_copy:
            self.crmimap.delete_emails('1 2 3')

            mock_copy.assert_not_called()


@tag('TestCase')
class TestCrmImapMoveEmails(BaseTestCase):
    """Test CrmIMAP move_emails_to_spam method."""

    def setUp(self):
        print(" Run Test Method:", self._testMethodName)

        self.crmimap = CrmIMAP('test@example.com')
        self.crmimap.connection = MagicMock()
        self.crmimap.boxes = {
            'INBOX': {'name': 'INBOX', 'name on server': b'INBOX'},
            'Spam': {'name': 'Spam', 'name on server': b'Spam'}
        }

    @patch('crm.utils.crm_imap.CrmIMAP._uid_delete')
    @patch('crm.utils.crm_imap.CrmIMAP._uid_copy')
    @patch('crm.utils.crm_imap.CrmIMAP.select_box')
    def test_move_emails_to_spam_success(self, mock_select, mock_copy, mock_delete):
        """Test successful move to spam."""
        mock_select.return_value = 'OK'

        self.crmimap.move_emails_to_spam('1 2')

        mock_select.assert_called_once_with('INBOX')
        mock_copy.assert_called_once_with('1 2', 'Spam')
        mock_delete.assert_called_once_with('1 2')


@tag('TestCase')
class TestCrmImapMarkAsRead(BaseTestCase):
    """Test CrmIMAP mark_emails_as_read method."""

    def setUp(self):
        print(" Run Test Method:", self._testMethodName)

        self.crmimap = CrmIMAP('test@example.com')
        self.crmimap.connection = MagicMock()

    @patch('crm.utils.crm_imap.CrmIMAP._uid_seen')
    @patch('crm.utils.crm_imap.CrmIMAP.select_box')
    def test_mark_as_read_success(self, mock_select, mock_uid_seen):
        """Test successful mark as read."""
        mock_select.return_value = 'OK'

        self.crmimap.mark_emails_as_read('1 2 3')

        mock_select.assert_called_once_with('INBOX')
        mock_uid_seen.assert_called_once_with('1 2 3')


@tag('TestCase')
class TestCrmImapCheckBoxStatus(BaseTestCase):
    """Test CrmIMAP check_box_status method."""

    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()
        from common.utils.helpers import USER_MODEL

        user, _ = USER_MODEL.objects.get_or_create(
            username="test_owner_boxstatus",
            defaults={'email': 'test_owner_boxstatus@test.com'}
        )
        cls.owner = user

    def setUp(self):
        print(" Run Test Method:", self._testMethodName)

        self.crmimap = CrmIMAP('test@example.com')
        self.email_account = EmailAccount.objects.create(
            name='Test Email Account',
            email_host='imap.example.com',
            email_port=993,
            email_host_user='test@example.com',
            email_host_password='password',
            from_email='test@example.com',
            main=True,
            owner=self.owner,
            inbox_uidnext=100,
            inbox_uidvalidity=1
        )
        self.crmimap.ea = self.email_account
        self.crmimap.connection = MagicMock()
        self.crmimap.boxes = {
            'INBOX': {'name': 'INBOX', 'name on server': b'INBOX'}
        }

    @patch('crm.utils.crm_imap.CrmIMAP._execute')
    def test_check_box_status_no_change(self, mock_execute):
        """Test check_box_status when nothing changed."""
        status_data = b'"INBOX" (UIDVALIDITY 1 UIDNEXT 100)'
        mock_execute.return_value = ('OK', [status_data], None)

        upd_fields = []
        changed, uid_validity = self.crmimap.check_box_status(
            'INBOX', upd_fields)

        self.assertFalse(changed)
        self.assertTrue(uid_validity)
        self.assertEqual(upd_fields, [])

    @patch('crm.utils.crm_imap.CrmIMAP._execute')
    def test_check_box_status_uidnext_changed(self, mock_execute):
        """Test check_box_status when UIDNEXT changed."""
        status_data = b'"INBOX" (UIDVALIDITY 1 UIDNEXT 200)'
        mock_execute.return_value = ('OK', [status_data], None)

        upd_fields = []
        changed, uid_validity = self.crmimap.check_box_status(
            'INBOX', upd_fields)

        self.assertTrue(changed)
        self.assertTrue(uid_validity)
        self.assertIn('inbox_uidnext', upd_fields)

    @patch('crm.utils.crm_imap.CrmIMAP._execute')
    def test_check_box_status_uidvalidity_changed(self, mock_execute):
        """Test check_box_status when UIDVALIDITY changed."""
        status_data = b'"INBOX" (UIDVALIDITY 99 UIDNEXT 100)'
        mock_execute.return_value = ('OK', [status_data], None)

        upd_fields = []
        changed, uid_validity = self.crmimap.check_box_status(
            'INBOX', upd_fields)

        # Changed is only set when UIDNEXT changes, not UIDVALIDITY
        self.assertFalse(changed)
        self.assertFalse(uid_validity)
        self.assertIn('inbox_uidvalidity', upd_fields)


@tag('TestCase')
class TestCrmImapIfSelectedBox(BaseTestCase):
    """Test CrmIMAP if_selected_box method."""

    def setUp(self):
        print(" Run Test Method:", self._testMethodName)

        self.crmimap = CrmIMAP('test@example.com')
        self.crmimap.connection = MagicMock()
        self.crmimap.selected_box = None

    def test_if_selected_box_when_no_selection(self):
        """Test if_selected_box returns False when no box selected."""
        result = self.crmimap.if_selected_box('INBOX')

        self.assertFalse(result)

    def test_if_selected_box_when_different_box(self):
        """Test if_selected_box returns False for different box."""
        self.crmimap.selected_box = {'name': 'Sent', 'name on server': b'Sent'}
        self.crmimap.connection.state = 'SELECTED'

        result = self.crmimap.if_selected_box('INBOX')

        self.assertFalse(result)

    def test_if_selected_box_when_same_box(self):
        """Test if_selected_box returns True when same selected."""
        self.crmimap.selected_box = {
            'name': 'INBOX', 'name on server': b'INBOX'}
        self.crmimap.connection.state = 'SELECTED'

        result = self.crmimap.if_selected_box('INBOX')

        self.assertTrue(result)

    def test_if_selected_box_wrong_connection_state(self):
        """Test if_selected_box returns False for wrong connection state."""
        self.crmimap.selected_box = {
            'name': 'INBOX', 'name on server': b'INBOX'}
        self.crmimap.connection.state = 'AUTH'

        result = self.crmimap.if_selected_box('INBOX')

        self.assertFalse(result)


@tag('TestCase')
class TestCrmImapExecute(BaseTestCase):
    """Test CrmIMAP._execute method."""

    def setUp(self):
        print(" Run Test Method:", self._testMethodName)

        self.crmimap = CrmIMAP('test@example.com')
        self.crmimap.connection = MagicMock()
        self.crmimap.ea = MagicMock()
        self.crmimap.error = None

    @override_settings(REUSE_IMAP_CONNECTION=False)
    def test_execute_success(self):
        """Test _execute with successful command."""
        mock_command = MagicMock(return_value=('OK', [b'data']))

        result, data, error = self.crmimap._execute(
            mock_command, (b'test',), 'Test message'
        )

        self.assertEqual(result, 'OK')
        self.assertEqual(data, [b'data'])
        self.assertIsNone(error)

    @override_settings(REUSE_IMAP_CONNECTION=False)
    def test_execute_without_params(self):
        """Test _execute without parameters."""
        mock_command = MagicMock(return_value=('OK', None))

        result, data, error = self.crmimap._execute(
            mock_command, None, 'Test message'
        )

        self.assertEqual(result, 'OK')
        mock_command.assert_called_once_with()

    @override_settings(REUSE_IMAP_CONNECTION=False)
    @patch('crm.utils.crm_imap.CrmIMAP._mail_admins')
    def test_execute_with_exception(self, mock_mail_admins):
        """Test _execute handles exceptions."""
        mock_command = MagicMock(
            side_effect=imaplib.IMAP4.abort("Connection error")
        )

        result, data, error = self.crmimap._execute(
            mock_command, None, 'Test message'
        )

        self.assertIsNotNone(error)


@tag('TestCase')
class TestCrmImapGetIn(BaseTestCase):
    """Test CrmIMAP.get_in initialization flow."""

    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()
        from common.utils.helpers import USER_MODEL

        user, _ = USER_MODEL.objects.get_or_create(
            username="test_owner_getin",
            defaults={'email': 'test_owner_getin@test.com'}
        )
        cls.owner = user

    def setUp(self):
        print(" Run Test Method:", self._testMethodName)

        self.crmimap = CrmIMAP('test@example.com')
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

    @patch('crm.utils.crm_imap.CrmIMAP._get_boxes')
    @patch('crm.utils.crm_imap.CrmIMAP._log_in')
    @patch('crm.utils.crm_imap.CrmIMAP._connect')
    def test_get_in_success(self, mock_connect, mock_login, mock_get_boxes):
        """Test get_in successful initialization."""
        self.crmimap.error = None

        boxes = {'INBOX': {'name': 'INBOX', 'name on server': b'INBOX'}}
        self.crmimap.get_in(boxes, self.email_account)

        self.assertEqual(self.crmimap.ea, self.email_account)
        mock_connect.assert_called_once()
        mock_login.assert_called_once()
        mock_get_boxes.assert_called_once()

    @patch('crm.utils.crm_imap.CrmIMAP._log_in')
    @patch('crm.utils.crm_imap.CrmIMAP._connect')
    def test_get_in_connection_error(self, mock_connect, mock_login):
        """Test get_in stops on connection error."""
        def set_error():
            self.crmimap.error = Exception("Connection failed")

        mock_connect.side_effect = set_error

        self.crmimap.get_in({}, self.email_account)

        mock_login.assert_not_called()


@tag('TestCase')
class TestCrmImapGetBoxInitialData(BaseTestCase):
    """Test _get_box_initial_data function."""

    def setUp(self):
        print(" Run Test Method:", self._testMethodName)

    def test_get_box_initial_data_returns_dict(self):
        """Test _get_box_initial_data returns correct structure."""
        result = _get_box_initial_data()

        self.assertIsInstance(result, dict)
        self.assertIn('Sent', result)
        self.assertIn('Spam', result)
        self.assertIn('Trash', result)

    def test_get_box_initial_data_values_structure(self):
        """Test returned box structure."""
        result = _get_box_initial_data()

        for box_name, box_data in result.items():
            self.assertIn('name', box_data)
            self.assertIn('name on server', box_data)
            self.assertEqual(box_data['name'], box_name)


@tag('TestCase')
class TestCrmImapUidOperations(BaseTestCase):
    """Test CrmIMAP UID operations."""

    def setUp(self):
        print(" Run Test Method:", self._testMethodName)

        self.crmimap = CrmIMAP('test@example.com')
        self.crmimap.connection = MagicMock()
        self.crmimap.boxes = {
            'Trash': {'name': 'Trash', 'name on server': b'Trash'}
        }

    @patch('crm.utils.crm_imap.CrmIMAP._execute')
    def test_uid_copy(self, mock_execute):
        """Test _uid_copy operation."""
        mock_execute.return_value = ('OK', None, None)

        result, data, error = self.crmimap._uid_copy('1 2', 'Trash')

        self.assertEqual(result, 'OK')
        mock_execute.assert_called_once()

    @patch('crm.utils.crm_imap.CrmIMAP._expunge')
    @patch('crm.utils.crm_imap.CrmIMAP._execute')
    def test_uid_delete(self, mock_execute, mock_expunge):
        """Test _uid_delete operation."""
        mock_execute.return_value = ('OK', None, None)
        mock_expunge.return_value = ('OK', None, None)

        result, data, error = self.crmimap._uid_delete('1 2')

        mock_execute.assert_called_once()
        mock_expunge.assert_called_once()

    @patch('crm.utils.crm_imap.CrmIMAP._execute')
    def test_uid_seen(self, mock_execute):
        """Test _uid_seen operation."""
        mock_execute.return_value = ('OK', None, None)

        result, data, error = self.crmimap._uid_seen('1 2 3')

        self.assertEqual(result, 'OK')


@tag('TestCase')
class TestCrmImapStringRepresentation(BaseTestCase):
    """Test CrmIMAP string representation."""

    def setUp(self):
        print(" Run Test Method:", self._testMethodName)

    def test_str_representation(self):
        """Test __str__ returns proper representation."""
        email_user = 'test@example.com'
        crmimap = CrmIMAP(email_user)

        result = str(crmimap)

        self.assertIn('CrmIMAP', result)
        self.assertIn(email_user, result)
