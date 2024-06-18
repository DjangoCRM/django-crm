from random import random
from django.conf import settings
from django.contrib.auth.models import Group
from django.test import tag
from django.urls import reverse

from common.utils.helpers import USER_MODEL
from help.models import Page
from help.models import Paragraph
from tests.utils.helpers import get_adminform_initials
from tests.base_test_classes import BaseTestCase

# manage.py test tests.help.test_help --keepdb


@tag('TestCase')
class TestHelp(BaseTestCase):
    """Test help app."""

    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()
        cls.content_id = random()
        username_list = ("Adam.Admin", "Garry.Chief",
                         "Darian.Manager.Co-worker.Head.Global")
        users = USER_MODEL.objects.filter(
            username__in=username_list)
        cls.admin = users.get(
            username="Adam.Admin"
        )
        cls.chief = users.get(
            username="Garry.Chief"
        )
        cls.manager = users.get(
            username="Darian.Manager.Co-worker.Head.Global"
        )
        cls.add_page_url = reverse("admin:help_page_add")
        cls.changelist_url = reverse(
            "admin:help_page_changelist"
        )
        cls.managers_group = Group.objects.filter(name='managers').first()
        cls.deal_changelist_url = reverse(
            "site:crm_deal_changelist"
        )
        language_code = settings.LANGUAGE_CODE
        # add help page
        cls.page = Page.objects.create(
            app_label='crm',
            model='Deal',
            page='l',
            main=True,
            language_code=language_code
        )
        content = str(int(random() * 1E5))
        paragraph = Paragraph.objects.create(
            document=cls.page,
            title='Deal list overview',
            content=content,
            language_code=language_code,
            draft=False
        )
        paragraph.groups.set((cls.managers_group,))

    def setUp(self):
        print("Run Test Method:", self._testMethodName)

    def test_add_help_page(self):
        # add help page through form
        self.client.force_login(self.admin)
        response = self.client.get(self.add_page_url, follow=True)
        self.assertEqual(response.status_code, 200, response.reason_phrase)
        data = get_adminform_initials(response)
        content = str(int(random() * 1E5))
        data['app_label'] = 'crm'
        data['model'] = 'Deal'
        data['page'] = 'l'  # changelist
        data['title'] = 'Deal list page'
        data['main'] = True
        data['paragraph_set-TOTAL_FORMS'] = '1'
        data['paragraph_set-0-groups'] = [str(self.managers_group.id)]
        data['paragraph_set-0-title'] = 'Deal list'
        data['paragraph_set-0-content'] = content
        data['paragraph_set-0-index_number'] = 1
        # submit form
        response = self.client.post(self.add_page_url, data, follow=True)
        self.assertEqual(response.status_code, 200, response.reason_phrase)
        self.assertNoFormErrors(response)
        self.assertEqual(response.redirect_chain[-1][0], self.changelist_url)
        self.assertTrue(
            Paragraph.objects.filter(content=content).exists(),
            "The Paragraph DoesNotExist"
        )

    def test_availability_for_managers(self):
        self.client.force_login(self.manager)
        response = self.client.get(self.deal_changelist_url, follow=True)
        self.assertEqual(response.status_code, 200, response.reason_phrase)
        url = reverse("site:help_page_change", args=(self.page.id,))
        self.assertContains(response, url, status_code=200)

    def test_inaccessibility_for_chiefs(self):
        self.client.force_login(self.chief)
        response = self.client.get(self.deal_changelist_url, follow=True)
        self.assertEqual(response.status_code, 200, response.reason_phrase)
        url = reverse("site:help_page_change", args=(self.page.id,))
        self.assertNotContains(response, url, status_code=200)
