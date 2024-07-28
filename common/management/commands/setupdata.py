import os
from secrets import token_urlsafe

from django.conf import settings
from django.core.management.base import BaseCommand
from django.core.management import call_command


class Command(BaseCommand):
    help = "Migrate and populate data base with initial data"

    def handle(self, *args, **options):
        if not settings.TESTING:
            call_command('migrate', verbosity=1)

        call_command(
            'loaddata',
            'country.json',
            'currency.json',
            'groups.json',
            'resolution.json',
            'department.json',
            'deal_stage.json',
            'projectstage.json',
            'taskstage.json',
            'client_type.json',
            'closing_reason.json',
            'industry.json',
            'lead_source.json',
            'publicemaildomain.json',
            'help_en.json',
            verbosity=1
        )
        if not settings.TESTING:
            pas = token_urlsafe(6)
            os.environ.setdefault('DJANGO_SUPERUSER_PASSWORD', pas)
            os.environ.setdefault('DJANGO_SUPERUSER_USERNAME', 'IamSUPER')
            os.environ.setdefault('DJANGO_SUPERUSER_EMAIL', 'super@example.com')
            call_command('createsuperuser', '--noinput', verbosity=1)
            print(
                "SUPERUSER Credentials:\n",
                " USERNAME: IamSUPER\n",
                f" PASSWORD: {pas}\n",
                " EMAIL: super@example.com\n"
            )
