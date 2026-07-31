from queue import Queue

from django.apps import AppConfig
from django.conf import settings

from common.utils.worker_runtime import should_start_background_workers
from common.utils.worker_runtime import start_crm_mail_workers
from common.utils.worker_runtime import start_crm_schedulers


class CrmConfig(AppConfig):
    name = 'crm'
    label = 'crm'
    default_auto_field = 'django.db.models.AutoField'

    def ready(self):
        from crm.site.crmadminsite import crm_site
        from sharedkernel.adminsites import CRM_SITE_NAME
        from sharedkernel.adminsites import register_admin_site

        register_admin_site(CRM_SITE_NAME, crm_site)

        if settings.TESTING:
            from crm.utils.create_email_request import CreateEmailInquiry
            from crm.utils.restore_imap_emails import RestoreImapEmails

            self.inq_eml_queue = Queue(2)
            self.eml_queue = Queue(4)
            rim = RestoreImapEmails(self.eml_queue, self.inq_eml_queue)
            cei = CreateEmailInquiry(self.inq_eml_queue)
            rim.daemon = True
            cei.daemon = True
            rim.start()
            cei.start()
            return

        if not should_start_background_workers():
            return

        start_crm_mail_workers(self)
        start_crm_schedulers()

    def import_emails(self, user):
        importer = getattr(self, 'im', None)
        if importer is not None:
            importer.send(user)
