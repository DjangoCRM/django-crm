
import imaplib
import os
import sys
import threading
from datetime import datetime as dt
from time import sleep
from typing import Optional
from django.conf import settings
from django.contrib.sites.models import Site
from django.core.mail import mail_admins

from massmail.models import EmailAccount


if sys.platform != "win32":
    import fcntl

path = settings.MEDIA_ROOT / 'locks'
sleep_time_sec = 0.03
release_limit = int(60 / sleep_time_sec)    # 60 sec
sleep_time_sec2 = 0.01
lockfile_limit = int(20 / sleep_time_sec2)    # 20 sec


class CrmIMAP:

    def __init__(self, email_host_user: str):
        # quick initialization
        self.email_host_user = email_host_user
        self.locked = True

    def check_box_status(self, box: str, upd_fields: list) -> tuple:
        """Return (changed, uid_validity)"""
        changed, uid_validity = False, True
        names = "(UIDVALIDITY UIDNEXT)"
        name_on_server = self.boxes[box]["name on server"]
        result, data, _ = self._execute(
            self.connection.status,
            (name_on_server, names),
            f"Exception at CrmIMAP.status ({box}, {names}."
        )
        if result != 'OK':
            return changed, uid_validity  # False, True

        data_str = data[0].decode()
        # '"INBOX" (UIDNEXT 11776 UIDVALIDITY 2)'
        items = data_str.split("(")[1].split(")")[0].split(" ")
        status_data = {items[0]: items[1], items[2]: items[3]}

        box = box.lower()
        uidnext = f"{box}_uidnext"
        uidvalidity = f"{box}_uidvalidity"

        if status_data['UIDNEXT'] != str(getattr(self.ea, uidnext)):
            changed = True
            setattr(self.ea, uidnext, int(status_data['UIDNEXT']))
            upd_fields.append(uidnext)

        if status_data['UIDVALIDITY'] != str(getattr(self.ea, uidvalidity)):
            uid_validity = False
            setattr(self.ea, uidvalidity, int(status_data['UIDVALIDITY']))
            upd_fields.append(uidvalidity)

        return changed, uid_validity

    def close_and_logout(self) -> None:
        if self.connection:
            try:
                if self.connection.state != 'AUTH':     # 'NONAUTH'
                    self.connection.close()             # AUTH
                self.connection.logout()                # LOGOUT
            except imaplib.IMAP4.error:                 # NOQA
                pass

    def delete_emails(self, uids_str) -> None:
        """Move emails to 'Trash' box."""
        result = self.select_box('INBOX')
        if result != 'OK':
            return
        self._uid_copy(uids_str, 'Trash')
        self._uid_delete(uids_str)

    def get_emails_by_message_id(self, message_id: str) -> tuple:
        """Return (result, data)"""
        result, data, _ = self._execute(
            self.connection.uid,
            ('search', None, f'(HEADER Message-ID "{message_id}")'),
            f"Exception at IMAP.uid SEARCH, None, HEADER Message-ID {message_id}"
        )
        return result, data

    def get_in(self, boxes: dict, ea: EmailAccount) -> None:
        self._complete_init(boxes, ea)
        self._connect()
        if not self.error:
            self._log_in()
            if not self.error:
                self._get_boxes()

    def if_selected_box(self, box: str) -> bool:
        state = self.connection.state
        if any((not box, not self.selected_box,
                self.selected_box and self.selected_box['name'] != box,
                state != 'SELECTED')):
            return False
        return True

    def lock(self) -> None:
        """Lock this instance for other customers."""
        if self.locked:
            counter = release_limit
            while self.locked:
                sleep(sleep_time_sec)
                counter -= 1
                if not counter:
                    n = release_limit * sleep_time_sec
                    msg = f"The CrmIMAP.{self} was not released within {n} seconds"
                    site = Site.objects.get_current()
                    mail_admins(
                        msg,
                        f'''{msg}\n
                        \nSite {site.domain}
                        \nEmail account:_____{self.ea}
                        \ncreate_time:_______{self.create_time}
                        \nLast_Noop_time:___{self.noop_time}
                        \nLast_request_time:_{self.last_request_time}
                        \nException time:____{dt.now()}
                        \nLog: \n{self._parse_log()}
                        ''',
                    )
                    raise RuntimeError(msg)
        self.locked = True

    def mark_emails_as_read(self, uids_str) -> None:
        result = self.select_box('INBOX')
        if result != 'OK':
            return
        self._uid_seen(uids_str)

    def move_emails_to_spam(self, uids_str) -> None:
        result = self.select_box('INBOX')
        if result != 'OK':
            return
        self._uid_copy(uids_str, 'Spam')
        self._uid_delete(uids_str)

    def noop(self) -> str:
        """Returns result value"""
        result = 'NO'
        if not self.error:
            result, data, error = self._execute(
                self.connection.noop, None,
                f"Exception at CrmIMAP.NOOP, None ({self.ea})."
            )
        return result

    def release(self) -> None:
        """Unlock this instance for other customers."""
        if settings.REUSE_IMAP_CONNECTION:
            self.locked = False
        else:
            self.close_and_logout()

    def search(self, params: str) -> tuple:
        """Return (result, data, error)"""
        return self._execute(
            self.connection.uid,
            ('search', None, params),
            f'Exception at IMAP.uid SEARCH, None, params: {params}.'
        )

    def select_box(self, box: str) -> str:
        """
        Returns:
            str: result
        """
        result = 'OK'
        if not self.if_selected_box(box):
            box = self.boxes[box]
            result, data, err = self._execute(
                self.connection.select, (box['name on server'],),
                f"Exception at CrmIMAP.select {box['name']}."
            )
            if result == 'OK':
                self.selected_box = box     # NOQA
        return result

    def uid_fetch(self, uid: bytes,
                  param: str = '(RFC822)') -> tuple:
        """Return (result, data, error)"""
        return self._execute(
            self.connection.uid,
            ('fetch', uid, param),
            f'Exception at IMAP.uid FETCH {uid}'
        )

    def _close_lockfile(self) -> None:
        try:
            if sys.platform == 'win32':
                os.close(self.fd)
                os.unlink(self.lockfile)
            else:
                fcntl.lockf(self.fp, fcntl.LOCK_UN)
                if os.path.isfile(self.lockfile):
                    os.unlink(self.lockfile)
        except Exception as err:     # FileNotFoundError
            msg = f"The lockfile of {self} was deleted already?"
            site = Site.objects.get_current()
            mail_admins(
                msg,
                f'''{msg}\n
                \nException: {err} 
                \nSite {site.domain}
                \nThread: {threading.current_thread()}
                \nProcess: {os.getpid()}\n                
                \nEmail account:_____{self.ea}
                \ncreate_time:_______{self.create_time}
                \nLast_Noop_time:___{self.noop_time}
                \nLast_request_time:_{self.last_request_time}
                \nException time:____{dt.now()}
                \nLog: \n{self._parse_log()}
                ''',
            )

    def _complete_init(self, boxes: dict, ea: EmailAccount):
        now = dt.now()
        self.boxes = boxes
        self.connection = None
        self.debug = settings.IMAP_DEBUG_LEVEL
        self.ea = ea
        self.error = None
        self.ea = ea
        self.lockfile = path / f"{self.ea.imap_host}.lock"
        self.selected_box = None
        self.noop_time = None
        self.create_time = now
        self.last_request_time = now

    def _execute(self, command,
                 params: Optional[tuple], msg: str) -> tuple:
        """Return (result, data, error)"""
        if settings.REUSE_IMAP_CONNECTION:
            self._open_lockfile()
        result = data = None
        try:
            if params:
                result, data = command(*params)
            else:
                result, data = command()
        except (imaplib.IMAP4.abort, ConnectionResetError) as err:
            self.error = err
            if settings.IMAP_DEBUG_LEVEL:
                self._mail_admins(command, params, msg, result, data)
        except Exception as err:
            self.error = err
            self._mail_admins(command, params, msg, result, data)

        if settings.REUSE_IMAP_CONNECTION:
            self._close_lockfile()
        return result, data, self.error

    def _expunge(self) -> tuple:
        """Return (result, data, error)"""
        return self._execute(
            self.connection.expunge, None,
            'Exception at CrmIMAP.EXPUNGE, None'
        )

    def _get_boxes(self) -> None:
        if self.boxes:
            return
        result, data, error = self._execute(
            self.connection.list, None,
            'Exception at CrmIMAP.LIST, None'
        )
        if result != 'OK' or self.error:
            return
        self.boxes = _get_box_initial_data()

        for name in self.boxes.keys():
            name_on_server = self.boxes[name]['name on server']
            item = next((
                x for x in data
                if name_on_server in x), None
            )
            if not item and name == 'Spam':
                item = next((x for x in data if b'Junk' in x))
                if not item:
                    self.boxes[name]['name on server'] = None
                    continue
                name_on_server = b'Junk'
            if item:
                items = item.decode().split(" ")
                name_on_server = name_on_server.decode()
                if name_on_server in items[-1]:
                    continue
                if name_on_server in items[0] or name_on_server in items[1]:
                    self.boxes[name]['name on server'] = items[-1].encode()
                    continue
        self.boxes['INBOX'] = {'name': 'INBOX', 'name on server': b'INBOX'}

    def _connect(self) -> None:
        try:
            self.connection = imaplib.IMAP4_SSL(self.ea.imap_host)
        except Exception as err:
            self.error = err
            mail_admins(
                'IMAP4_SSL exception at CrmIMAP._connect',
                f'''imaplib.IMAP4_SSL({self.ea.imap_host})
                \nEmail account: {self.ea}
                \nException: {self.error}''',
                fail_silently=True,
            )

    def _log_in(self) -> None:
        self._execute(
            self.connection.login,
            (self.ea.email_host_user,
             self.ea.email_app_password or self.ea.email_host_password),
            'Exception at CrmIMAP.LOGIN'
        )
        if self.error:
            self._mail_admins(
                'LOGIN', None,
                'Exception at CrmIMAP.LOGIN',
                None, None
            )

    def _mail_admins(self, command: str, params: Optional[tuple],
                     msg: str, result, data) -> None:
        site = Site.objects.get_current()
        mail_admins(
            msg,
            f'''{msg}
            \nThe connection will be restored automatically.\n
            Site {site.domain}\n
            Process: {os.getpid()}\n
            CrmIMAP._execute({command}, {params})\n
            Email account:     {self.ea}\n
            Exception:         {self.error}\n
            Type Exception:    {type(self.error)}\n
            Result:            {result}\n
            Data:              {data}\n
            \nCreate_time:_______{self.create_time}\n
            Last_Noop_time:____{self.noop_time}\n
            Last_request_time:_{self.last_request_time}\n
            Exception time:____{dt.now()}\n
            Thread: {threading.current_thread()}\n
            \nLog: \n{self._parse_log()}
            ''',
            fail_silently=True,
        )

    def _open_lockfile(self) -> None:
        counter = lockfile_limit
        while counter:
            if sys.platform == 'win32':
                try:
                    if os.path.exists(self.lockfile):
                        os.unlink(self.lockfile)
                    self.fd = os.open(
                        self.lockfile, os.O_CREAT | os.O_EXCL | os.O_RDWR)
                except OSError as err:
                    _, e, _ = sys.exc_info()
                    if e.errno == 13:
                        pass
                    print(err)
                    raise
                else:
                    return

            else:  # non Win32
                self.fp = open(self.lockfile, 'w')
                self.fp.flush()
                try:
                    fcntl.lockf(self.fp, fcntl.LOCK_EX | fcntl.LOCK_NB)
                except IOError:
                    pass
                else:
                    return

            sleep(sleep_time_sec2)
            counter -= 1

        n = lockfile_limit * sleep_time_sec2
        msg = f"The lockfile of {self} was not released within {n} seconds"
        site = Site.objects.get_current()
        mail_admins(
            msg,
            f'''{msg}\n
            \nThe connection will be restored automatically.\n
            \nSite {site.domain}\n
            Email account:_____{self.ea}\n
            \ncreate_time:_______{self.create_time}\n
            Last_Noop_time:___{self.noop_time}\n
            Last_request_time:_{self.last_request_time}\n
            Exception time:____{dt.now()}\n
            \nLog: \n{self._parse_log()}
            ''',
        )
        raise RuntimeError(msg)

    def _parse_log(self) -> str:
        if self.debug:
            log = ''
            items = [
                (dt.utcfromtimestamp(v[1]), v[0])
                for v in self.connection._cmd_log.values()  # NOQA
            ]
            items.sort(key=lambda x: x[0])
            for i in items:
                line = f"{i[0].time()} {i[1]}\n"
                log += line
            return log
        return "IMAP_DEBUG_LEVEL = 0"

    def _uid_copy(self, uids_str, box) -> tuple:
        """Return (result, data, error)"""
        box = self.boxes[box]
        return self._execute(
            self.connection.uid,
            ('COPY', uids_str, box['name on server']),
            f'Exception at IMAP.uid COPY {uids_str}'
        )

    def _uid_delete(self, uids_str: str) -> tuple:
        """Return (result, data, error)"""
        self._execute(
            self.connection.uid,
            ('STORE', uids_str, '+FLAGS', r"(\Deleted)"),
            f"Exception at CrmIMAP.uid STORE {uids_str}, +FLAGS, (\\Deleted)"
        )
        result, data, error = self._expunge()
        return result, data, error

    def _uid_seen(self, uids_str) -> tuple:
        """Return (result, data, error)"""
        return self._execute(
            self.connection.uid,
            ('STORE', uids_str, '+FLAGS', r"(\Seen)"),
            f"Exception at CrmIMAP.uid STORE, {uids_str} +FLAGS, (\\Seen)"
        )

    def __str__(self):
        return f"CrmIMAP: {self.email_host_user}"


def _get_box_initial_data() -> dict:
    return {
        'Sent': {'name': 'Sent', 'name on server': b'Sent'},
        'Spam': {'name': 'Spam', 'name on server': b'Spam'},
        'Trash': {'name': 'Trash', 'name on server': b'Trash'}
    }
