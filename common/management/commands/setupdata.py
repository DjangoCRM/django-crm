from django.core.management.base import BaseCommand
from django.core.management import call_command


class Command(BaseCommand):
    help = "Populate data base with initial data"

    def handle(self, *args, **options):
        call_command('loaddata', 'country.json', verbosity=0)
        call_command('loaddata', 'currency.json', verbosity=0)
        call_command('loaddata', 'groups.json', verbosity=0)
        call_command('loaddata', 'resolution.json', verbosity=0)
        call_command('loaddata', 'department.json', verbosity=0)
        call_command('loaddata', 'deal_stage.json', verbosity=0)
        call_command('loaddata', 'projectstage.json', verbosity=0)
        call_command('loaddata', 'taskstage.json', verbosity=0)
        call_command('loaddata', 'client_type.json', verbosity=0)
        call_command('loaddata', 'closing_reason.json', verbosity=0)
        call_command('loaddata', 'industry.json', verbosity=0)
        call_command('loaddata', 'lead_source.json', verbosity=0)
        call_command('loaddata', 'publicemaildomain.json', verbosity=0)
