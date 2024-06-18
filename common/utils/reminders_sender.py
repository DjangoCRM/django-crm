import time
import threading
from tendo.singleton import SingleInstance
from django.contrib.sites.models import Site
from django.urls import reverse
from django.template import loader
from django.utils import timezone
from django.utils.translation import gettext as _
from django.core.mail import send_mail, mail_admins
from django.conf import settings

from common.models import Reminder
from common.utils.helpers import save_message


class RemindersSender(threading.Thread, SingleInstance):

    def __init__(self, *args, **kwargs):
        threading.Thread.__init__(self, *args, **kwargs)
        self.daemon = True
        if settings.TESTING:
            SingleInstance.__init__(self, flavor_id='Reminder_test')
        else:
            SingleInstance.__init__(self, flavor_id='Reminder')
    
    def run(self):
        if not settings.TESTING:
            # To prevent hit the db until the apps.ready() is completed.
            time.sleep(1)

            while True:
                if settings.DEBUG:
                    break
                send_remainders()
                time.sleep(settings.REMAINDER_CHECK_INTERVAL)


def send_remainders() -> None:
    now = timezone.now()
    reminders = Reminder.objects.filter(active=True, reminder_date__lte=now)
    if reminders:
        site = Site.objects.get_current()
        template = loader.get_template("common/reminder_message.html")
        for r in reminders:
            content_obj = r.content_object
            content_obj_name = content_obj._meta.verbose_name   # NOQA
            r_url = reverse('site:common_reminder_change', args=(r.id,))
            obj_url = reverse(
                f'site:{content_obj._meta.app_label}_{content_obj._meta.model_name}_change',    # NOQA
                args=(content_obj.id,)
            )
            content_obj_url = f'https://{site.domain}{obj_url}'
            subject = 'CRM Remainder: ' + " ".join(r.subject.splitlines())
            save_message(
                r.owner,
                '<i class ="material-icons" style="font-size: 17px;vertical-align: middle;">alarm_on</i>'
                f'<a href="{r_url}"> {subject}</a> {_("Regarding")} - {content_obj_name}: {content_obj}',
                'INFO'
            )
            if r.send_notification_email:
                context = {
                    'content_obj': content_obj,
                    'content_obj_name': content_obj_name,
                    'content_obj_url': content_obj_url,
                    'content': r.description if r.description else subject
                }
                u = r.owner
                if u.email:
                    send_mail(
                        subject,
                        r.description if r.description else subject,
                        settings.DEFAULT_FROM_EMAIL,
                        (u.email,),
                        fail_silently=True,
                        html_message=template.render(context)
                    )
                    r.send_notification_email = False
                else:
                    mail_admins(
                        'No email address for User - %s.' % u,
                        'CRM reminder can not send him messages',
                        fail_silently=False,
                    )
            if getattr(content_obj, 'remind_me', None):
                content_obj.remind_me = False
                content_obj.save(update_fields=['remind_me'])
            r.active = False
            r.save(update_fields=['send_notification_email', 'active'])
