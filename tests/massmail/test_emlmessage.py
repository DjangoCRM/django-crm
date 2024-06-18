from django.test import tag
from django.urls import reverse

from common.utils.helpers import get_department_id
from common.utils.helpers import USER_MODEL
from massmail.models import EmlMessage
from tests.base_test_classes import BaseTestCase
from tests.utils.helpers import get_adminform_initials

# python manage.py test tests.massmail.test_emlmessage --keepdb


@tag('TestCase')
class TestEmlMessage(BaseTestCase):
    """Test add EmlMessage"""

    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()
        cls.add_url = reverse("site:massmail_emlmessage_add")
        cls.changelist_url = reverse("site:massmail_emlmessage_changelist")
        username_list = ("Adam.Admin",
                         "Darian.Manager.Co-worker.Head.Global")
        users = USER_MODEL.objects.filter(
            username__in=username_list)
        cls.admin = users.get(username="Adam.Admin")
        cls.user = users.get(
            username="Darian.Manager.Co-worker.Head.Global")

    def setUp(self):
        print("Run Test Method:", self._testMethodName)
        self.client.force_login(self.user)
        self.response = self.client.get(self.add_url, follow=True)

    def test_add_emlmessage(self):
        self.assertEqual(self.response.status_code, 200,
                         self.response.reason_phrase)
        data = get_adminform_initials(self.response)
        data['subject'] = "New newsletter"
        data['content'] = "content"
        response = self.client.post(self.add_url, data, follow=True)
        self.assertNoFormErrors(response)
        self.assertEqual(response.status_code, 200, response.reason_phrase)
        self.assertEqual(response.redirect_chain[0][0], self.changelist_url)
        # open emlmessage changlist
        self.response = self.client.get(self.changelist_url, follow=True)
        self.assertEqual(self.response.status_code, 200,
                         self.response.reason_phrase)

    def test_change_company(self):
        msg = create_emlmessage(self.user)
        change_url = reverse("site:massmail_emlmessage_change", args=(msg.id,))
        response = self.client.get(change_url, follow=True)
        self.assertEqual(response.status_code, 200, response.reason_phrase)
        self.assertEqual(response.redirect_chain, [])
        data = get_adminform_initials(response)
        data['subject'] = 'New2 newsletter'
        response = self.client.post(change_url, data, follow=True)
        self.assertNoFormErrors(response)
        self.assertEqual(response.status_code, 200, response.reason_phrase)
        self.assertEqual(response.redirect_chain[0][0], self.changelist_url)

    def test_fix_company_by_admin(self):
        msg = create_emlmessage(self.user)
        self.client.force_login(self.admin)
        change_url = reverse("admin:massmail_emlmessage_change", args=(msg.id,))
        response = self.client.get(change_url, follow=True)
        self.assertEqual(response.status_code, 200, response.reason_phrase)
        self.assertEqual(response.redirect_chain, [])
        data = get_adminform_initials(response)
        data['content'] = "new content"
        response = self.client.post(change_url, data, follow=True)
        self.assertNoFormErrors(response)
        self.assertEqual(response.status_code, 200, response.reason_phrase)
        changelist_url = reverse("admin:massmail_emlmessage_changelist")
        self.assertEqual(response.redirect_chain[0][0], changelist_url)


def create_emlmessage(user) -> EmlMessage:
    msg = EmlMessage(
        subject="New newsletter",
        content="content"
    )
    msg.department_id = get_department_id(user)
    msg.owner = user
    msg.save()
    return msg
