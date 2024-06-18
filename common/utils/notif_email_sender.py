import threading
from queue import Queue
from smtplib import SMTPServerDisconnected
from django.conf import settings
from django.core.mail import EmailMessage


class NotifEmailSender(threading.Thread):
    """
    Used to send CRM mail notifications.
    Creates email messages and sends them one by one using queue.
    Email body always serves as HTML type.
    """

    def __init__(self):
        threading.Thread.__init__(self)
        self.daemon = True
        self.send_queue = Queue()

    def send_msg(self, subject: str = "",
                 body: str = "", to: list = None) -> None:

        msg = EmailMessage(
            subject=subject,
            body=body,
            from_email=settings.DEFAULT_FROM_EMAIL,
            to=to,
            reply_to=settings.CRM_REPLY_TO
        )
        msg.content_subtype = "html"
        self.send_queue.put(msg)

    def run(self):
        while True:
            eml = self.send_queue.get()
            if not settings.DEBUG:
                try:
                    eml.send()
                except SMTPServerDisconnected:
                    try:
                        eml.send()
                    except:     # NOQA
                        pass
                except:         # NOQA
                    pass
