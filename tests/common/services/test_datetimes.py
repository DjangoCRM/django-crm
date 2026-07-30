"""Unit tests for common.services.datetimes."""

from datetime import date

from django.test import SimpleTestCase

from common.services.datetimes import get_delta_date
from common.services.datetimes import get_now
from common.services.datetimes import get_today


class DatetimeServiceTests(SimpleTestCase):
    def test_get_today_matches_get_now_date(self):
        self.assertEqual(get_today(), get_now().date())

    def test_get_delta_date_returns_date_instance(self):
        self.assertIsInstance(get_delta_date(1), date)
