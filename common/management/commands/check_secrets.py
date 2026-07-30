from django.core.management.base import BaseCommand

from webcrm.secret_literal_scanner import scan_repository


class Command(BaseCommand):
    help = 'Scan settings modules and .env.example for secret-shaped literal assignments.'

    def handle(self, *args, **options):
        findings = scan_repository()
        if not findings:
            self.stdout.write(self.style.SUCCESS('No secret literal violations found.'))
            return

        for finding in findings:
            self.stderr.write(
                f'{finding.path}:{finding.lineno}: {finding.name} — {finding.reason}'
            )
        self.stderr.write(
            self.style.ERROR(f'Found {len(findings)} secret literal violation(s).')
        )
        raise SystemExit(1)
