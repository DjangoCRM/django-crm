from random import random
from django.contrib.contenttypes.models import ContentType
from django.core import mail
from django.test import tag
from django.urls import reverse
from django.utils import timezone
from urllib.parse import urlencode

from chat.models import ChatMessage
from chat.site.chatmessageadmin import ChatMessageAdmin
from chat.site.chatmessageadmin import get_query_string
from common.utils.helpers import USER_MODEL
from crm.models import Deal
from crm.site.crmadminsite import crm_site
from tasks.models import Memo
from tasks.models import Project
from tasks.models import Task
from tasks.models import ProjectStage
from tasks.models import TaskStage
from tests.utils.helpers import add_file_to_form
from tests.utils.helpers import get_adminform_initials
from tests.base_test_classes import BaseTestCase

# manage.py test tests.chat.test_chat --keepdb

chat_admin = ChatMessageAdmin(model=ChatMessage, admin_site=crm_site)


@tag('TestCase')
class TestChat(BaseTestCase):
    """Test chat in task, memo, project and deal change view."""

    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()
        cls.content_id = random()
        cls.changelist_url = reverse(
            "site:tasks_memo_changelist"
        )
        username_list = ("Garry.Chief", "Andrew.Manager.Global",
                         "Darian.Manager.Co-worker.Head.Global")
        users = USER_MODEL.objects.filter(
            username__in=username_list)
        cls.chief = users.get(
            username="Garry.Chief"
        )
        cls.andrew = users.get(
            username="Andrew.Manager.Global"
        )
        cls.darian = users.get(
            username="Darian.Manager.Co-worker.Head.Global"
        )
        cls.task_stage = TaskStage.objects.get(default=True)
        cls.project_stage = ProjectStage.objects.get(default=True)
        cls.add_msg_url = reverse("site:chat_chatmessage_add")

    def setUp(self):
        print("Run Test Method:", self._testMethodName)

    def test_chat_in_memo(self):
        """Test chat in memo"""
        # create mock memo
        memo = Memo.objects.create(
            name="Mock memo",
            to=self.darian,
            owner=self.andrew
        )
        # submit "Add chat message" button in memo change view
        response, query_str = self.submit_add_msg_button(memo)
        self.assertEqual(response.status_code, 200)
        data = get_adminform_initials(response)
        # fill in the form
        content = random()
        data['content'] = content
        data['recipients'] = [str(self.darian.id)]
        # submit form
        response = self.client.post(
            self.add_msg_url + query_str, 
            data, follow=True
        )
        self.assertEqual(response.status_code, 200)
        self.assertNoFormErrors(response)
        try:
            msg = ChatMessage.objects.get(
                content=content,
                object_id=memo.id,
                recipients=self.darian
            )
        except ChatMessage.DoesNotExist:
            self.fail("The chat message is not created")   
        # notification email sent?
        self.assertQuerySetEqual(msg.recipients.all(), msg.to.all())
        self.assertEqual(len(mail.outbox), 1)
        self.assertEqual(mail.outbox[0].to, [self.darian.email])
        mail.outbox = []

        # reply to the message
        self.client.force_login(self.darian)
        response = self.submit_reply_button(msg)
        self.assertEqual(response.status_code, 200)
        data = get_adminform_initials(response)
        # fill in the form
        reply_content = random()
        data['content'] = reply_content
        # submit form
        reply_url = response.wsgi_request.get_full_path()
        response = self.client.post(reply_url, data, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertNoFormErrors(response)
        self.assertTrue(
            ChatMessage.objects.filter(
                content=reply_content,
                object_id=memo.id,
                recipients=self.andrew
            ).exists(),
            "The chat message is not created"
        )
        # notification email sent?
        self.assertEqual(len(mail.outbox), 1)
        self.assertEqual(mail.outbox[0].to[0], self.andrew.email)
        mail.outbox = []

    def test_chat_in_task(self):
        """Test chat in task"""
        # create task
        task = Task.objects.create(
            name="Mock task",
            owner=self.chief,
            stage=self.task_stage
        )
        task.responsible.set([self.andrew, self.darian])
        # submit "Add chat message" button in task change view
        response, query_str = self.submit_add_msg_button(task)
        self.assertEqual(response.status_code, 200)
        data = get_adminform_initials(response)
        # fill in the form
        content = random()
        data['content'] = content
        # data['owner'] = 'Test memo'
        data['recipients'] = [str(self.darian.id), str(self.chief.id)]
        add_file_to_form(self._testMethodName, data)
        # submit form
        response = self.client.post(
            self.add_msg_url + query_str,
            data, follow=True
        )
        self.assertEqual(response.status_code, 200)
        self.assertNoFormErrors(response)
        data['common-thefile-content_type-object_id-0-file'].close()
        try:
            msg = ChatMessage.objects.get(
                content=content,
                object_id=task.id,
                recipients=self.darian
            )
            file = msg.files.first()
        except ChatMessage.DoesNotExist:
            self.fail("The chat message is not created")
        # notification email sent?
        self.assertEqual(len(mail.outbox), 1)
        self.assertEqual(
            mail.outbox[0].to,
            [self.darian.email, self.chief.email]
        )
        self.assertIn(file.file.url, mail.outbox[0].body)
        mail.outbox = []

        # reply the message
        self.client.force_login(self.darian)
        response = self.submit_reply_button(msg)
        self.assertEqual(response.status_code, 200)
        data = get_adminform_initials(response)
        # fill in the form
        reply_content = random()
        data['content'] = reply_content
        data['recipients'] = [str(self.andrew.id), str(self.chief.id)]
        # submit form
        reply_url = response.wsgi_request.get_full_path()
        response = self.client.post(reply_url, data, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertNoFormErrors(response)
        self.assertTrue(
            ChatMessage.objects.filter(
                content=reply_content,
                object_id=task.id,
                recipients__in=(self.andrew, self.chief)
            ).exists(),
            "The chat message is not created"
        )
        # notification email sent?
        self.assertEqual(len(mail.outbox), 1)
        self.assertEqual(mail.outbox[0].to, [
                         self.andrew.email, self.chief.email])
        mail.outbox = []
        file.file.delete()
        
    def test_chat_in_project(self):
        """Test chat in project"""
        project = Project.objects.create(
            name="Mock project",
            owner=self.chief,
            stage=self.project_stage
        )
        project.responsible.set([self.andrew, self.darian])          
        # submit "Add chat message" button in project change view
        response, query_str = self.submit_add_msg_button(project)
        self.assertEqual(response.status_code, 200)
        data = get_adminform_initials(response)
        # fill in the form
        content = random()
        data['content'] = content
        # data['owner'] = 'Test memo'
        data['recipients'] = [str(self.darian.id), str(self.chief.id)]
        # submit form
        response = self.client.post(
            self.add_msg_url + query_str, 
            data, 
            follow=True
        )
        self.assertEqual(response.status_code, 200)
        self.assertNoFormErrors(response)
        try:
            msg = ChatMessage.objects.get(
                object_id=project.id,
                content=content,
                recipients=self.darian
            )
        except ChatMessage.DoesNotExist:
            self.fail("The chat message is not created")   
        # notification email sent?
        self.assertEqual(len(mail.outbox), 1)
        self.assertEqual(
            mail.outbox[0].to, 
            [self.darian.email, 
             self.chief.email]
        )
        mail.outbox = []

        # reply the message
        self.client.force_login(self.darian)
        response = self.submit_reply_button(msg)
        self.assertEqual(response.status_code, 200)
        data = get_adminform_initials(response)
        # fill in the form
        reply_content = random()
        data['content'] = reply_content
        # submit form
        reply_url = response.wsgi_request.get_full_path()
        response = self.client.post(reply_url, data, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertNoFormErrors(response)
        self.assertTrue(
            ChatMessage.objects.filter(
                object_id=project.id,
                content=reply_content,
                recipients=self.andrew
            ).exists(),
            "The chat message is not created"
        )
        # notification email sent?
        self.assertEqual(len(mail.outbox), 1)
        self.assertEqual(mail.outbox[0].to[0], self.andrew.email)
        mail.outbox = []
        
    def test_chat_in_deal(self):
        """Test chat in deal"""
        content = random()
        deal = Deal.objects.create(
            name="Mock deal",
            description=content,
            owner=self.andrew,
            co_owner=self.darian,
            next_step="next step",
            next_step_date=timezone.now()
        )                
        # submit "Add chat message" button in deal change view
        response, query_str = self.submit_add_msg_button(deal)
        self.assertEqual(response.status_code, 200)
        data = get_adminform_initials(response)
        # fill in the form
        content = random()
        data['content'] = content
        data['recipients'] = [str(self.darian.id), str(self.chief.id)]
        # submit form
        response = self.client.post(
            self.add_msg_url + query_str, 
            data, follow=True
        )
        self.assertEqual(response.status_code, 200)
        self.assertNoFormErrors(response)
        try:
            msg = ChatMessage.objects.get(
                object_id=deal.id,
                content=content,
                recipients=self.darian
            )
        except ChatMessage.DoesNotExist:
            self.fail("The chat message is not created")   
        # notification email sent?
        self.assertEqual(len(mail.outbox), 1)
        self.assertEqual(
            mail.outbox[0].to, 
            [self.darian.email, self.chief.email]
        )
        mail.outbox = []

        # reply the message
        self.client.force_login(self.darian)
        response = self.submit_reply_button(msg)
        self.assertEqual(response.status_code, 200)
        data = get_adminform_initials(response)
        # fill in the form
        reply_content = random()
        data['content'] = reply_content
        # submit form
        reply_url = response.wsgi_request.get_full_path()
        response = self.client.post(reply_url, data, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertNoFormErrors(response)
        self.assertTrue(
            ChatMessage.objects.filter(
                object_id=deal.id,
                content=reply_content,
                recipients=self.andrew
            ).exists(),
            "The chat message is not created"
        )
        # notification email sent?
        self.assertEqual(len(mail.outbox), 1)
        self.assertEqual(mail.outbox[0].to[0], self.andrew.email)
        mail.outbox = []
        
    def submit_add_msg_button(self, instance):
        self.client.force_login(self.andrew)
        # get_for_model(project) works wrong due cache
        # content_type = ContentType.objects.get_for_model(instance)
        content_type = ContentType.objects.get(
            model=instance._meta.model_name
        )
        params = {
            'content_type': content_type.id,
            'object_id': instance.id,
            'owner': self.andrew.id
        }
        query_str = f'?{urlencode(params)}'        
        return self.client.get(
            self.add_msg_url + query_str, 
            follow=True
        ), query_str        

    def submit_reply_button(self, instance):
        query_str = f'?{get_query_string(instance)}'
        reply_url = reverse('site:chat_chatmessage_add') + query_str
        return self.client.get(reply_url, follow=True)
