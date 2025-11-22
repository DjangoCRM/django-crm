from datetime import date

from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework.test import APIClient

from crm.models import Deal
from tasks.models import Task, TaskStage
from tests.base_test_classes import BaseTestCase


User = get_user_model()


class ApiPermissionsTestCase(BaseTestCase):
    def setUp(self):
        super().setUp()
        self.client = APIClient()
        self.other_client = APIClient()
        self.user = User.objects.get(username="Marina.Co-worker.Global")
        self.other_user = User.objects.get(username="Masha.Co-worker.Bookkeeping")
        self.client.force_authenticate(self.user)
        self.other_client.force_authenticate(self.other_user)

    def test_task_creation_sets_defaults_and_scopes_access(self):
        url = reverse("v1:task-list")
        payload = {
            "name": "API task",
            "next_step": "Do something",
            "next_step_date": date.today(),
        }
        response = self.client.post(url, payload, format="json")
        self.assertEqual(response.status_code, 201, response.content)
        task_id = response.data["id"]

        task = Task.objects.get(id=task_id)
        default_stage = TaskStage.objects.filter(default=True).first()
        self.assertEqual(task.stage, default_stage)
        self.assertIn(self.user, task.responsible.all())

        detail_url = reverse("v1:task-detail", args=[task_id])
        blocked_response = self.other_client.get(detail_url)
        self.assertEqual(blocked_response.status_code, 404)

    def test_deal_creation_adds_defaults_and_scopes_by_owner(self):
        url = reverse("v1:deal-list")
        payload = {
            "name": "API deal",
            "next_step": "Call client",
        }
        response = self.client.post(url, payload, format="json")
        self.assertEqual(response.status_code, 201, response.content)
        deal_id = response.data["id"]
        deal = Deal.objects.get(id=deal_id)
        self.assertTrue(deal.ticket)
        self.assertEqual(deal.owner, self.user)

        detail_url = reverse("v1:deal-detail", args=[deal_id])
        blocked_response = self.other_client.get(detail_url)
        self.assertEqual(blocked_response.status_code, 404)

    def test_schema_available_with_versioned_namespace(self):
        url = reverse("v1:schema")
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertIn("openapi", str(response.content).lower())
