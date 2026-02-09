import json
from django.contrib.auth.models import User
from django.test import tag
from django.urls import reverse

from massmail.models import Signature
from tests.base_test_classes import BaseTestCase

# python manage.py test tests.common.views.test_reload_field --keepdb


@tag('TestCase')
class TestReloadField(BaseTestCase):
    """Tests for the reload_field AJAX view that handles
    dynamic form field updates for signature preview,
    owner and co_owner selection."""

    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()
        username_list = (
            "Adam.Admin",
            "Eve.Superoperator.Co-worker",
            "Andrew.Manager.Global",
            "Darian.Manager.Co-worker.Head.Global",
            "Valeria.Operator.Global",
            "Olga.Co-worker.Global",
        )
        users = User.objects.filter(username__in=username_list)
        cls.admin = users.get(username="Adam.Admin")
        cls.superoperator = users.get(
            username="Eve.Superoperator.Co-worker"
        )
        cls.manager = users.get(username="Andrew.Manager.Global")
        cls.head_manager = users.get(
            username="Darian.Manager.Co-worker.Head.Global"
        )
        cls.operator = users.get(username="Valeria.Operator.Global")
        cls.co_worker = users.get(username="Olga.Co-worker.Global")
        # "Global sales" department group pk=9
        cls.department_id = 9
        cls.url = reverse('reload_field')

    def setUp(self):
        print("Run Test Method:", self._testMethodName)

    # --- Authentication tests ---

    def test_unauthenticated_user_redirected(self):
        """Unauthenticated requests must be redirected to the login page
        because the URL is wrapped with login_required."""
        response = self.client.get(self.url)
        self.assertNotEqual(response.status_code, 200)
        self.assertEqual(response.status_code, 302)

    # --- No params tests ---

    def test_no_params_returns_empty_choices(self):
        """A request with no query parameters should return
        a JSON response with only the blank default choice."""
        self.client.force_login(self.admin)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)
        self.assertEqual(
            data,
            {'choices': [{'label': '---------', 'value': ''}]}
        )

    # --- Department param tests ---

    def test_department_as_superuser(self):
        """When a superuser requests a department, the response
        should include users who are managers, operators, or
        superoperators in that department. The superuser branch
        also adds Q(is_superuser=True) to the filter, but only
        users who are actually members of the department group
        appear in the results."""
        self.client.force_login(self.admin)
        response = self.client.get(
            self.url,
            {'department': str(self.department_id)}
        )
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)
        choices = data['choices']
        # First choice is always the blank default
        self.assertEqual(choices[0], {'label': '---------', 'value': ''})
        # Extract returned user IDs (skip blank choice)
        returned_ids = {int(c['value']) for c in choices[1:]}
        # These users are managers/operators AND in Global sales
        expected_ids = {
            self.manager.pk,
            self.head_manager.pk,
            self.operator.pk,
            self.superoperator.pk,
        }
        self.assertEqual(returned_ids, expected_ids)

    def test_department_as_superoperator(self):
        """A superoperator should get the same expanded filter
        as a superuser (includes Q(is_superuser=True)).
        Eve is set as superoperator by the middleware because
        she is in the operators group with multiple departments."""
        self.client.force_login(self.superoperator)
        response = self.client.get(
            self.url,
            {'department': str(self.department_id)}
        )
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)
        choices = data['choices']
        self.assertEqual(choices[0], {'label': '---------', 'value': ''})
        returned_ids = {int(c['value']) for c in choices[1:]}
        expected_ids = {
            self.manager.pk,
            self.head_manager.pk,
            self.operator.pk,
            self.superoperator.pk,
        }
        self.assertEqual(returned_ids, expected_ids)

    def test_department_as_regular_manager(self):
        """A regular manager (non-superuser, non-superoperator)
        should NOT have Q(is_superuser=True) in the filter.
        Their department_id is also overridden to their own
        department via get_department_id()."""
        self.client.force_login(self.manager)
        response = self.client.get(
            self.url,
            {'department': str(self.department_id)}
        )
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)
        choices = data['choices']
        self.assertEqual(choices[0], {'label': '---------', 'value': ''})
        returned_ids = {int(c['value']) for c in choices[1:]}
        expected_ids = {
            self.manager.pk,
            self.head_manager.pk,
            self.operator.pk,
            self.superoperator.pk,
        }
        self.assertEqual(returned_ids, expected_ids)

    def test_department_override_for_regular_user(self):
        """When a regular user requests a department that is NOT
        their own, the view overrides department_id with the
        user's actual department. This prevents users from
        browsing users in other departments.

        Andrew (manager in Global sales, pk=9) requests
        Bookkeeping (pk=11) but should get Global sales results."""
        self.client.force_login(self.manager)
        response = self.client.get(
            self.url,
            {'department': '11'}  # Bookkeeping
        )
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)
        choices = data['choices']
        returned_ids = {int(c['value']) for c in choices[1:]}
        # Should return Global sales users, not Bookkeeping
        self.assertIn(self.manager.pk, returned_ids)
        self.assertNotIn(
            User.objects.get(
                username="Masha.Co-worker.Bookkeeping"
            ).pk,
            returned_ids
        )

    def test_department_choices_have_correct_format(self):
        """Each choice in the response must have 'label' (username)
        and 'value' (user ID as string) keys."""
        self.client.force_login(self.admin)
        response = self.client.get(
            self.url,
            {'department': str(self.department_id)}
        )
        data = json.loads(response.content)
        for choice in data['choices']:
            self.assertIn('label', choice)
            self.assertIn('value', choice)
            self.assertIsInstance(choice['label'], str)
            self.assertIsInstance(choice['value'], str)

    def test_department_blank_choice_is_first(self):
        """The blank '---------' choice must always be the
        first element in the choices list."""
        self.client.force_login(self.admin)
        response = self.client.get(
            self.url,
            {'department': str(self.department_id)}
        )
        data = json.loads(response.content)
        choices = data['choices']
        self.assertGreater(len(choices), 1)
        self.assertEqual(choices[0]['label'], '---------')
        self.assertEqual(choices[0]['value'], '')

    def test_department_no_duplicate_users(self):
        """Users who belong to multiple matching groups should
        not appear more than once thanks to distinct()."""
        self.client.force_login(self.admin)
        response = self.client.get(
            self.url,
            {'department': str(self.department_id)}
        )
        data = json.loads(response.content)
        values = [c['value'] for c in data['choices'][1:]]
        self.assertEqual(len(values), len(set(values)))

    # --- Signature param tests ---

    def test_signature_with_valid_id(self):
        """When 'signature' param has a valid Signature ID,
        the view delegates to signature_preview which returns
        an HttpResponse with the rendered signature content."""
        signature = Signature.objects.create(
            name="Test Sig",
            type=Signature.PLAIN_TEXT,
            content="Best regards, Test User",
            owner=self.admin
        )
        self.client.force_login(self.admin)
        response = self.client.get(
            self.url,
            {'signature': str(signature.pk)}
        )
        self.assertEqual(response.status_code, 200)
        self.assertIn(
            "Best regards, Test User",
            response.content.decode()
        )

    def test_signature_with_empty_value(self):
        """When 'signature' key is present but empty, the view
        still enters signature_preview which returns an empty
        HttpResponse because signature_id is falsy."""
        self.client.force_login(self.admin)
        response = self.client.get(
            self.url,
            {'signature': ''}
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.content.decode(), '')

    def test_response_content_type_department(self):
        """Department requests must return application/json."""
        self.client.force_login(self.admin)
        response = self.client.get(
            self.url,
            {'department': str(self.department_id)}
        )
        self.assertEqual(response['Content-Type'], 'application/json')

    def test_response_content_type_no_params(self):
        """Requests with no params must return application/json."""
        self.client.force_login(self.admin)
        response = self.client.get(self.url)
        self.assertEqual(response['Content-Type'], 'application/json')
