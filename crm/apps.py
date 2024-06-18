from queue import Queue
from tendo.singleton import SingleInstanceException
from django.apps import AppConfig
from django.conf import settings


class CrmConfig(AppConfig):
    name = 'crm'
    label = 'crm'
    default_auto_field = 'django.db.models.AutoField'
    
    def ready(self):
        from crm.utils.create_email_request import CreateEmailInquiry
        from crm.utils.import_emails import ImportEmails
        from crm.utils.manage_imaps import CrmImapManager
        from crm.utils.restore_imap_emails import RestoreImapEmails

        ea_queue = Queue()
        self.inq_eml_queue = Queue(2)
        self.eml_queue = Queue(4)                           # NOQA
        self.mci = CrmImapManager(ea_queue)                 # NOQA
        self.mci.start()
        self.im = ImportEmails(ea_queue, self.eml_queue)    # NOQA
        self.im.start()
        rim = RestoreImapEmails(self.eml_queue, self.inq_eml_queue)
        rim.start()
        cei = CreateEmailInquiry(self.inq_eml_queue)
        cei.start()
        if not settings.TESTING:
            from crm.utils.rates_loader import RatesLoader
            try:
                rl = RatesLoader()
                rl.start()
            except SingleInstanceException:
                pass

    def import_emails(self, user):
        self.im.send(user)
