"""CRM-specific background worker startup helpers."""

from __future__ import annotations

import logging
from queue import Queue

from tendo.singleton import SingleInstanceException

from common.utils.worker_runtime import _track_thread

logger = logging.getLogger(__name__)


def start_crm_mail_workers(crm_config) -> list[str]:
    """Start CRM mail import threads and attach handles to the app config."""
    from crm.utils.create_email_request import CreateEmailInquiry
    from crm.utils.import_emails import ImportEmails
    from crm.utils.manage_imaps import CrmImapManager
    from crm.utils.restore_imap_emails import RestoreImapEmails

    ea_queue = Queue()
    crm_config.inq_eml_queue = Queue(2)
    crm_config.eml_queue = Queue(4)
    crm_config.mci = _track_thread(CrmImapManager(ea_queue))
    crm_config.im = _track_thread(ImportEmails(ea_queue, crm_config.eml_queue))
    rim = _track_thread(RestoreImapEmails(crm_config.eml_queue, crm_config.inq_eml_queue))
    cei = _track_thread(CreateEmailInquiry(crm_config.inq_eml_queue))

    started = []
    for name, thread in (
        ('crm_imap_manager', crm_config.mci),
        ('import_emails', crm_config.im),
        ('restore_imap_emails', rim),
        ('create_email_inquiry', cei),
    ):
        thread.start()
        started.append(name)
        logger.info('background_worker_started worker=%s', name)

    return started


def start_crm_schedulers() -> list[str]:
    """Start CRM scheduler threads such as the exchange-rate loader."""
    from crm.utils.rates_loader import RatesLoader

    started = []
    try:
        rates_loader = _track_thread(RatesLoader())
        rates_loader.start()
        started.append('rates_loader')
        logger.info('background_worker_started worker=%s', 'rates_loader')
    except SingleInstanceException:
        logger.info('background_worker_skipped worker=rates_loader reason=single_instance')
    return started
