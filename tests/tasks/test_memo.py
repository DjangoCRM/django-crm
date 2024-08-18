from random import random
from django.core import mail
from django.test import RequestFactory
from django.test import tag
from django.urls import reverse
from django.utils.translation import gettext as _

from common.utils.helpers import USER_MODEL
from tasks.models import Memo
from tasks.models import Project
from tasks.models import ProjectStage
from tasks.models import Task
from tasks.models import TaskStage
from tasks.site.memoadmin import MemoAdmin
from tasks.site.projectadmin import PROJECT_NEXT_STEP
from tasks.site.tasksbasemodeladmin import TASK_NEXT_STEP
from tests.base_test_classes import BaseTestCase
from tests.utils.helpers import add_file_to_form
from tests.utils.helpers import get_adminform_initials

# manage.py test tests.tasks.test_memo --keepdb


@tag('TestCase')
class TestMemo(BaseTestCase):
    """Test memo and creation task or project"""

    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()
        username_list = ("Garry.Chief", "Andrew.Manager.Global",
                         "Olga.Co-worker.Global", "Valeria.Operator.Global",
                         "Ekaterina.Task_operator", "Adam.Admin")
        users = USER_MODEL.objects.filter(
            username__in=username_list)
        cls.chief = users.get(username="Garry.Chief")
        cls.owner = users.get(username="Andrew.Manager.Global")
        cls.olga = users.get(username="Olga.Co-worker.Global")
        cls.valeria = users.get(username="Valeria.Operator.Global")
        cls.task_operator = users.get(username="Ekaterina.Task_operator")
        cls.admin = users.get(username="Adam.Admin")
        cls.add_url = reverse("site:tasks_memo_add")
        cls.memo_changelist_url = reverse("site:tasks_memo_changelist")
        cls.task_changelist_url = reverse('site:tasks_task_changelist')

    def setUp(self):
        print("Run Test Method:", self._testMethodName)
        self.factory = RequestFactory()
        # create memo
        self.content_id = random()
        self.memo = Memo.objects.create(
            name='Test memo',
            description=self.content_id,
            to=self.chief,
            owner=self.owner
        )
        self.memo_changeview_url = reverse(
            "site:tasks_memo_change",
            args=(self.memo.id,)
        )
        self.client.force_login(self.chief)
        # create a file

    def test_draft_memo_creation(self):
        self.client.force_login(self.owner)
        # open memo add view
        response = self.client.get(self.add_url, follow=True)
        self.assertEqual(response.status_code, 200, response.reason_phrase)
        data = get_adminform_initials(response)
        # add missing data
        content_id = random()
        data['name'] = 'Test draft memo'
        data['to'] = str(self.chief.id)
        data['description'] = content_id
        data['draft'] = True
        # submit form
        response = self.client.post(self.add_url, data, follow=True)
        self.assertEqual(response.status_code, 200, response.reason_phrase)
        try:
            memo = Memo.objects.get(description=content_id)
        except Memo.DoesNotExist:
            self.fail("The memo is not created")
        # notification email sent?
        self.assertEqual(len(mail.outbox), 0)
        mail.outbox = []

        self.client.force_login(self.chief)
        response = self.client.get(self.memo_changelist_url, follow=True)
        qs = response.context_data['cl'].queryset
        self.assertFalse(qs.contains(memo))
        self.client.force_login(self.task_operator)
        response = self.client.get(self.memo_changelist_url + "?to=all", follow=True)
        qs = response.context_data['cl'].queryset
        self.assertFalse(qs.contains(memo))
        self.client.force_login(self.admin)
        response = self.client.get(self.memo_changelist_url + "?to=all", follow=True)
        qs = response.context_data['cl'].queryset
        self.assertTrue(qs.contains(memo))

        self.client.force_login(self.owner)
        change_url = reverse("site:tasks_memo_change", args=(self.memo.id,))
        response = self.client.get(change_url, follow=True)
        self.assertEqual(response.status_code, 200, response.reason_phrase)
        data = get_adminform_initials(response)
        data['draft'] = False
        data['_save'] = ''
        response = self.client.post(change_url, data, follow=True)
        self.assertEqual(response.status_code, 200, response.reason_phrase)
        # notification email sent?
        self.assertEqual(len(mail.outbox), 1)
        self.assertEqual(mail.outbox[0].to[0], self.chief.email)
        mail.outbox = []
        response = self.client.post(change_url, data, follow=True)
        self.assertEqual(response.status_code, 200, response.reason_phrase)
        self.assertEqual(len(mail.outbox), 0)

    def test_memo_creation(self):
        """Test memo creation with file by add button."""
        self.client.force_login(self.owner)
        # open memo add view
        response = self.client.get(self.add_url, follow=True)
        self.assertEqual(response.status_code, 200, response.reason_phrase)
        data = get_adminform_initials(response)
        # add missing data
        content_id = random()
        data['name'] = 'Test memo'
        data['to'] = str(self.chief.id)
        data['description'] = content_id
        data['subscribers'] = [str(self.olga.id), str(self.valeria.id)]
        file_name = add_file_to_form(self._testMethodName, data)
        # submit form
        response = self.client.post(self.add_url, data, follow=True)
        self.assertEqual(response.status_code, 200, response.reason_phrase)
        self.assertEqual(response.redirect_chain[-1][0], self.memo_changelist_url)
        try:
            memo = Memo.objects.get(description=content_id)
            # Is the file attached?
            file = memo.files.first()
        except Memo.DoesNotExist:
            self.fail("The memo is not created")
        self.assertIn(file_name, file.file.name)

        # notification email sent?
        self.assertEqual(len(mail.outbox), 2)
        self.assertEqual(mail.outbox[0].to[0], self.chief.email)
        self.assertEqual(set(mail.outbox[1].to), {self.olga.email, self.valeria.email})
        self.assertIn(file.file.url, mail.outbox[0].body)
        file.file.delete()
        mail.outbox = []

    def test_memo_consideration(self):
        """Test memo consideration."""
        # open memo change view
        response = self.client.get(self.memo_changeview_url, follow=True)
        self.assertEqual(response.status_code, 200, response.reason_phrase)
        data = get_adminform_initials(response)
        data['stage'] = Memo.REVIEWED
        data['subscribers'] = [str(self.olga.id), str(self.valeria.id)]
        # submit form
        response = self.client.post(
            self.memo_changeview_url, data, follow=True)
        self.assertEqual(response.status_code, 200, response.reason_phrase)
        self.assertTrue(
            Memo.objects.filter(id=self.memo.id, stage=Memo.REVIEWED).exists(),
            "The memo is not reviewed"
        )
        # notification emails sent?
        self.assertEqual(len(mail.outbox), 2)
        email_set = {self.olga.email, self.valeria.email}
        self.assertEqual(set(mail.outbox[1].to), email_set)
        email_set.add(self.owner.email)
        self.assertEqual(set(mail.outbox[0].to), email_set)
        mail.outbox = []
        self.assertEqual(response.redirect_chain[-1][0], self.memo_changelist_url)

    def test_memo_consideration_with_task(self):
        """
        Test of consideration a memo with a file and 
        creation a task with the same file.
        """
        # open memo in change view
        response = self.client.get(self.memo_changeview_url, follow=True)
        self.assertEqual(response.status_code, 200, response.reason_phrase)
        data = get_adminform_initials(response)
        file_name = add_file_to_form(self._testMethodName, data)
        # submit "create task" button
        data['_create-task'] = ''
        data['stage'] = Memo.REVIEWED
        response = self.client.post(
            self.memo_changeview_url, data, follow=True)
        self.assertEqual(response.status_code, 200, response.reason_phrase)
        request = self.factory.post(self.memo_changeview_url, data)
        request.user = self.chief
        add_view_url = MemoAdmin.get_add_view_url(request, self.memo)
        self.assertEqual(add_view_url, response.redirect_chain[-1][0])

        data = get_adminform_initials(response)
        # set responsible and priority
        data['responsible'] = [str(self.olga.id), str(self.valeria.id)]
        data['priority'] = Task.MIDDLE

        response = self.client.post(add_view_url, data, follow=True)
        self.assertEqual(response.status_code, 200, response.reason_phrase)
        self.assertNoFormErrors(response)
        self.assertEqual(self.memo_changelist_url, response.redirect_chain[-1][0])
        try:
            task = Task.objects.get(
                name=self.memo.name,
                description__contains=self.content_id
            )
        except Task.DoesNotExist as err:
            self.fail(err)
        self.assertIn(self.owner, task.subscribers.all())
        file = task.files.first()
        self.assertIn(file_name, file.file.name)
        self.assertEqual(task.stage, TaskStage.objects.get(default=True))
        self.assertEqual(task.next_step, _(TASK_NEXT_STEP))
        self.memo.refresh_from_db()
        self.assertEqual(task.id, self.memo.task.id)
        # notification email sent?
        self.assertEqual(len(mail.outbox), 4)
        self.assertEqual(mail.outbox[0].to, [self.memo.owner.email])
        self.assertEqual(mail.outbox[1].to, [self.olga.email])
        self.assertEqual(mail.outbox[2].to, [self.valeria.email])
        self.assertEqual(mail.outbox[3].to, [self.memo.owner.email])
        self.assertIn(file.file.url, mail.outbox[0].body)
        file.file.delete()
        mail.outbox = []
        self.assertEqual(self.memo_changelist_url, response.redirect_chain[-1][0])
        response = self.client.get(self.memo_changeview_url, follow=True)
        self.assertEqual(response.status_code, 200, response.reason_phrase)

        response = self.client.get(self.memo_changelist_url, follow=True)
        self.assertEqual(response.status_code, 200, response.reason_phrase)
        response = self.client.get(self.task_changelist_url, follow=True)
        self.assertEqual(response.status_code, 200, response.reason_phrase)

    def test_memo_consideration_with_task_and_another_file(self):
        """
        Test of consideration a memo with a file and 
        creation a task with another file.
        """
        # open memo in change view
        response = self.client.get(self.memo_changeview_url, follow=True)
        self.assertEqual(response.status_code, 200, response.reason_phrase)
        data = get_adminform_initials(response)
        file_name1 = add_file_to_form(self._testMethodName, data)
        # submit "create task" button
        data['_create-task'] = ''
        response = self.client.post(
            self.memo_changeview_url, data, follow=True)
        self.assertEqual(response.status_code, 200, response.reason_phrase)
        request = self.factory.post(self.memo_changeview_url, data)
        request.user = self.chief
        add_view_url = MemoAdmin.get_add_view_url(request, self.memo)
        self.assertEqual(add_view_url, response.redirect_chain[-1][0])
        data['common-thefile-content_type-object_id-0-file'].close()

        data = get_adminform_initials(response)
        # set responsible and priority
        data['responsible'] = [str(self.olga.id), str(self.valeria.id)]
        data['priority'] = Task.MIDDLE
        del data[file_name1]
        # submit "save and continue" button
        data['_continue'] = ''
        file_name2 = add_file_to_form(self._testMethodName, data)
        response = self.client.post(add_view_url, data, follow=True)
        self.assertEqual(response.status_code, 200, response.reason_phrase)
        self.assertNoFormErrors(response)
        data['common-thefile-content_type-object_id-0-file'].close()
        file = self.memo.files.first()
        file.file.delete()
        try:
            task = Task.objects.get(
                name=self.memo.name,
                description__contains=self.content_id
            )
        except Task.DoesNotExist as err:
            self.fail(err)
        self.assertIn(
            reverse('site:tasks_task_change', args=(task.id,)),
            response.redirect_chain[-1][0]
        )
        self.assertIn(self.owner, task.subscribers.all())
        file = task.files.first()
        self.assertNotIn(file_name1, file.file.name)
        self.assertIn(file_name2, file.file.name)
        file.file.delete()

    def test_memo_consideration_with_project(self):
        """
        Test of consideration a memo with a file and 
        creation a project with the same file.
        """
        # open memo in change view
        response = self.client.get(self.memo_changeview_url, follow=True)
        self.assertEqual(response.status_code, 200, response.reason_phrase)
        data = get_adminform_initials(response)
        file_name = add_file_to_form(self._testMethodName, data)
        # submit "create project" button
        data['_create-project'] = ''
        response = self.client.post(
            self.memo_changeview_url, data, follow=True)
        self.assertEqual(response.status_code, 200, response.reason_phrase)
        request = self.factory.post(self.memo_changeview_url, data)
        request.user = self.chief
        add_view_url = MemoAdmin.get_add_view_url(request, self.memo)
        self.assertEqual(add_view_url, response.redirect_chain[-1][0])

        data = get_adminform_initials(response)
        # set responsible and priority
        data['responsible'] = [str(self.olga.id), str(self.valeria.id)]
        data['priority'] = Project.MIDDLE

        response = self.client.post(add_view_url, data, follow=True)
        self.assertEqual(response.status_code, 200, response.reason_phrase)
        self.assertNoFormErrors(response)
        self.assertEqual(self.memo_changelist_url, response.redirect_chain[-1][0])
        try:
            project = Project.objects.get(
                name=self.memo.name,
                description__contains=self.content_id
            )
        except Project.DoesNotExist as err:
            self.fail(err)
        self.assertIn(self.owner, project.subscribers.all())
        file = project.files.first()
        self.assertIn(file_name, file.file.name)
        self.assertEqual(project.stage, ProjectStage.objects.get(default=True))
        self.assertEqual(project.next_step, _(PROJECT_NEXT_STEP))
        # notification emails sent?
        self.assertEqual(len(mail.outbox), 4)
        self.assertEqual(mail.outbox[0].to, [self.memo.owner.email])
        self.assertEqual(mail.outbox[1].to, [self.olga.email])
        self.assertEqual(mail.outbox[2].to, [self.valeria.email])
        self.assertEqual(mail.outbox[3].to, [self.memo.owner.email])
        self.assertIn(file.file.url, mail.outbox[0].body)
        file.file.delete()
        mail.outbox = []
        self.assertEqual(self.memo_changelist_url, response.redirect_chain[-1][0])
        response = self.client.get(self.memo_changeview_url, follow=True)
        self.assertEqual(response.status_code, 200, response.reason_phrase)
        response = self.client.get(self.memo_changelist_url, follow=True)
        self.assertEqual(response.status_code, 200, response.reason_phrase)
        response = self.client.get(self.task_changelist_url, follow=True)
        self.assertEqual(response.status_code, 200, response.reason_phrase)

    def test_memo_doesnt_exists(self):
        self.obj_doesnt_exists(Memo)

    def test_memo_consideration_with_project_and_another_file(self):
        """
        Test of consideration a memo with a file and 
        creation a project with another file.
        """
        # open memo in change view
        response = self.client.get(self.memo_changeview_url, follow=True)
        self.assertEqual(response.status_code, 200, response.reason_phrase)
        data = get_adminform_initials(response)
        file_name1 = add_file_to_form(self._testMethodName, data)
        # submit "create task" button
        data['_create-project'] = ''
        response = self.client.post(
            self.memo_changeview_url, data, follow=True)
        self.assertEqual(response.status_code, 200, response.reason_phrase)
        request = self.factory.post(self.memo_changeview_url, data)
        request.user = self.chief
        add_view_url = MemoAdmin.get_add_view_url(request, self.memo)
        self.assertEqual(add_view_url, response.redirect_chain[-1][0])
        data['common-thefile-content_type-object_id-0-file'].close()

        data = get_adminform_initials(response)
        # set responsible and priority
        data['responsible'] = [str(self.olga.id), str(self.valeria.id)]
        data['priority'] = Task.MIDDLE
        del data[file_name1]
        # submit "save and continue" button
        data['_continue'] = ''
        file_name2 = add_file_to_form(self._testMethodName, data)
        response = self.client.post(add_view_url, data, follow=True)
        self.assertEqual(response.status_code, 200, response.reason_phrase)
        self.assertNoFormErrors(response)
        data['common-thefile-content_type-object_id-0-file'].close()
        file = self.memo.files.first()
        file.file.delete()
        try:
            project = Project.objects.get(
                name=self.memo.name,
                description__contains=self.content_id
            )
        except Project.DoesNotExist as err:
            self.fail(err)
        self.assertIn(
            reverse('site:tasks_project_change', args=(project.id,)),
            response.redirect_chain[-1][0]
        )
        self.assertIn(self.owner, project.subscribers.all())
        file = project.files.first()
        self.assertNotIn(file_name1, file.file.name)
        self.assertIn(file_name2, file.file.name)
        file.file.delete()
