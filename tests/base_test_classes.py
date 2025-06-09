from django.template.defaultfilters import striptags
from django.test import TestCase
from django.urls import reverse


class BaseTestCase(TestCase):
    fixtures = (
        'currency.json', 'test_country.json', 'resolution.json',
        'groups.json', 'department.json', 'test_users.json',
        'deal_stage.json',  'projectstage.json', 'taskstage.json',
        'client_type.json', 'closing_reason.json', 'industry.json',
        'lead_source.json', 'massmailsettings.json'
    )

    def assertNoFormErrors(self, response):
        errors = response.context.get('errors')
        if errors:  # AdminErrorList - [[]]
            msg = ""
            for error in errors:
                msg = f"{msg}\n{error}"
            raise self.failureException(striptags(f'{msg}'))
        if 'adminform' in response.context:
            errors = response.context['adminform'].form.errors
            if errors:  # ErrorDict
                msg = ""
                errors = errors.get_context()
                data = errors['errors']     # FIXME: does this work?
                for field, error in data:
                    msg = f"{msg}\n{field}: {error}"
                raise self.failureException(msg)

    def obj_doesnt_exists(self, model):
        odj_id = 2147483647
        odj_url = reverse(
            f"site:{model._meta.app_label}_{model._meta.model_name}_change", args=(odj_id,)
        )
        response = self.client.get(odj_url, follow=True)
        changelist_url = reverse(
            f"site:{model._meta.app_label}_{model._meta.model_name}_changelist"
        )
        self.assertEqual(response.redirect_chain[0][0], changelist_url)
