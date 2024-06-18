from random import random
from django.core import mail
from django.test import tag
from django.urls import reverse

from common.utils.helpers import USER_MODEL
from tasks.models import ProjectStage
from tasks.models import Project
from tests.base_test_classes import BaseTestCase
from tests.utils.helpers import add_file_to_form
from tests.utils.helpers import get_adminform_initials
from common.models import TheFile

# manage.py test tests.tasks.test_project --keepdb


@tag('TestCase')
class TestProject(BaseTestCase):
    """Test Project"""

    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()
        username_list = ("Garry.Chief", "Sergey.Co-worker.Head.Bookkeeping",
                         "Masha.Co-worker.Bookkeeping", "Adam.Admin")
        users = USER_MODEL.objects.filter(
            username__in=username_list)
        cls.chief = users.get(username="Garry.Chief")
        cls.sergey = users.get(
            username="Sergey.Co-worker.Head.Bookkeeping")
        cls.masha = users.get(
            username="Masha.Co-worker.Bookkeeping")
        cls.admin = users.get(username="Adam.Admin")
        cls.changelist_url = reverse('site:tasks_project_changelist')
        cls.add_url = reverse("site:tasks_project_add")
        cls.default_stage = ProjectStage.objects.get(default=True)

    def setUp(self):
        print("Run Test Method:", self._testMethodName)

    def test_creation_project_with_file(self):
        """Test project creation with file by add button."""
        self.client.force_login(self.chief)
        # open project add view
        response = self.client.get(self.add_url, follow=True)
        self.assertEqual(response.status_code, 200, response.reason_phrase)
        data = get_adminform_initials(response)
        content = random()
        # fill the form
        data['name'] = 'Provide financial report'
        data['priority'] = Project.MIDDLE
        data['description'] = content
        data['responsible'] = [str(self.sergey.id)]
        file_name = add_file_to_form(self._testMethodName, data)
        # submit the form
        response = self.client.post(self.add_url, data, follow=True)
        self.assertEqual(response.status_code, 200, response.reason_phrase)
        self.assertNoFormErrors(response)
        data['common-thefile-content_type-object_id-0-file'].close()
        try:
            file = TheFile.objects.get(file__endswith=file_name)
        except TheFile.DoesNotExist as e:
            self.fail(e)
        file.file.delete()
        # notification email sent?
        self.assertEqual(len(mail.outbox), 1)
        self.assertEqual(mail.outbox[0].to, [self.sergey.email])
        mail.outbox = []
        self.assertEqual(self.changelist_url, response.redirect_chain[-1][0])
        project = Project.objects.get(description=content)
        change_url = reverse("site:tasks_project_change", args=(project.id,))
        response = self.client.get(change_url, follow=True)
        self.assertEqual(response.status_code, 200, response.reason_phrase)
        response = self.client.get(self.changelist_url, follow=True)
        self.assertEqual(response.status_code, 200, response.reason_phrase)

    def test_completed_button(self):
        content = random()
        project = Project.objects.create(
            name="Test collective project",
            priority=Project.HIGH,
            description=content,
            stage=self.default_stage,
            owner=self.chief,
            next_step="next_step"
        )
        project.responsible.set((self.sergey,))
        subscribers = USER_MODEL.objects.filter(
            groups__name="Global sales")
        project.subscribers.add(*subscribers)

        self.client.force_login(self.sergey)
        response = self.client.get(self.changelist_url, follow=True)
        self.assertEqual(response.status_code, 200, response.reason_phrase)
        self.assertIn(project, response.context['cl'].result_list)
        # print(response.context['cl'].result_list)

        change_url = reverse("site:tasks_project_change", args=(project.id,))
        response = self.client.get(change_url, follow=True)
        self.assertEqual(response.status_code, 200, response.reason_phrase)

        data = get_adminform_initials(response)
        data['_completed'] = ''
        data['responsible'] = [str(self.sergey.id)]
        data['subscribers'] = [str(u.id) for u in subscribers]
        response = self.client.post(change_url, data, follow=True)
        self.assertEqual(response.status_code, 200, response.reason_phrase)
        self.assertNoFormErrors(response)
        self.assertEqual(self.changelist_url, response.redirect_chain[-1][0])

    def test_fix_project_by_admin(self):
        project = Project.objects.create(
            name="Test collective project",
            priority=Project.HIGH,
            description='content',
            stage=self.default_stage,
            owner=self.chief,
            next_step="next_step"
        )
        project.responsible.set((self.sergey,))
        subscribers = USER_MODEL.objects.filter(
            groups__name="Global sales")
        project.subscribers.add(*subscribers)

        self.client.force_login(self.admin)
        change_url = reverse("admin:tasks_project_change", args=(project.id,))
        response = self.client.get(change_url, follow=True)
        self.assertEqual(response.status_code, 200, response.reason_phrase)
        data = get_adminform_initials(response)
        data['description'] = 'description'
        data['responsible'] = [str(self.sergey.id)]
        data['subscribers'] = [str(u.id) for u in subscribers]
        response = self.client.post(change_url, data, follow=True)
        self.assertNoFormErrors(response)
        self.assertEqual(response.status_code, 200, response.reason_phrase)
        changelist_url = reverse("admin:tasks_project_changelist")
        self.assertEqual(response.redirect_chain[0][0], changelist_url)

    def test_close_project(self):
        """Test for closing a project and sending notifications about it."""
        self.client.force_login(self.sergey)
        # open task add view
        response = self.client.get(self.add_url, follow=True)
        self.assertEqual(response.status_code, 200, response.reason_phrase)
        data = get_adminform_initials(response)
        content = random()
        # fill the form
        data['name'] = 'Test project for change and close'
        data['priority'] = Project.HIGH
        data['description'] = content
        data['responsible'] = [str(self.masha.id)]
        data['subscribers'] = [str(self.chief.id)]
        # submit the form
        response = self.client.post(self.add_url, data, follow=True)
        self.assertEqual(response.status_code, 200, response.reason_phrase)
        self.assertNoFormErrors(response)
        self.assertEqual(len(mail.outbox), 2)
        mail.outbox = []
        try:
            project = Project.objects.get(description=content, owner=self.sergey)
        except Project.DoesNotExist as e:
            self.fail(e)
        self.client.force_login(self.masha)
        change_url = project.get_absolute_url()
        response = self.client.get(change_url, follow=True)
        self.assertEqual(response.status_code, 200, response.reason_phrase)
        data = get_adminform_initials(response)
        # fill the form
        data['next_step'] = 'My final step'
        data['stage'] = str(ProjectStage.objects.get(done=True).id)
        data['subscribers'] = [self.chief.id]
        # submit the form
        response = self.client.post(change_url, data, follow=True)
        self.assertEqual(response.status_code, 200, response.reason_phrase)
        self.assertNoFormErrors(response)
        self.assertEqual(len(mail.outbox), 1)
        self.assertEqual(mail.outbox[0].to, [
                         self.chief.email, self.sergey.email])
        self.assertIn(project.name, mail.outbox[0].subject)
        mail.outbox = []
   
    def test_project_doesnt_exists(self):
        self.client.force_login(self.chief)
        self.obj_doesnt_exists(Project)
