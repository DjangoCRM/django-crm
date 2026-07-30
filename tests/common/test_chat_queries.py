"""Tests for lazy chat model resolution in common.queries."""

from django.contrib.contenttypes.models import ContentType
from django.test import RequestFactory
from django.test import tag

from common.queries import add_chat_context
from common.queries import annotate_chat
from common.utils.helpers import USER_MODEL
from crm.models import Company
from crm.models import Contact
from crm.models import Country
from tests.base_test_classes import BaseTestCase


@tag('TestCase')
class ChatQueryHelperTests(BaseTestCase):
    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()
        cls.owner = USER_MODEL.objects.get(username='Andrew.Manager.Global')
        cls.other_user = USER_MODEL.objects.get(username='Adam.Admin')
        cls.content_type = ContentType.objects.get_for_model(Contact)
        cls.contact = Contact.objects.create(
            first_name='Chat',
            last_name='Target',
            email='chat-target@example.com',
            owner=cls.owner,
            company=Company.objects.create(
                full_name='Chat Query Co',
                email='chat-query@example.com',
                owner=cls.owner,
                country=Country.objects.first(),
            ),
        )
        chat_message = cls._chat_message_model()
        cls.read_message = chat_message.objects.create(
            content_type=cls.content_type,
            object_id=cls.contact.pk,
            content='Read thread',
            owner=cls.owner,
        )
        cls.read_message.to.add(cls.owner)
        cls.unread_message = chat_message.objects.create(
            content_type=cls.content_type,
            object_id=cls.contact.pk,
            content='Unread thread',
            owner=cls.other_user,
        )
        cls.unread_message.to.add(cls.owner)
        cls.unread_message.recipients.add(cls.owner)
        cls.other_recipient_message = chat_message.objects.create(
            content_type=cls.content_type,
            object_id=cls.contact.pk,
            content='Other recipient thread',
            owner=cls.other_user,
        )
        cls.other_recipient_message.to.add(cls.other_user)
        cls.other_recipient_message.recipients.add(cls.other_user)

    @staticmethod
    def _chat_message_model():
        from django.apps import apps

        return apps.get_model('chat', 'ChatMessage')

    def test_annotate_chat_marks_unread_for_requesting_recipient(self):
        request = RequestFactory().get('/')
        request.user = self.owner
        request.user.is_chief = False
        row = annotate_chat(
            request,
            Contact.objects.filter(pk=self.contact.pk),
        ).get()
        self.assertTrue(row.is_chat)
        self.assertTrue(row.is_unread_chat)

    def test_annotate_chat_ignores_unread_for_other_recipient(self):
        request = RequestFactory().get('/')
        request.user = self.owner
        request.user.is_chief = False
        annotated_sql = str(
            annotate_chat(
                request,
                Contact.objects.filter(pk=self.contact.pk),
            ).query,
        )
        self.assertIn('EXISTS', annotated_sql.upper())
        row = annotate_chat(
            request,
            Contact.objects.filter(pk=self.contact.pk),
        ).get()
        self.assertTrue(row.is_chat)

    def test_add_chat_context_reports_unread_state(self):
        request = RequestFactory().get('/')
        request.user = self.owner
        context = {}
        add_chat_context(
            request,
            context,
            self.contact.pk,
            self.content_type,
        )
        self.assertTrue(context['is_chat'])
        self.assertTrue(context['is_unread_chat'])

    def test_add_chat_context_without_messages(self):
        request = RequestFactory().get('/')
        request.user = self.owner
        context = {}
        add_chat_context(request, context, '999999', self.content_type)
        self.assertFalse(context['is_chat'])
