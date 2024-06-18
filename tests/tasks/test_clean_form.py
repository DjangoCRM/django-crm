from django.test import tag

from common.utils.helpers import USER_MODEL
from tasks.forms import ONE_RESPONSIBLE_MSG
from tasks.site.taskadmin import TaskAdmin
from tasks.models import Task
from tasks.models import TaskStage
from tests.base_test_classes import BaseTestCase
from tests.utils.helpers import get_adminform_initials

# manage.py test tests.tasks.test_clean_form --keepdb


@tag('TestCase')
class TestCleanTaskForm(BaseTestCase):
    """Test clean TaskForm"""

    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()
        username_list = ("Garry.Chief", "Sergey.Co-worker.Head.Bookkeeping",
                         "Masha.Co-worker.Bookkeeping")
        users = USER_MODEL.objects.filter(
            username__in=username_list)
        cls.chief = users.get(username="Garry.Chief")
        cls.sergey = users.get(
            username="Sergey.Co-worker.Head.Bookkeeping")
        cls.masha = users.get(
            username="Masha.Co-worker.Bookkeeping")
        cls.default_stage = TaskStage.objects.get(default=True)

    def setUp(self):
        print("Run Test Method:", self._testMethodName)

    def test_number_responsible(self):
        """A subtask should have only one responsible person."""
        main_task = Task.objects.create(
            name="A task to check the possible number of responsible subtasks.",
            owner=self.chief,
            stage=self.default_stage
        )
        main_task.responsible.add(self.sergey, self.masha)
        self.client.force_login(self.sergey)
        add_subtask_url = TaskAdmin.get_add_subtask_url(main_task.id)
        response = self.client.get(add_subtask_url, follow=True)
        self.assertEqual(response.status_code, 200, response.reason_phrase)
        data = get_adminform_initials(response)
        data['name'] = "The task of Sergey and Masha"
        data['responsible'] = [str(self.sergey.id), str(self.masha.id)]
        response = self.client.post(add_subtask_url, data, follow=True)
        self.assertEqual(response.status_code, 200, response.reason_phrase)
        errors = response.context.get('errors')
        self.assertEqual(errors[0][0], ONE_RESPONSIBLE_MSG)
