import sys
import django
from django.conf import settings
from django.test import tag

from common.site.crmsite import set_app_models
from common.utils.helpers import USER_MODEL
from tests.base_test_classes import BaseTestCase
from tests.main_menu_data import DATA
from tests.main_menu_data import ADMIN_DATA

# manage.py test tests.test_base --keepdb
# manage.py test tests.test_base --noinput


@tag('TestCase')
class MyTests(BaseTestCase):

    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()
        username_list = []
        for username, _ in DATA:
            username_list.append(username)
        cls.users = USER_MODEL.objects.filter(
            username__in=username_list)

    def setUp(self):
        print("Run Test Method:", self._testMethodName)

    def test_versions(self):
        print(
            "Python version",
            f"{sys.version_info[0]}.{sys.version_info[1]}.{sys.version_info[2]}"
        )
        if sys.version_info[0] < 3:
            self.fail("Must be using Python > 3.7")
        if sys.version_info[1] < 7:
            self.fail("Must be using Python > 3.7")
        django_version = django.get_version().split('.')
        print("Django version", django.get_version())
        if int(django_version[0]) < 5:
            self.fail("Must be using Django > 5.0")
        if int(django_version[1]) < 0:
            self.fail("Must be using Django > 5.0")

    def test_apps_models_perms(self):
        """
        Test for users with different roles access to some of apps, models
        and permissions at home page (with 'en' language code).
        """

        # self.client.force_login(User.objects.get_or_create(username='testuser')[0])
        # from tests.utils.dump_group_permissions import import_group_perms
        # import_group_perms()
        # from tests.utils.dump_group_permissions import convert_group_fixture
        # convert_group_fixture()

        for username, correct_app_list in DATA:
            if hasattr(settings, 'MODEL_ON_INDEX_PAGE'):
                for app_label in settings.APP_ON_INDEX_PAGE:
                    app = next((
                        a for a in correct_app_list
                        if app_label == a['app_label']), None
                    )
                    if app:
                        set_app_models(app, app_label)
            self.client.force_login(self.users.get(username=username))
            # Issue a GET request.
            response = self.client.get(
                '/' + settings.SECRET_CRM_PREFIX,
                HTTP_ACCEPT_LANGUAGE='en',
                follow=True
            )
            context_app_list = response.context['app_list']
            self.assertEqual(response.status_code, 200, response.reason_phrase)

            self.check_app_availability_and_model_permissions(username, correct_app_list, context_app_list)

    def test_apps_menu_changelists(self):
        """
        Test for users with different roles access to app menus and model changelists pages.
        """
        for username, correct_app_list in DATA:
            self.get_response_all_urls(username, correct_app_list)

    def test_admin_apps_menu_changelists(self):
        """
        Test for users with admin role access to app menus and model changelists pages.
        """
        correct_app_list = ADMIN_DATA
        user = self.users.filter(is_superuser=True).first()
        username = user.username
        self.get_response_all_urls(username, correct_app_list)

    def get_response_all_urls(self, username, correct_app_list):
        self.client.force_login(self.users.get(username=username))
        for app in correct_app_list:
            self.check_response(app['app_url'], username)

            for model in app['models']:
                url = app['app_url'] + f'{model["object_name"].lower()}/'
                self.check_response(url, username)
        self.client.logout()

    def test_admin_apps_models_perms(self):
        """
        Test for users with admin roles access to apps, models
        and permissions at home page of admin (with 'en' language code).
        """

        correct_app_list = ADMIN_DATA
        user = self.users.filter(is_superuser=True).first()
        username = user.username
        self.client.force_login(user)
        # Issue a GET request.
        response = self.client.get(
            '/' + settings.SECRET_ADMIN_PREFIX,
            HTTP_ACCEPT_LANGUAGE='en',
            follow=True
        )
        context_app_list = response.context['app_list']
        self.assertEqual(response.status_code, 200, response.reason_phrase)

        self.check_app_availability_and_model_permissions(username, correct_app_list, context_app_list)

    def check_app_availability_and_model_permissions(self, username, correct_app_list, context_app_list):
        # Check that the available
        if correct_app_list != context_app_list:
            if len(correct_app_list) == len(context_app_list):
                for correct_app, context_app in zip(correct_app_list, context_app_list):
                    if correct_app == context_app:
                        continue
                    for x in correct_app.keys():
                        if correct_app[x] == context_app[x]:
                            continue
                        if x != 'models':
                            msg = f'"{x}" does not match in "{context_app["name"]}" app for user {username}.'
                            self.assertEqual(correct_app[x], context_app[x], msg)
                        else:
                            if len(context_app['models']) == len(correct_app['models']):
                                for context_model, correct_model \
                                        in zip(context_app['models'], correct_app['models']):
                                    if context_model == correct_model:
                                        continue
                                    for y in correct_model.keys():
                                        if correct_model[y] == context_model[y]:
                                            continue
                                        if y != 'perms':
                                            msg = f'"{y}" of "{context_model["name"]}" model does ' \
                                                  f'not match in "{context_app["name"]}" app for user {username}.'
                                            self.assertEqual(correct_model[y], context_model[y], msg)
                                        else:
                                            for z in correct_model['perms'].keys():
                                                msg = f'"{z}" permission of "{context_model["name"]}" does not ' \
                                                      f'match in "{context_app["name"]}" app for user {username}.'
                                                self.assertIs(correct_model['perms'][z], context_model['perms'][z],
                                                              msg)
                            else:
                                correct_models = [model['name'] for model in correct_app['models']]
                                context_models = [model['name'] for model in context_app['models']]
                                difference = set(context_models) ^ set(correct_models)
                                msg = f"Models list does not match in '{context_app['name']}' app " \
                                      f"for user {username}. The difference is {difference} model."
                                self.assertEqual(correct_models, context_models, msg)
            else:
                # correct_app_names = [app['name'] for app in correct_app_list]
                # context_app_names = [app['name'] for app in context_app_list]
                # difference = set(context_app_names) ^ set(correct_app_names)
                msg = f"App list does not match for user {username}."
                self.assertEqual(correct_app_list, context_app_list, msg)

        self.client.logout()        

    def check_response(self, url: str, username: str) -> None:
        response = self.client.get(url, HTTP_ACCEPT_LANGUAGE='en')
        self.assertEqual(response.status_code, 200,
                         "User {} got response status_code {} at url {}".format(
                             username, response.status_code, url
                         ))
