import os
import threading
from datetime import datetime as dt
from datetime import timedelta
from random import random
from time import sleep
from typing import Optional
from django.conf import settings
from django.contrib.sites.models import Site
from django.core.mail import mail_admins

from crm.settings import IMAP_CONNECTION_IDLE
from crm.settings import IMAP_NOOP_PERIOD
from crm.utils.crm_imap import CrmIMAP
from massmail.models import EmailAccount

delta_period = timedelta(seconds=30)
idle_period = timedelta(days=IMAP_CONNECTION_IDLE)


class CrmImapManager(threading.Thread):
    """Create and manage CrmIMAP objects."""

    def __init__(self, ea_queue): 
        threading.Thread.__init__(self)
        self.daemon = True
        self.boxes_storage = {}
        self.close = False
        self.ea_queue = ea_queue
        self.crmimap_storage = {}

    def get_crmimap(self, ea: EmailAccount, 
                    box: Optional[str] = None) -> Optional[CrmIMAP]:
        if not settings.TESTING:
            return self._get_or_create_crmimap(ea, box)

    def run(self) -> None:
        if settings.REUSE_IMAP_CONNECTION:
            if not settings.TESTING:
                s = int(random() * IMAP_NOOP_PERIOD)
                sleep(s)
                self._keep_in_touch()
    
    def _create_crmimap(self, ea: EmailAccount) -> Optional[CrmIMAP]:
        crmimap = CrmIMAP(ea.email_host_user)
        if ea.email_host_user not in self.crmimap_storage:
            if settings.REUSE_IMAP_CONNECTION:
                self.crmimap_storage[ea.email_host_user] = crmimap
            boxes = self.boxes_storage.get(ea.email_host_user)
            crmimap.get_in(boxes, ea)
            if not crmimap.error:
                if not boxes:
                    self.boxes_storage[ea.email_host_user] = crmimap.boxes
        else:
            crmimap = self.crmimap_storage.get(ea.email_host_user)
        crmimap.last_request_time = dt.now()
        return crmimap

    def _del_crmimap(self, crmimap: CrmIMAP) -> None:
        del self.crmimap_storage[crmimap.email_host_user]
        crmimap.close_and_logout()

    def _get_crmimap(self, ea: EmailAccount) -> Optional[CrmIMAP]:
        crmimap = None
        if settings.REUSE_IMAP_CONNECTION:
            crmimap = self.crmimap_storage.get(ea.email_host_user)
            if crmimap:
                crmimap.lock()
                if not crmimap.error:
                    crmimap.last_request_time = dt.now()
                    result = crmimap.noop()
                    if result != 'OK' or crmimap.error:
                        self._del_crmimap(crmimap)
                        crmimap = None
                else:
                    self._del_crmimap(crmimap)
                    crmimap = None
        return crmimap

    def _get_or_create_crmimap(self, ea: EmailAccount, 
                               box: Optional[str]) -> Optional[CrmIMAP]:
        crmimap = self._get_crmimap(ea) or self._create_crmimap(ea)
        if crmimap and not crmimap.error and box:
            crmimap.select_box(box)
        return crmimap

    def _keep_in_touch(self) -> None:
        while True:
            key_list = list(self.crmimap_storage.keys())
            for key in key_list:
                value = getattr(self.crmimap_storage.get(key, None), 'locked')
                if value is False:
                    self.crmimap_storage[key].locked = True
                    self._serve_crmimap(key)

            sleep(IMAP_NOOP_PERIOD)

    def _serve_crmimap(self, key) -> None:
        try:
            crmimap = self.crmimap_storage[key]
            now = dt.now()
            request_time_delta = now - crmimap.last_request_time
            if crmimap.noop_time:
                noop_time_delta = now - crmimap.noop_time
            else:
                noop_time_delta = request_time_delta

            ea = crmimap.ea
            if noop_time_delta > delta_period and \
                    request_time_delta > delta_period:
                crmimap.noop_time = now
                result = crmimap.noop()
                if result != 'OK':
                    self._del_crmimap(crmimap)
                    crmimap = self._create_crmimap(ea)

            crmimap.release()
            self.ea_queue.put(ea)
        except Exception as err:  # FIXME: remove after a while
            site = Site.objects.get_current()
            mail_admins(
                "Exception CrmImapManager._serve_crmimap()",
                f"""\nException:__{err}\n
                \nException time:____{dt.now().time()}
                \nSite {site.domain}
                \nThread: {threading.current_thread()}
                \nProcess: {os.getpid()}\n
                """
            )        
