import time
import threading
from tendo.singleton import SingleInstance
from django.conf import settings
from django.core.mail import mail_admins
from django.contrib.sites.models import Site
from django.template import loader
from django.urls import reverse
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from django.utils.translation import override

from common.models import Reminder
from common.utils.helpers import get_trans_for_user
from common.utils.helpers import save_message
from common.utils.helpers import send_crm_email
from settings.models import Reminders

regarding_str = _('Regarding')


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
            # To prevent hitting the db until the apps.ready() is completed.
            time.sleep(1)

            while True:
                if settings.DEBUG:
                    break
                send_remainders()
                try:
                    interval = Reminders.objects.get(id=1).check_interval
                except Reminders.DoesNotExist:
                    # TODO: The "REMAINDER_CHECK_INTERVAL" setting is deprecated and should be removed in the future.
                    interval = getattr(settings, 'REMAINDER_CHECK_INTERVAL', None) or 300
                    Reminders.objects.create(id=1, check_interval=interval)

                time.sleep(interval)


def send_remainders() -> None:
    now = timezone.now()
    reminders = Reminder.objects.filter(active=True, reminder_date__lte=now)
    if reminders:
        site = Site.objects.get_current()
        template = loader.get_template("common/reminder_message.html")
        for r in reminders:
            content_obj = r.content_object
            r_url = reverse('site:common_reminder_change', args=(r.id,))
            obj_url = reverse(
                f'site:{content_obj._meta.app_label}_{content_obj._meta.model_name}_change',    # NOQA
                args=(content_obj.id,)
            )
            model_name = Reminder._meta.object_name     # NOQA
            user = r.owner
            trans_name = get_trans_for_user(model_name, user)
            subject = f'CRM {trans_name}: ' + " ".join(r.subject.splitlines())
            trans_regarding = get_trans_for_user(regarding_str, user)
            content_obj_name = get_trans_for_user(content_obj._meta.object_name, user)  # NOQA
            save_message(
                r.owner,
                '<i class ="material-icons" style="font-size: 17px;vertical-align: middle;">alarm_on</i>'
                f'<a href="{r_url}"> {subject}</a> {trans_regarding} - {content_obj_name}: {content_obj}',
                'INFO'
            )
            if r.send_notification_email:
                content_obj_url = f'https://{site.domain}{obj_url}'
                context = {
                    'content_obj': content_obj,
                    'content_obj_name': content_obj_name,
                    'content_obj_url': content_obj_url,
                    'content': r.description if r.description else subject
                }
                if user.email:
                    code = user.profile.language_code  # NOQA
                    with override(code):
                        body = template.render(context)
                    send_crm_email(
                        subject,
                        body,
                        [user.email]
                    )
                    r.send_notification_email = False
                else:
                    mail_admins(
                        'No email address for User - %s.' % user,
                        'CRM reminder can not send him messages',
                        fail_silently=False,
                    )
            if getattr(content_obj, 'remind_me', None):
                content_obj.remind_me = False
                content_obj.save(update_fields=['remind_me'])
            r.active = False
            r.save(update_fields=['send_notification_email', 'active'])
