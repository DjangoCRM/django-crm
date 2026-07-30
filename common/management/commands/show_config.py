import sys

from django.core.management.base import BaseCommand

from webcrm.config import config


class Command(BaseCommand):
    help = 'Print resolved configuration keys with source tier and masked secret values.'

    def handle(self, *args, **options):
        unresolved = config.unresolved_mandatory()
        rows = sorted(config.diagnostics())
        for name in rows:
            value = config.diagnostics()[name]
            source = config.source_diagnostics().get(name, 'unknown')
            self.stdout.write(f'{name}\t{source}\t{value}')

        for name in unresolved:
            self.stdout.write(f'{name}\tmissing\t<unresolved>')

        if unresolved:
            self.stderr.write(
                self.style.ERROR(
                    'Unresolved mandatory configuration: '
                    + ', '.join(unresolved)
                )
            )
            raise SystemExit(1)
