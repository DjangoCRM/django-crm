"""Tests for background worker gating and management commands."""

from __future__ import annotations

import signal
from unittest.mock import patch

from django.apps import apps
from django.core.management import call_command
from django.test import SimpleTestCase, override_settings, tag

from common.utils.worker_runtime import should_start_background_workers
from crm.apps import CrmConfig


@tag('TestCase')
class BackgroundWorkerSettingsTests(SimpleTestCase):
    @override_settings(RUN_BACKGROUND_WORKERS=False, TESTING=False)
    def test_should_not_start_when_flag_disabled(self):
        self.assertFalse(should_start_background_workers())

    @override_settings(RUN_BACKGROUND_WORKERS=True, TESTING=True)
    def test_should_not_start_during_tests(self):
        self.assertFalse(should_start_background_workers())

    @override_settings(RUN_BACKGROUND_WORKERS=True, TESTING=False)
    def test_should_start_for_legacy_single_process_install(self):
        self.assertTrue(should_start_background_workers())


@tag('TestCase')
class AppConfigWorkerGatingTests(SimpleTestCase):
    @override_settings(RUN_BACKGROUND_WORKERS=False, TESTING=False)
    def test_crm_ready_starts_no_mail_workers_when_flag_disabled(self):
        with patch('crm.apps.start_crm_mail_workers') as start_mail, patch(
            'crm.apps.start_crm_schedulers'
        ) as start_schedulers:
            CrmConfig('crm', apps.get_app_config('crm').module).ready()
        start_mail.assert_not_called()
        start_schedulers.assert_not_called()

    @override_settings(RUN_BACKGROUND_WORKERS=True, TESTING=False)
    def test_crm_ready_starts_workers_when_flag_enabled(self):
        with patch('crm.apps.start_crm_mail_workers') as start_mail, patch(
            'crm.apps.start_crm_schedulers'
        ) as start_schedulers:
            CrmConfig('crm', apps.get_app_config('crm').module).ready()
        start_mail.assert_called_once()
        start_schedulers.assert_called_once()


@tag('TestCase')
class WorkerManagementCommandTests(SimpleTestCase):
    @patch('common.management.commands.run_mail_workers.wait_for_shutdown')
    @patch('common.management.commands.run_mail_workers.register_signal_handlers')
    @patch(
        'crm.utils.worker_runtime.start_crm_mail_workers',
        return_value=['import_emails'],
    )
    @patch('common.management.commands.run_mail_workers.stop_tracked_threads')
    def test_run_mail_workers_starts_and_stops_workloads(
        self,
        stop_threads,
        start_workers,
        register_handlers,
        wait_for_shutdown,
    ):
        call_command('run_mail_workers')
        start_workers.assert_called_once()
        register_handlers.assert_called_once_with(stop_threads)
        stop_threads.assert_called_once()

    @patch('common.management.commands.run_schedulers.wait_for_shutdown')
    @patch('common.management.commands.run_schedulers.register_signal_handlers')
    @patch(
        'crm.utils.worker_runtime.start_crm_schedulers',
        return_value=['rates_loader'],
    )
    @patch(
        'common.management.commands.run_schedulers.start_common_schedulers',
        return_value=['notification_email_sender'],
    )
    @patch('common.management.commands.run_schedulers.stop_tracked_threads')
    def test_run_schedulers_starts_and_stops_workloads(
        self,
        stop_threads,
        start_common,
        start_crm,
        register_handlers,
        wait_for_shutdown,
    ):
        call_command('run_schedulers')
        start_common.assert_called_once()
        start_crm.assert_called_once()
        register_handlers.assert_called_once_with(stop_threads)
        stop_threads.assert_called_once()

    @patch('common.utils.worker_runtime._shutdown_event.set')
    @patch('common.utils.worker_runtime.stop_tracked_threads')
    def test_signal_handler_requests_shutdown(self, stop_threads, set_event):
        from common.utils.worker_runtime import register_signal_handlers

        register_signal_handlers(stop_threads)
        signal.getsignal(signal.SIGTERM)(signal.SIGTERM, None)
        set_event.assert_called_once()
        stop_threads.assert_called_once()
