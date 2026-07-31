"""Run reminder, notification, and exchange-rate scheduler threads."""

from __future__ import annotations

import importlib
import logging

from django.apps import apps
from django.core.management.base import BaseCommand

from common.utils.worker_runtime import (
    register_signal_handlers,
    start_common_schedulers,
    stop_tracked_threads,
    wait_for_shutdown,
)

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = 'Run CRM scheduler background workers until SIGTERM or SIGINT.'

    def handle(self, *args, **options):
        start_crm_schedulers = importlib.import_module(
            'crm.utils.worker_runtime',
        ).start_crm_schedulers
        common_config = apps.get_app_config('common')
        started = start_common_schedulers(common_config)
        started.extend(start_crm_schedulers())
        register_signal_handlers(stop_tracked_threads)
        self.stdout.write(
            self.style.SUCCESS(
                'Started scheduler workers: ' + ', '.join(started)
            )
        )
        wait_for_shutdown()
        stop_tracked_threads()
        logger.info('background_workers_shutdown workers=%s', ','.join(started))
        self.stdout.write(self.style.SUCCESS('Scheduler workers stopped.'))
