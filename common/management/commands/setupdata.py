import os
from secrets import token_urlsafe

from django.conf import settings
from django.contrib.auth.models import Group
from django.contrib.auth.models import User
from django.core.management import call_command
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = "Migrate and populate database with initial data"

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
            'sites.json',
            'reminders.json',
            'massmailsettings.json',
            'transaction_quality_signal.json',
            verbosity=1
        )

        pas = token_urlsafe(6)
        User.objects.create_user("IamSUPER", "super@example.com", pas, is_staff=True, is_superuser=True)
        print(
            "SUPERUSER Credentials:\n",
            " USERNAME: IamSUPER\n",
            f" PASSWORD: {pas}\n",
            " EMAIL: super@example.com\n"
        )
        pas = token_urlsafe(6)
        groups = Group.objects.filter(name__in=['managers', "co-workers", "Global sales"])
        user = User.objects.create_user("IamSALES", "sales@example.com", pas, is_staff=True)
        user.groups.add(*groups)
        print(
            "SALES MANAGER Credentials:\n",
            " USERNAME: IamSALES\n",
            f" PASSWORD: {pas}\n",
            " EMAIL: sales@example.com\n"
        )
