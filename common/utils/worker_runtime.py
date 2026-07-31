"""Shared helpers for starting and stopping background worker threads."""

from __future__ import annotations

import logging
import signal
import threading
from typing import Callable

from django.conf import settings

logger = logging.getLogger(__name__)

_shutdown_event = threading.Event()
_registered_threads: list[threading.Thread] = []


def shutdown_requested() -> bool:
    return _shutdown_event.is_set()


def register_signal_handlers(stop_callback: Callable[[], None]) -> None:
    def _handler(signum, _frame):
        logger.info('background_workers_shutdown signal=%s', signum)
        _shutdown_event.set()
        stop_callback()

    signal.signal(signal.SIGTERM, _handler)
    signal.signal(signal.SIGINT, _handler)


def wait_for_shutdown() -> None:
    _shutdown_event.wait()


def _track_thread(thread: threading.Thread) -> threading.Thread:
    thread.daemon = False
    _registered_threads.append(thread)
    return thread


def stop_tracked_threads() -> None:
    for thread in reversed(_registered_threads):
        close_flag = getattr(thread, 'close', None)
        if close_flag is not None:
            thread.close = True
        finish_work = getattr(thread, 'finish_work', None)
        if callable(finish_work):
            try:
                finish_work()
            except Exception:
                logger.exception('Failed to finish worker thread %s', thread.name)
    for thread in _registered_threads:
        thread.join(timeout=5)


def start_common_schedulers(common_config) -> list[str]:
    """Start common notification and reminder scheduler threads."""
    from common.utils.notif_email_sender import NotifEmailSender
    from common.utils.reminders_sender import RemindersSender

    common_config.nes = _track_thread(NotifEmailSender())
    common_config.nes.start()
    started = ['notification_email_sender']
    logger.info('background_worker_started worker=%s', 'notification_email_sender')

    try:
        common_config.rs = _track_thread(RemindersSender())
        common_config.rs.start()
        started.append('reminders_sender')
        logger.info('background_worker_started worker=%s', 'reminders_sender')
    except SingleInstanceException:
        logger.info('background_worker_skipped worker=reminders_sender reason=single_instance')

    return started


def should_start_background_workers() -> bool:
    return settings.RUN_BACKGROUND_WORKERS and not settings.TESTING
