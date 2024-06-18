from queue import Empty
from django.apps import apps
from django.conf import settings
from django.core import mail
from django.test import TransactionTestCase

from common.utils.helpers import get_today
from crm.models import CrmEmail, Deal, Request
from crm.utils.restore_imap_emails import EXCEPT_SUBJECT
from crm.utils.ticketproc import get_ticket_str
from crm.utils.ticketproc import new_ticket
from massmail.models.email_account import EmailAccount
from tests.utils.helpers import attach_file_to_email_msg
from tests.utils.helpers import get_email_message
from tests.utils.helpers import get_user

# manage.py test tests.crm.utils.test_restore_imap_emails --noinput
# manage.py test tests.crm.utils.test_restore_imap_emails.TestRestoreImapEmails.test_restore_inquiry_email --keepdb


class TestRestoreImapEmails(TransactionTestCase):
    # Inherit TransactionTestCase since creating and saving objects
    # happens in a separate thread.
    fixtures = ('groups.json',)

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        app_config = apps.get_app_config('crm')
        cls.eml_queue = app_config.eml_queue
        cls.inq_eml_queue = app_config.inq_eml_queue

    def setUp(self):
        print("Run Test Method:", self._testMethodName)
        self.owner = get_user()
        self.ea = EmailAccount.objects.create(
            name='CRM Email Account',
            email_host='smtp.example.com',
            email_port=587,
            email_host_user='andrew@example.com',
            email_host_password='password',
            from_email='andrew@example.com',
            main=True,
            email_use_tls=True,
            email_use_ssl=False,
            owner=self.owner,
        )
        self.msg, self.content, self.subject_str = get_email_message()

    def test_restore_incoming_email_with_ticked(self):
        """Test restore in db an incoming email with ticked"""
        ticket = new_ticket()
        deal = Deal.objects.create(
            name="Mock deal",
            description=self.content,
            next_step_date=get_today(),
            ticket=ticket
        )
        self.msg.replace_header('Subject', get_ticket_str(ticket))
        self.eml_queue.put((self.msg.as_bytes(), self.ea, 'incoming', 1, '', None))
        self.eml_queue.join()
        try:
            CrmEmail.objects.get(ticket=ticket, deal=deal)
        except CrmEmail.DoesNotExist:
            self.fail("Expected Email not created in db")

    def test_restore_inquiry_email(self):
        """Test restore in db an inquiry email with file"""
        file_name = attach_file_to_email_msg(self.msg)
        self.eml_queue.put((self.msg.as_bytes(), self.ea, 'inquiry', 1, '', None))
        self.eml_queue.join()
        try:
            with self.inq_eml_queue.all_tasks_done:
                while self.inq_eml_queue.unfinished_tasks:
                    self.inq_eml_queue.all_tasks_done.wait(timeout=3)
        except Empty:
            self.fail("Email not added to queue to create a request")
        self.assertIn(self.content, mail.outbox[0].body)
        try:
            request = Request.objects.get(
                request_for=self.subject_str,
                description__contains=self.content
            )
        except Request.DoesNotExist:
            self.fail("The request was not created")
        file = request.files.first()
        self.assertIn(file_name, file.file.name)
        file.file.delete()
        try:
            CrmEmail.objects.get(subject=self.subject_str, content__contains=self.content)
        except CrmEmail.DoesNotExist:
            self.fail("New Email not created in db")
        mail.outbox = []

    def test_restore_incoming_email(self):
        """Test handle an incoming email without ticket"""
        self.eml_queue.put((self.msg.as_bytes(), self.ea, 'incoming', 1, '', None))
        self.eml_queue.join()
        try:
            CrmEmail.objects.get(subject=self.subject_str)
            self.fail("New Email created in db")
        except CrmEmail.DoesNotExist:
            pass
        mail.outbox = []

    def test_handle_exception(self):
        """Test handle an exception"""
        self.eml_queue.put((self.msg, self.ea, 'incoming', 1, '', None))
        self.eml_queue.join()
        self.assertEqual(len(mail.outbox), 1)
        admins = [x[1] for x in settings.ADMINS]
        self.assertEqual(mail.outbox[0].to, admins)
        self.assertEqual(
            mail.outbox[0].subject,
            settings.EMAIL_SUBJECT_PREFIX + EXCEPT_SUBJECT
        )
        mail.outbox = []
