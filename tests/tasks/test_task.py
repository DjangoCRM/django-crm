from datetime import timedelta
from random import random
from django.core import mail
from django.db.models import Q
from django.test import RequestFactory
from django.test import tag
from django.test import override_settings
from django.urls import reverse
from django.utils.formats import date_format
from django.utils.translation import override

from common.models import TheFile
from common.utils.helpers import get_active_users
from common.utils.helpers import get_trans_for_lang
from common.utils.helpers import USER_MODEL
from common.utils.helpers import get_today
from common.utils.usermiddleware import set_user_groups
from tasks.site.taskadmin import TaskAdmin
from tasks.site.tasksbasemodeladmin import subscribers_subject
from tasks.site.tasksbasemodeladmin import TASK_IS_CLOSED_str
from tasks.site.tasksbasemodeladmin import TasksBaseModelAdmin
from tasks.models import Task
from tasks.models import TaskStage
from tests.base_test_classes import BaseTestCase
from tests.utils.helpers import add_file_to_form
from tests.utils.helpers import get_adminform_initials

# manage.py test tests.tasks.test_task --keepdb


@tag('TestCase')
class TestTask(BaseTestCase):
    """Test task"""
    fixtures = (
        'currency.json', 'test_country.json', 'resolution.json',
        'groups.json', 'department.json', 'test_users.json',
        'projectstage.json', 'taskstage.json',
    )

    @classmethod
    @override_settings(LANGUAGE_CODE='en')
    def setUpTestData(cls):
        super().setUpTestData()
        username_list = ("Garry.Chief", "Sergey.Co-worker.Head.Bookkeeping",
                         "Masha.Co-worker.Bookkeeping", "Eve.Superoperator.Co-worker")
        users = USER_MODEL.objects.filter(
            username__in=username_list)
        cls.chief = users.get(username="Garry.Chief")
        cls.sergey = users.get(
            username="Sergey.Co-worker.Head.Bookkeeping")
        cls.masha = users.get(
            username="Masha.Co-worker.Bookkeeping")
        cls.eve = users.get(
            username="Eve.Superoperator.Co-worker")
        cls.changelist_url = reverse('site:tasks_task_changelist')
        cls.add_url = reverse("site:tasks_task_add")
        cls.default_stage = TaskStage.objects.get(default=True)
        cls.done_stage = TaskStage.objects.get(done=True)
        cls.factory = RequestFactory()

    def setUp(self):
        print(" Run Test Method:", self._testMethodName)

    def test_co_owner_task(self):
        """Checking the appointment of the head of the department
         as co-owners of the task"""
        self.client.force_login(self.masha)
        # open task add view
        response = self.client.get(self.add_url, follow=True)
        self.assertEqual(response.status_code, 200, response.reason_phrase)
        data = get_adminform_initials(response)
        # fill the form
        data['name'] = 'Provide financial report'
        response = self.client.post(self.add_url, data, follow=True)
        self.assertEqual(response.status_code, 200, response.reason_phrase)
        self.assertNoFormErrors(response)
        self.assertTrue(
            Task.objects.filter(
                name='Provide financial report',
                owner=self.masha,
                co_owner=self.sergey,
            ).exists(),
            "The task DoesNotExist"
        )

    def test_creation_task_with_file(self):
        """Test task creation with file by add button."""
        self.client.force_login(self.chief)
        # open task add view
        response = self.client.get(self.add_url, follow=True)
        self.assertEqual(response.status_code, 200, response.reason_phrase)
        data = get_adminform_initials(response)
        content = random()
        # fill the form
        data['name'] = 'Provide financial report'
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
        # notification email sent?
        self.assertEqual(len(mail.outbox), 1)
        self.assertEqual(mail.outbox[0].to, [self.sergey.email])
        self.assertIn(file.file.url, mail.outbox[0].body)
        file.file.delete()
        mail.outbox = []
        self.assertEqual(self.changelist_url, response.redirect_chain[-1][0])
        task = Task.objects.get(description=content)
        change_url = reverse("site:tasks_task_change", args=(task.id,))
        response = self.client.get(change_url, follow=True)
        self.assertEqual(response.status_code, 200, response.reason_phrase)
        response = self.client.get(self.changelist_url, follow=True)
        self.assertEqual(response.status_code, 200, response.reason_phrase)

    def test_subtask_completed_in_email(self):
        """Create completed subtask by email"""
        self.client.force_login(self.chief)
        # open task add view
        response = self.client.get(self.add_url, follow=True)
        self.assertEqual(response.status_code, 200, response.reason_phrase)
        data = get_adminform_initials(response)
        # fill the form
        name = 'Create completed subtask by email'
        data['name'] = name
        data['description'] = 'description'
        data['responsible'] = [str(self.sergey.id), str(self.masha.id)]
        # submit the form
        response = self.client.post(self.add_url, data, follow=True)
        self.assertEqual(response.status_code, 200, response.reason_phrase)
        self.assertNoFormErrors(response)
        try:
            task = Task.objects.get(name=name, owner=self.chief)
        except Exception as err:
            self.fail(err)
        # notification email sent?
        self.assertEqual(len(mail.outbox), 2)
        msg = mail.outbox[0]
        self.assertEqual(msg.to, [self.sergey.email])
        msg = mail.outbox[1]
        self.assertEqual(msg.to, [self.masha.email])
        mail.outbox = []
        complete_url = reverse("email-subtask_completed", args=(task.token, self.masha.id))
        self.assertIn(complete_url[4:], msg.body)
        self.client.logout()
        response = self.client.get(complete_url, follow=True)
        self.assertEqual(response.status_code, 200, response.reason_phrase)
        try:
            subtask = Task.objects.get(
                name=name,
                task=task,
                stage=self.done_stage,
                owner=self.masha
            )
        except Exception as err:
            self.fail(err)
        self.assertEqual(subtask.stage.done, True)
        self.assertEqual(mail.outbox[0].to, [self.sergey.email])
        self.assertEqual(mail.outbox[1].to, [task.owner.email])

    def test_task_completed_in_email(self):
        """Mark the task as completed in the email"""
        self.client.force_login(self.chief)
        # open task add view
        response = self.client.get(self.add_url, follow=True)
        self.assertEqual(response.status_code, 200, response.reason_phrase)
        data = get_adminform_initials(response)
        # fill the form
        name = 'Mark the task as completed in the email'
        data['name'] = name
        data['description'] = 'description'
        data['responsible'] = [str(self.sergey.id)]
        # submit the form
        response = self.client.post(self.add_url, data, follow=True)
        self.assertEqual(response.status_code, 200, response.reason_phrase)
        self.assertNoFormErrors(response)
        try:
            task = Task.objects.get(name=name)
        except Exception as err:
            self.fail(err)

        # notification email sent?
        self.assertEqual(len(mail.outbox), 1)
        msg = mail.outbox[0]
        self.assertEqual(msg.to, [self.sergey.email])
        mail.outbox = []
        complete_url = reverse("task_completed", args=(task.token, self.sergey.id))
        self.assertIn(complete_url[4:], msg.body)
        self.client.logout()
        response = self.client.get(complete_url, follow=True)
        self.assertEqual(response.status_code, 200, response.reason_phrase)
        task.refresh_from_db()
        self.assertEqual(task.stage.done, True)
        self.assertEqual(mail.outbox[0].to, [task.owner.email])
        
    def test_completed_button(self):
        content = random()
        task = Task.objects.create(
            name="Test collective task",
            priority='1',
            description=content,
            stage=self.default_stage,
            owner=self.chief,
            next_step="next_step"
        )
        task.responsible.set((self.sergey,))
        subscribers = USER_MODEL.objects.filter(
            groups__name="Global sales")
        task.subscribers.add(*subscribers)

        self.client.force_login(self.sergey)
        response = self.client.get(self.changelist_url, follow=True)
        self.assertEqual(response.status_code, 200, response.reason_phrase)
        self.assertIn(task, response.context['cl'].result_list)

        change_url = reverse("site:tasks_task_change", args=(task.id,))
        response = self.client.get(change_url, follow=True)
        self.assertEqual(response.status_code, 200, response.reason_phrase)

        data = get_adminform_initials(response)
        data['_completed'] = ''
        response = self.client.post(change_url, data, follow=True)
        self.assertEqual(response.status_code, 200, response.reason_phrase)
        self.assertNoFormErrors(response)
        self.assertEqual(self.changelist_url, response.redirect_chain[-1][0])
        self.assertNotIn(task, response.context['cl'].result_list)

    def test_fix_task_by_admin(self):
        task = Task.objects.create(
            name="Test collective task",
            priority='1',
            description='content',
            stage=self.default_stage,
            owner=self.chief,
            next_step="next_step"
        )
        task.responsible.set((self.sergey,))
        subscribers = USER_MODEL.objects.filter(
            groups__name="Global sales")
        task.subscribers.add(*subscribers)

        admin = USER_MODEL.objects.get(username="Adam.Admin")
        self.client.force_login(admin)
        change_url = reverse("admin:tasks_task_change", args=(task.id,))
        response = self.client.get(change_url, follow=True)
        self.assertEqual(response.status_code, 200, response.reason_phrase)
        data = get_adminform_initials(response)
        data['description'] = 'description'
        # data['responsible'] = [str(self.sergey.id)]
        # data['subscribers'] = [str(u.id) for u in subscribers]
        response = self.client.post(change_url, data, follow=True)
        self.assertNoFormErrors(response)
        self.assertEqual(response.status_code, 200, response.reason_phrase)
        changelist_url = reverse("admin:tasks_task_changelist")
        self.assertEqual(response.redirect_chain[0][0], changelist_url)

    def test_completed_button_in_main_task(self):
        """Test gray completed button in main task"""
        task = self.creat_task()
        task.responsible.set((self.sergey, self.masha))
        subscribers = USER_MODEL.objects.filter(
            groups__name="Global sales")
        task.subscribers.add(*subscribers)

        self.client.force_login(self.sergey)
        response = self.client.get(self.changelist_url, follow=True)
        self.assertEqual(response.status_code, 200, response.reason_phrase)
        self.assertIn(task, response.context['cl'].result_list)

        change_url = reverse("site:tasks_task_change", args=(task.id,))
        response = self.client.get(change_url, follow=True)
        self.assertEqual(response.status_code, 200, response.reason_phrase)

        completed_button_url = reverse(
            "create_completed_subtask", args=(task.id,))
        response = self.client.get(completed_button_url, follow=True)
        self.assertEqual(response.status_code, 200, response.reason_phrase)
        response = self.client.get(self.changelist_url, follow=True)
        self.assertEqual(response.status_code, 200, response.reason_phrase)
        self.assertNotIn(task, response.context['cl'].result_list)

    def test_close_task(self):
        """Test for closing a task and sending notifications about it."""
        self.sergey.profile.language_code = 'uk'
        self.sergey.profile.save(update_fields=['language_code'])
        self.client.force_login(self.sergey)
        # open add task view in uk language
        add_url = '/uk/' + self.add_url[4:]
        with override('uk'):
            response = self.client.get(add_url, follow=True)
            self.assertEqual(response.status_code, 200, response.reason_phrase)
            data = get_adminform_initials(response)
            content = random()
            # fill the form
            data['name'] = 'Test task for change and close'
            data['description'] = content
            data['responsible'] = [str(self.masha.id)]
            data['subscribers'] = [str(self.chief.id)]
            # submit the form
            response = self.client.post(add_url, data, follow=True)
            self.assertEqual(response.status_code, 200, response.reason_phrase)
            self.assertNoFormErrors(response)
            self.assertEqual(len(mail.outbox), 2)
            mail.outbox = []
            try:
                task = Task.objects.get(description=content, owner=self.sergey)
            except Task.DoesNotExist as e:
                self.fail(e)
            
        self.client.force_login(self.masha)
        change_url = task.get_absolute_url()
        response = self.client.get(change_url, follow=True)
        self.assertEqual(response.status_code, 200, response.reason_phrase)
        data = get_adminform_initials(response)
        # fill the form
        data['next_step'] = 'My final step'
        data['stage'] = str(self.done_stage.id)
        # submit the form
        response = self.client.post(change_url, data, follow=True)
        self.assertEqual(response.status_code, 200, response.reason_phrase)
        self.assertNoFormErrors(response)
        self.assertEqual(len(mail.outbox), 2)
        self.assertEqual(mail.outbox[0].to, [self.sergey.email])
        uk_subj = get_trans_for_lang(TASK_IS_CLOSED_str, 'uk')
        en_subj = get_trans_for_lang(TASK_IS_CLOSED_str, 'en')
        self.assertNotEqual(uk_subj, en_subj)
        self.assertIn(uk_subj, mail.outbox[0].subject)
        self.assertEqual(mail.outbox[1].to, [self.chief.email])
        self.assertIn(task.name, mail.outbox[0].subject)
        mail.outbox = []

    def test_deactivating_supertask(self):
        main_task, masha_subtask, sergey_subtask = self.creat_task_with_subtasks()
        main_task.responsible.add(self.eve)

        self.client.force_login(self.masha)
        change_url = masha_subtask.get_absolute_url()
        response = self.client.get(change_url, follow=True)
        self.assertEqual(response.status_code, 200, response.reason_phrase)
        data = get_adminform_initials(response)
        data['_completed'] = ''
        response = self.client.post(change_url, data, follow=True)
        self.assertEqual(response.status_code, 200, response.reason_phrase)
        self.assertNoFormErrors(response)
        self.assertEqual(self.changelist_url, response.redirect_chain[-1][0])

        self.client.force_login(self.sergey)
        change_url = sergey_subtask.get_absolute_url()
        response = self.client.get(change_url, follow=True)
        self.assertEqual(response.status_code, 200, response.reason_phrase)
        data = get_adminform_initials(response)
        data['_completed'] = ''
        # the file for copy to the main task
        file_name = add_file_to_form(self._testMethodName, data)
        response = self.client.post(change_url, data, follow=True)
        self.assertEqual(response.status_code, 200, response.reason_phrase)
        self.assertNoFormErrors(response)
        self.assertEqual(self.changelist_url, response.redirect_chain[-1][0])
        data['common-thefile-content_type-object_id-0-file'].close()
        try:
            subtask_file = TheFile.objects.get(
                file__endswith=file_name,
                object_id=sergey_subtask.id
            )
            subtask_file.file.delete()
        except TheFile.DoesNotExist as e:
            self.fail(e)

        # use gray completed button in main task
        self.client.force_login(self.eve)
        completed_button_url = reverse(
            "create_completed_subtask", args=(main_task.id,))
        response = self.client.get(completed_button_url, follow=True)
        self.assertEqual(response.status_code, 200, response.reason_phrase)

        main_task.refresh_from_db()
        self.assertIs(main_task.active, False)
        self.assertIs(main_task.stage.done, True)
        try:
            main_task_file = TheFile.objects.get(
                file__endswith=file_name,
                object_id=main_task.id
            )
            main_task_file.file.delete()
        except TheFile.DoesNotExist as e:
            self.fail(e)

    def test_task_sequence_in_changelist_view(self):
        task = self.creat_task()
        task.name = "Single task"
        task.save(update_fields=['name'])

        main_task, masha_subtask, sergey_subtask = self.creat_task_with_subtasks()

        self.client.force_login(self.chief)
        response = self.client.get(self.changelist_url, follow=True)
        self.assertEqual(response.status_code, 200, response.reason_phrase)
        queryset = response.context_data['cl'].queryset

        self.assertQuerySetEqual(queryset, (main_task, sergey_subtask, masha_subtask, task))
        # toggle default task sorting
        url = reverse("toggle_default_sorting")
        toggle_sorting_url = f"{url}?model=Task&next_url={self.changelist_url}"
        response = self.client.get(toggle_sorting_url, follow=True)
        self.assertEqual(response.status_code, 200, response.reason_phrase)
        self.assertEqual(self.changelist_url, response.redirect_chain[-1][0]) 
        response = self.client.get(self.changelist_url, follow=True)
        self.assertEqual(response.status_code, 200, response.reason_phrase)
        queryset = response.context_data['cl'].queryset             
        self.assertQuerySetEqual(queryset, (task, main_task, masha_subtask, sergey_subtask))
                
        response = self.client.get(self.changelist_url + "?active=all", follow=True)
        self.assertEqual(response.status_code, 200, response.reason_phrase)
        queryset = response.context_data['cl'].queryset
        self.assertQuerySetEqual(queryset, (main_task, sergey_subtask, masha_subtask, task))

    def test_create_subtask_for_another(self):
        """Create subtask for another person"""
        now_date = get_today()
        later_date = now_date + timedelta(days=3)
        task = Task.objects.create(
            name="Task for another person",
            priority=Task.HIGH,
            stage=self.default_stage,
            owner=self.chief
        )
        task.responsible.add(self.sergey)

        # responsible department head creates a task for his subordinate employee
        self.client.force_login(self.sergey)
        change_url = task.get_absolute_url()
        response = self.client.get(change_url, follow=True)
        self.assertEqual(response.status_code, 200, response.reason_phrase)
        data = get_adminform_initials(response)
        # fill the form
        data['next_step'] = 'Next step'
        data['due_date'] = date_format(now_date, format="SHORT_DATE_FORMAT")
        data['_create-task'] = ''
        # submit the form
        response = self.client.post(change_url, data, follow=True)
        self.assertEqual(response.status_code, 200, response.reason_phrase)
        self.assertNoFormErrors(response)
        request = self.factory.post(change_url, data)
        request.user = self.sergey
        add_view_url = TasksBaseModelAdmin.get_add_view_url(request, task)
        self.assertEqual(add_view_url, response.redirect_chain[-1][0])

        data = get_adminform_initials(response)
        # fill the form
        content = random()
        data['name'] = "Task for Masha"
        data['due_date'] = date_format(now_date, format="SHORT_DATE_FORMAT")
        data['description'] = content
        data['responsible'] = [str(self.masha.id)]
        data['priority'] = Task.MIDDLE
        # submit the form
        response = self.client.post(add_view_url, data, follow=True)
        self.assertEqual(response.status_code, 200, response.reason_phrase)
        self.assertNoFormErrors(response)
        self.assertEqual(
            reverse('site:tasks_task_changelist'),
            response.redirect_chain[-1][0]
        )
        try:
            new_task = Task.objects.get(
                name="Task for Masha",
                description=content,
                task=task, owner=self.sergey,
                responsible=self.masha
            )
        except Task.DoesNotExist as e:
            self.fail(e)

        self.assertEqual(new_task.stage, TaskStage.objects.get(default=True))

        new_change_url = new_task.get_absolute_url()
        self.client.force_login(self.masha)
        response = self.client.get(new_change_url)
        self.assertEqual(response.status_code, 200, response.reason_phrase)
        data = get_adminform_initials(response)
        # fill the form
        data['next_step'] = "My next step"
        data['next_step_date'] = date_format(
            later_date, format="SHORT_DATE_FORMAT")
        # submit the form
        response = self.client.post(new_change_url, data, follow=True)
        self.assertEqual(response.status_code, 200, response.reason_phrase)
        self.assertNoFormErrors(response)
        new_task.refresh_from_db()
        self.assertEqual(new_task.next_step, "My next step")
        response = self.client.get(response.redirect_chain[0][0])
        self.assertEqual(response.status_code, 200, response.reason_phrase)
        # self.assertContains(response, NEXT_STEP_DATE_WARNING)
        mail.outbox = []

    def test_cannot_create_task_for_another(self):
        # an employee who is not a chief or department head cannot
        # create a task for another employee
        self.client.force_login(self.masha)
        response = self.client.get(self.add_url, follow=True)
        self.assertEqual(response.status_code, 200, response.reason_phrase)
        data = get_adminform_initials(response)
        # fill the form
        data['name'] = "Masha's task"
        data['responsible'] = [str(self.sergey.id)]
        data['_continue'] = ''
        # submit the form
        response = self.client.post(self.add_url, data, follow=True)
        self.assertEqual(response.status_code, 200, response.reason_phrase)
        errors = response.context.get('errors')
        self.assertIn("Select a valid choice.", errors[0][0])

        # try to add a responsible in own task
        response = self.client.get(self.add_url, follow=True)
        data = get_adminform_initials(response)
        data['name'] = "Masha's task"
        data['_continue'] = ''
        response = self.client.post(self.add_url, data, follow=True)
        self.assertEqual(response.status_code, 200, response.reason_phrase)
        self.assertNoFormErrors(response)
        data = get_adminform_initials(response)
        data['responsible'].append(str(self.sergey.id))
        data['_continue'] = ''
        change_url = response.redirect_chain[-1][0]
        response = self.client.post(change_url, data, follow=True)
        self.assertEqual(response.status_code, 200, response.reason_phrase)
        errors = response.context.get('errors')
        self.assertIn("Select a valid choice.", errors[0][0])

    def test_task_doesnt_exists(self):
        chief = USER_MODEL.objects.get(username="Garry.Chief")
        self.client.force_login(chief)
        self.obj_doesnt_exists(Task)

    def test_subtask_completion_notification(self):
        main_task = self.creat_task()   # owner self.chief
        main_task.responsible.add(self.eve) # responsible [self.sergey, self.masha]

        self.client.force_login(self.eve)
        change_url = main_task.get_absolute_url()
        response = self.client.get(change_url, follow=True)
        self.assertEqual(response.status_code, 200, response.reason_phrase)
        
        add_subtask_url = TaskAdmin.get_add_subtask_url(main_task.id)
        self.assertEqual(add_subtask_url, response.context_data['add_subtask_url'])
        response = self.client.get(add_subtask_url, follow=True)
        self.assertEqual(response.status_code, 200, response.reason_phrase)
        data = get_adminform_initials(response)
        data['name'] = "Eve's task"
        data['_continue'] = ''
        # test queryset & initial of responsible form field
        queryset, initials = self.get_responsible_field_data(
            self.eve, add_subtask_url, response.resolver_match)
        responsible = main_task.responsible.all().order_by("username")
        self.assertQuerySetEqual(queryset, responsible)
        self.assertEqual(initials, [self.eve.id])
        # submit the form
        response = self.client.post(add_subtask_url, data, follow=True)
        self.assertEqual(response.status_code, 200, response.reason_phrase)
        self.assertNoFormErrors(response)
        self.assertEqual(len(mail.outbox), 2)
        # subscription notifications
        self.assertEqual(set(mail.outbox[0].to), {self.sergey.email, self.masha.email})
        self.assertEqual(mail.outbox[1].to, [self.chief.email])
        mail.outbox = []
        change_url = response.redirect_chain[-1][0]
        response = self.client.get(change_url, follow=True)
        self.assertEqual(response.status_code, 200, response.reason_phrase)
        data = get_adminform_initials(response)
        data['hide_main_task'] = True
        data['stage'] = str(self.done_stage.id)
        response = self.client.post(change_url, data, follow=True)
        self.assertEqual(response.status_code, 200, response.reason_phrase)
        self.assertNoFormErrors(response)

        # completed task notifications
        self.assertEqual(len(mail.outbox), 1)
        self.assertEqual(set(mail.outbox[0].to), {self.sergey.email, self.masha.email, self.chief.email})
        mail.outbox = []        
                
        self.client.force_login(self.masha)
        response = self.client.get(add_subtask_url, follow=True)
        self.assertEqual(response.status_code, 200, response.reason_phrase)
        data = get_adminform_initials(response)
        data['name'] = "Masha's task"
        data['_continue'] = ''
        # test queryset & initial of responsible form field
        queryset, initials = self.get_responsible_field_data(
            self.masha, add_subtask_url, response.resolver_match)
        self.assertQuerySetEqual(queryset, responsible)
        self.assertEqual(initials, [self.masha.id])

        sergey_code = self.sergey.profile.language_code
        self.sergey.profile.language_code = 'uk'
        self.sergey.profile.save(update_fields=['language_code'])

        # submit the form
        response = self.client.post(add_subtask_url, data, follow=True)
        self.assertEqual(response.status_code, 200, response.reason_phrase)
        self.assertNoFormErrors(response)
        # subscription notifications
        self.assertEqual(len(mail.outbox), 2)
        self.assertNotIn(self.eve.email, mail.outbox[0].to)
        uk_subj = get_trans_for_lang(subscribers_subject, 'uk')
        en_subj = get_trans_for_lang(subscribers_subject, 'en')
        self.assertNotEqual(uk_subj, en_subj)
        self.assertIn(uk_subj, mail.outbox[0].subject)
        mail.outbox = []
        change_url = response.redirect_chain[-1][0]
        response = self.client.get(change_url, follow=True)
        self.assertEqual(response.status_code, 200, response.reason_phrase)
        data = get_adminform_initials(response)
        data['stage'] = str(self.done_stage.id)
        response = self.client.post(change_url, data, follow=True)
        self.assertEqual(response.status_code, 200, response.reason_phrase)
        self.assertNoFormErrors(response)
        # completed task notifications
        self.assertEqual(len(mail.outbox), 2)
        self.assertNotIn(self.eve.email, mail.outbox[0].to)
        mail.outbox = []

        self.client.force_login(self.sergey)
        response = self.client.get(add_subtask_url, follow=True)
        self.assertEqual(response.status_code, 200, response.reason_phrase)
        data = get_adminform_initials(response)
        data['name'] = "Sergey's task"
        data['_continue'] = ''
        # test queryset & initial of responsible form field
        queryset, initials = self.get_responsible_field_data(
            self.sergey, add_subtask_url, response.resolver_match
        )
        users = get_active_users()
        department_users = users.filter(
            groups=self.sergey.department_id
        )
        responsible = users.filter(
            Q(id__in=responsible) | Q(id__in=department_users)
        )
        self.assertQuerySetEqual(queryset, responsible, ordered=False)
        self.assertIsNone(initials)

        # Sergey uses the grey "Completed" button in the main task
        change_url = main_task.get_absolute_url()
        response = self.client.get(change_url, follow=True)
        self.assertEqual(response.status_code, 200, response.reason_phrase)
        completed_button_url = reverse(
            "create_completed_subtask", args=(main_task.id,))
        self.assertContains(response, completed_button_url)
        response = self.client.get(completed_button_url, follow=True)
        self.assertEqual(response.status_code, 200, response.reason_phrase)

        # subscription notifications (Eve uses 'hide_main_task')
        self.assertEqual([self.masha.email], mail.outbox[0].to)
        # notice of appointment as co-owner
        self.assertEqual([self.chief.email], mail.outbox[1].to)
        # completed task notifications
        self.assertEqual([self.chief.email, self.masha.email], mail.outbox[2].to)
        mail.outbox = []
        self.sergey.profile.language_code = sergey_code
        self.sergey.profile.save(update_fields=['language_code'])

    def test_create_task_for_yourself(self):
        # user is not department head
        self.client.force_login(self.masha)
        response = self.client.get(self.add_url, follow=True)
        # test queryset & initial of responsible form field
        queryset, initials = self.get_responsible_field_data(
            self.masha, self.add_url, response.resolver_match
        )
        self.assertEqual(list(queryset), [self.masha])
        self.assertEqual(initials, [self.masha.id])

        content = random()
        data = get_adminform_initials(response)
        data['name'] = "Masha's task"
        data['description'] = content
        response = self.client.post(self.add_url, data, follow=True)
        self.assertEqual(response.status_code, 200, response.reason_phrase)
        self.assertNoFormErrors(response)
        self.assertEqual(
            reverse('site:tasks_task_changelist'),
            response.redirect_chain[-1][0]
        )
        self.assertTrue(
            Task.objects.filter(
                name="Masha's task",
                description=content,
                owner=self.masha,
                responsible=self.masha
            ).exists(),
            "The task DoesNotExist"
        )

    def test_create_subtask_for_not_responsible(self):
        """Test of creating a subtask for users who are
         not responsible in the main task."""
        main_task = self.creat_task()
        tanya = USER_MODEL.objects.get(
            username="Tanya.Co-worker.Bookkeeping")

        for user in (self.chief, self.sergey):
            self.client.force_login(user)
            add_subtask_url = TaskAdmin.get_add_subtask_url(main_task.id)
            response = self.client.get(add_subtask_url, follow=True)
            self.assertEqual(response.status_code, 200, response.reason_phrase)
            content = random()
            data = get_adminform_initials(response)
            data['name'] = "Tanya's task"
            data['description'] = content
            data['responsible'] = [str(tanya.id)]
            response = self.client.post(add_subtask_url, data, follow=True)
            self.assertEqual(response.status_code, 200, response.reason_phrase)
            self.assertNoFormErrors(response)
            self.assertTrue(
                Task.objects.filter(
                    name="Tanya's task",
                    description=content,
                    responsible=tanya,
                    owner=user
                ).exists(),
                "The task DoesNotExist"
            )

        self.client.force_login(tanya)
        response = self.client.get(self.changelist_url, follow=True)
        self.assertEqual(response.status_code, 200, response.reason_phrase)
        queryset = response.context_data['cl'].queryset
        self.assertEqual(queryset.count(), 2)

    def creat_task(self) -> Task:
        content = random()
        task = Task.objects.create(
            name="Test task for create subtask",
            priority=Task.HIGH,
            description=content,
            stage=self.default_stage,
            owner=self.chief
        )
        task.responsible.add(self.sergey, self.masha)
        return task

    def creat_task_with_subtasks(self):
        main_task = self.creat_task()
        main_task.name = "Main task"
        main_task.next_step_date = main_task.next_step_date + timedelta(days=5)
        main_task.save(update_fields=['name', 'next_step_date'])
        create_subtask_url = TaskAdmin.get_add_subtask_url(main_task.id)

        self.client.force_login(self.masha)
        response = self.client.get(create_subtask_url, follow=True)
        self.assertEqual(response.status_code, 200, response.reason_phrase)
        data = get_adminform_initials(response)
        data['name'] = "Masha's task"
        data['next_step_date'] = data['next_step_date'] + timedelta(days=5)
        response = self.client.post(create_subtask_url, data, follow=True)
        self.assertEqual(response.status_code, 200, response.reason_phrase)
        self.assertNoFormErrors(response)

        masha_subtask = Task.objects.get(task=main_task, owner=self.masha)
        masha_subtask.next_step_date = masha_subtask.next_step_date + timedelta(days=5)
        masha_subtask.save(update_fields=['next_step_date'])
        self.client.force_login(self.sergey)
        response = self.client.get(create_subtask_url, follow=True)
        self.assertEqual(response.status_code, 200, response.reason_phrase)
        data = get_adminform_initials(response)
        data['name'] = "Sergey's task"
        data['responsible'] = [str(self.sergey.id)]
        response = self.client.post(create_subtask_url, data, follow=True)
        self.assertEqual(response.status_code, 200, response.reason_phrase)
        self.assertNoFormErrors(response)

        sergey_subtask = Task.objects.get(task=main_task, owner=self.sergey)
        return main_task, masha_subtask, sergey_subtask

    def get_responsible_field_data(self, user, url, resolver_match):
        request = self.factory.get(url)
        department = user.groups.filter(
            department__isnull=False).first()
        user.department_id = department.id if department else None
        request.user = user
        groups = request.user.groups.all()
        set_user_groups(request, groups)
        request.resolver_match = resolver_match
        response = resolver_match.func(request)
        form = response.context_data['adminform'].form
        queryset = form.base_fields['responsible']._queryset
        initials = form.base_fields['responsible'].initial        
        
        return queryset, initials
