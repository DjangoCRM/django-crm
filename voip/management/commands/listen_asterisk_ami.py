from tendo.singleton import SingleInstance, SingleInstanceException
from django.core.management.base import BaseCommand

from voip.ami import AmiListener


class Command(BaseCommand):
    help = "Listen to Asterisk AMI events and push incoming call notifications to CRM users."

    def add_arguments(self, parser):
        parser.add_argument(
            '--once',
            action='store_true',
            help='Run a single connection attempt (useful for tests).',
        )

    def handle(self, *args, **options):
        try:
            SingleInstance("listen_asterisk_ami")
        except SingleInstanceException:
            self.stdout.write(self.style.WARNING("Another instance is already running, quitting."))
            return

        listener = AmiListener()
        listener.run_forever(stop_after_one=options['once'])
