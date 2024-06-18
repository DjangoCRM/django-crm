from random import random
from time import sleep

from django.core import mail
from django.test import SimpleTestCase

from common.utils.helpers import send_crm_email

# manage.py test tests.common.utils.test_notification_email_sender --keepdb


class TestNotifEmailSender(SimpleTestCase):

    def setUp(self):
        print("Run Test Method:", self._testMethodName)

    def test_notification_email_sender(self):
                
        subject = "CRM Notification"
        body = str(random())
        to = ["Ted@example.com"]
        
        send_crm_email(subject, body, to)
        
        sleep(0.01)
        self.assertEqual(len(mail.outbox), 1)
        self.assertEqual(mail.outbox[0].to, [to[0]])
        self.assertEqual(mail.outbox[0].body, body)
        mail.outbox = []
