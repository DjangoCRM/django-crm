import calendar
import time
import threading
from tendo.singleton import SingleInstance
from unittest import skip
from django.conf import settings
from django.core.mail import mail_admins
from django.db import connection
from django.test import Client
from django.test import override_settings
from django.test import TestCase
from django.utils import timezone
from django.urls import reverse

from analytics.models import IncomeStat
from analytics.models import IncomeStatSnapshot
from common.utils.helpers import get_manager_departments
from common.utils.helpers import USER_MODEL


class MonthlySnapshotSaving(threading.Thread, SingleInstance):
    """Save Snapshot for all departments at the end of last day of every month"""

    def __init__(self, *args, **kwargs):
        threading.Thread.__init__(self, *args, **kwargs)
        self.daemon = True
        if settings.TESTING:
            SingleInstance.__init__(self, flavor_id='MonthlySnapshotSaving_test')
        else:
            SingleInstance.__init__(self, flavor_id='MonthlySnapshotSaving')

    def run(self):
        ss = SaveSnapshot()
        while True:
            now = timezone.localtime(timezone.now())
            last_day = calendar.monthrange(now.year, now.month)[1]
            save_dt = now.replace(
                day=last_day,
                hour=23,
                minute=0,
                second=0,
                microsecond=0
            )
            secs = (save_dt - now).total_seconds()
            if secs > 0:
                connection.close()
                time.sleep(secs)
                try:
                    ss.save_snapshots()
                except Exception as e:
                    mail_admins(
                        "Exception: MonthlySnapshotSaving",
                        f'''
                        \nException time: {now}
                        \nException: {e}''',
                        fail_silently=False,
                    )
            connection.close()
            time.sleep(3600)    # one hour


@skip("This is not a test")
class SaveSnapshot(TestCase):
    """Save Snapshot for all departments"""

    @override_settings(
        SECURE_HSTS_SECONDS=0,
        SECURE_SSL_REDIRECT=False,
        SECURE_HSTS_PRELOAD=False
    )
    def save_snapshots(self) -> None:
        self.client = Client(SERVER_NAME='localhost')
        user = USER_MODEL.objects.filter(is_superuser=True).first()
        self.client.force_login(user)
        departments = get_manager_departments()
        for dep in departments:
            url = reverse("site:analytics_incomestat_changelist")
            response = self.client.get(
                url + f'?department={dep.id}',
                HTTP_ACCEPT_LANGUAGE=settings.LANGUAGE_CODE
            )
            snapshot = IncomeStatSnapshot(
                department_id=dep.id,
                webpage=response.context_data['snapshot'],
            )
            snapshot.save()
