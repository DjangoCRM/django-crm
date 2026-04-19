"""
Unit tests for MonthlySnapshotSaving thread and related functionality.

Tests the automatic snapshot saving mechanism for Income Stat reports
at the end of each month for reporting purposes.
"""
import threading
from datetime import datetime
from unittest.mock import patch, MagicMock

from django.test import tag, override_settings, TestCase
from django.utils import timezone
from django.contrib.auth.models import User
from django.urls import reverse

from analytics.models import IncomeStatSnapshot
from analytics.utils.monthly_snapshot_saving import (
    get_time_to_next_monthly_snapshot_saving,
    MonthlySnapshotSaving,
    SaveSnapshot
)
from tests.base_test_classes import BaseTestCase


# ============================================================================
# Tests for get_time_to_next_monthly_snapshot_saving helper function
# ============================================================================

@tag('Analytics')
class TestGetTimeToNextMonthlySnapshot(TestCase):
    """Test the get_time_to_next_monthly_snapshot_saving function."""

    def setUp(self):
        print(" Run Test Method:", self._testMethodName)

    def test_time_calculation_early_in_month(self):
        """Test time calculation when current time is early in the month."""
        # Test on 1st of January, expecting snapshot on Jan 31st at 23:00
        now = timezone.make_aware(datetime(2024, 1, 1, 10, 30, 0))
        secs = get_time_to_next_monthly_snapshot_saving(now)

        # Calculate expected seconds
        last_day = 31
        save_dt = now.replace(
            day=last_day,
            hour=23,
            minute=0,
            second=0,
            microsecond=0
        )
        expected_secs = (save_dt - now).total_seconds()

        self.assertEqual(secs, expected_secs)
        self.assertGreater(secs, 0)

    def test_time_calculation_late_in_month(self):
        """Test time calculation when current time is late in the month."""
        # Test on 30th of January at 23:30, expecting snapshot on Jan 31st at 23:00
        # This is about 24 hours later
        now = timezone.make_aware(datetime(2024, 1, 30, 23, 30, 0))
        secs = get_time_to_next_monthly_snapshot_saving(now)

        self.assertGreater(secs, 0)
        # From Jan 30 23:30 to Jan 31 23:00 is 23.5 hours = 84600 seconds
        self.assertLess(secs, 90000)  # Less than 25 hours

    def test_time_calculation_last_day_before_snapshot_time(self):
        """Test on the last day before snapshot time (23:00)."""
        # Test on 31st of January at 22:00, expecting snapshot at 23:00
        now = timezone.make_aware(datetime(2024, 1, 31, 22, 0, 0))
        secs = get_time_to_next_monthly_snapshot_saving(now)

        # Should be exactly 3600 seconds (1 hour)
        self.assertEqual(secs, 3600)

    def test_time_calculation_after_snapshot_time(self):
        """Test after snapshot time - should return negative value."""
        # Test on 31st of January at 23:30 (after snapshot time)
        now = timezone.make_aware(datetime(2024, 1, 31, 23, 30, 0))
        secs = get_time_to_next_monthly_snapshot_saving(now)

        # Should be negative (past the snapshot time)
        self.assertLess(secs, 0)

    def test_february_leap_year(self):
        """Test calculation for February in a leap year."""
        # Test on 1st of February 2024 (leap year)
        now = timezone.make_aware(datetime(2024, 2, 1, 10, 0, 0))
        secs = get_time_to_next_monthly_snapshot_saving(now)

        # February 2024 has 29 days
        save_dt = now.replace(
            day=29,
            hour=23,
            minute=0,
            second=0,
            microsecond=0
        )
        expected_secs = (save_dt - now).total_seconds()

        self.assertEqual(secs, expected_secs)

    def test_february_non_leap_year(self):
        """Test calculation for February in a non-leap year."""
        # Test on 1st of February 2023 (non-leap year)
        now = timezone.make_aware(datetime(2023, 2, 1, 10, 0, 0))
        secs = get_time_to_next_monthly_snapshot_saving(now)

        # February 2023 has 28 days
        save_dt = now.replace(
            day=28,
            hour=23,
            minute=0,
            second=0,
            microsecond=0
        )
        expected_secs = (save_dt - now).total_seconds()

        self.assertEqual(secs, expected_secs)

    def test_all_months_have_valid_last_day(self):
        """Test that calculation works for the last day of all months."""
        year = 2024
        for month in range(1, 13):
            now = timezone.make_aware(datetime(year, month, 1, 10, 0, 0))
            secs = get_time_to_next_monthly_snapshot_saving(now)

            # Should always return a positive time early in month
            self.assertGreater(secs, 0)


# ============================================================================
# Tests for MonthlySnapshotSaving thread
# ============================================================================

@tag('Analytics')
class TestMonthlySnapshotSavingThread(BaseTestCase):
    """Test the MonthlySnapshotSaving thread class."""

    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()
        cls.superuser = User.objects.filter(is_superuser=True).first()
        if not cls.superuser:
            cls.superuser = User.objects.create_superuser(
                username='superadmin',
                email='super@example.com',
                password='testpass123'
            )

    def setUp(self):
        print(" Run Test Method:", self._testMethodName)

    def test_initialization_with_testing_flag_true(self):
        """Test thread initialization when TESTING is True."""
        with override_settings(TESTING=True):
            thread = MonthlySnapshotSaving()

            self.assertIsInstance(thread, MonthlySnapshotSaving)
            self.assertTrue(thread.daemon)

    def test_initialization_with_testing_flag_false(self):
        """Test thread initialization when TESTING is False."""
        with override_settings(TESTING=False):
            thread = MonthlySnapshotSaving()

            self.assertIsInstance(thread, MonthlySnapshotSaving)
            self.assertTrue(thread.daemon)

    @patch('analytics.utils.monthly_snapshot_saving.SaveSnapshot')
    def test_thread_runs_save_snapshots(self, mock_save_snapshot_class):
        """Test that the thread runs save_snapshots method."""
        mock_instance = MagicMock()
        mock_save_snapshot_class.return_value = mock_instance

        with override_settings(TESTING=True):
            thread = MonthlySnapshotSaving()
            thread.run()

            # Should call save_snapshots at least once
            mock_instance.save_snapshots.assert_called()

    @patch('analytics.utils.monthly_snapshot_saving.mail_admins')
    @patch('analytics.utils.monthly_snapshot_saving.SaveSnapshot')
    def test_exception_handling_sends_email(self, mock_save_snapshot_class, mock_mail_admins):
        """Test that exceptions trigger admin email notification."""
        # Setup mock to raise an exception
        mock_instance = MagicMock()
        mock_instance.save_snapshots.side_effect = Exception("Test error")
        mock_save_snapshot_class.return_value = mock_instance

        with override_settings(TESTING=True):
            thread = MonthlySnapshotSaving()
            thread.run()

            # mail_admins should be called with error details
            mock_mail_admins.assert_called_once()
            call_args = mock_mail_admins.call_args
            self.assertIn("Exception: MonthlySnapshotSaving", call_args[0][0])
            self.assertIn("Test error", call_args[0][1])

    @patch('analytics.utils.monthly_snapshot_saving.connection')
    @patch('analytics.utils.monthly_snapshot_saving.SaveSnapshot')
    def test_database_connection_closed(self, mock_save_snapshot_class, mock_connection):
        """Test that database connection is properly closed."""
        mock_instance = MagicMock()
        mock_save_snapshot_class.return_value = mock_instance

        with override_settings(TESTING=True):
            thread = MonthlySnapshotSaving()
            thread.run()

            # Connection should be closed
            self.assertTrue(mock_connection.close.called)


# ============================================================================
# Tests for SaveSnapshot functionality
# ============================================================================

@tag('Analytics')
class TestSaveSnapshotFunctionality(BaseTestCase):
    """Test the SaveSnapshot.save_snapshots method."""

    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()
        # Get a superuser for authentication
        cls.superuser = User.objects.filter(is_superuser=True).first()
        if not cls.superuser:
            cls.superuser = User.objects.create_superuser(
                username='superadmin',
                email='super@example.com',
                password='testpass123'
            )

    def setUp(self):
        print(" Run Test Method:", self._testMethodName)

    def test_save_snapshots_creates_snapshot_objects(self):
        """Test that save_snapshots creates IncomeStatSnapshot objects."""
        initial_count = IncomeStatSnapshot.objects.count()

        with override_settings(TESTING=True):
            snapshot_service = SaveSnapshot()
            snapshot_service.save_snapshots()

        # Should have created at least one snapshot
        final_count = IncomeStatSnapshot.objects.count()
        self.assertGreater(final_count, initial_count)

    def test_saved_snapshot_has_required_fields(self):
        """Test that saved snapshots have all required fields."""
        with override_settings(TESTING=True):
            snapshot_service = SaveSnapshot()
            snapshot_service.save_snapshots()

        snapshot = IncomeStatSnapshot.objects.latest('id')

        # Check required fields
        self.assertIsNotNone(snapshot.department_id)
        self.assertIsNotNone(snapshot.webpage)
        self.assertTrue(len(snapshot.webpage) > 0)
        self.assertIsNotNone(snapshot.creation_date)

    def test_saved_snapshot_webpage_contains_html(self):
        """Test that snapshot webpage contains HTML content."""
        with override_settings(TESTING=True):
            snapshot_service = SaveSnapshot()
            snapshot_service.save_snapshots()

        snapshot = IncomeStatSnapshot.objects.latest('id')

        # Should contain HTML tags
        self.assertIn('<', snapshot.webpage)
        self.assertIn('>', snapshot.webpage)

    def test_snapshot_saved_for_each_department(self):
        """Test that snapshots are saved for each manager department."""
        # Clear existing snapshots
        IncomeStatSnapshot.objects.all().delete()

        with override_settings(TESTING=True):
            snapshot_service = SaveSnapshot()
            snapshot_service.save_snapshots()

        snapshots = IncomeStatSnapshot.objects.all()

        # Should have created at least one snapshot
        self.assertGreater(snapshots.count(), 0)

    def test_snapshot_authenticated_as_superuser(self):
        """Test that snapshot generation is authenticated as superuser."""
        with override_settings(TESTING=True):
            snapshot_service = SaveSnapshot()

            # The save_snapshots method should authenticate as superuser
            # This should not raise an authentication error
            snapshot_service.save_snapshots()

        # If we got here without exception, authentication worked
        snapshots = IncomeStatSnapshot.objects.all()
        self.assertGreater(snapshots.count(), 0)

    def test_snapshot_uses_correct_url(self):
        """Test that snapshot is generated from IncomeStatAdmin URL."""
        with override_settings(TESTING=True):
            # Mock the Client class to verify the correct URL is called
            with patch('analytics.utils.monthly_snapshot_saving.Client') as mock_client_class:
                mock_client_instance = MagicMock()
                mock_response = MagicMock()
                mock_response.context_data = {'snapshot': '<html>test</html>'}
                mock_client_instance.get.return_value = mock_response
                mock_client_class.return_value = mock_client_instance

                snapshot_service = SaveSnapshot()

                # We need to patch get_manager_departments to avoid department issues
                with patch('analytics.utils.monthly_snapshot_saving.get_manager_departments') as mock_depts:
                    from django.contrib.auth.models import Group
                    dept = Group.objects.filter(
                        department__isnull=False).first()
                    if dept:
                        mock_depts.return_value = [dept]
                        snapshot_service.save_snapshots()

                        # Verify the correct URL was called
                        mock_client_instance.get.assert_called()
                        call_args = mock_client_instance.get.call_args
                        url = call_args[0][0] if call_args[0] else ''
                        # Should contain incomestat in the URL
                        self.assertIn('incomestat', url)

    @override_settings(
        SECURE_HSTS_SECONDS=0,
        SECURE_SSL_REDIRECT=False,
        SECURE_HSTS_PRELOAD=False
    )
    def test_snapshot_with_security_settings_override(self):
        """Test that snapshots are saved with security settings disabled."""
        with override_settings(TESTING=True):
            snapshot_service = SaveSnapshot()
            snapshot_service.save_snapshots()

        snapshots = IncomeStatSnapshot.objects.all()
        self.assertGreater(snapshots.count(), 0)


# ============================================================================
# Integration Tests
# ============================================================================

@tag('Analytics')
class TestMonthlySnapshotSavingIntegration(BaseTestCase):
    """Integration tests for the complete MonthlySnapshotSaving system."""

    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()
        cls.superuser = User.objects.filter(is_superuser=True).first()
        if not cls.superuser:
            cls.superuser = User.objects.create_superuser(
                username='superadmin',
                email='super@example.com',
                password='testpass123'
            )

    def setUp(self):
        print(" Run Test Method:", self._testMethodName)

    def test_snapshot_creation_workflow(self):
        """Test that SaveSnapshot can create snapshot objects."""
        with override_settings(TESTING=True):
            snapshot_service = SaveSnapshot()
            # Run the snapshot service
            snapshot_service.save_snapshots()

        # Verify at least one snapshot was created
        snapshots = IncomeStatSnapshot.objects.all()
        self.assertGreater(snapshots.count(), 0)

    def test_snapshot_data_persistence(self):
        """Test that snapshot data is persisted correctly."""
        initial_count = IncomeStatSnapshot.objects.count()

        with override_settings(TESTING=True):
            snapshot_service = SaveSnapshot()
            snapshot_service.save_snapshots()

        final_count = IncomeStatSnapshot.objects.count()
        self.assertGreater(final_count, initial_count)

    @patch('analytics.utils.monthly_snapshot_saving.mail_admins')
    def test_system_handles_errors_gracefully(self, mock_mail_admins):
        """Test that the system handles errors gracefully."""
        with override_settings(TESTING=True):
            with patch('analytics.utils.monthly_snapshot_saving.SaveSnapshot.save_snapshots') as mock_save:
                mock_save.side_effect = ValueError("Test error")

                thread = MonthlySnapshotSaving()
                # Should not raise exception
                thread.run()

                # Admin email should have been sent
                mock_mail_admins.assert_called()

    def test_thread_lifecycle(self):
        """Test that MonthlySnapshotSaving thread can be created and run."""
        with override_settings(TESTING=True):
            with patch('analytics.utils.monthly_snapshot_saving.SaveSnapshot.save_snapshots'):
                thread = MonthlySnapshotSaving()

                # Thread should be daemon
                self.assertTrue(thread.daemon)

                # Thread should be a Thread instance
                self.assertIsInstance(thread, threading.Thread)


# ============================================================================
# Edge Case Tests
# ============================================================================

@tag('Analytics')
class TestMonthlySnapshotSavingEdgeCases(TestCase):
    """Test edge cases and boundary conditions."""

    def setUp(self):
        print(" Run Test Method:", self._testMethodName)

    def test_exact_snapshot_time(self):
        """Test calculation exactly at snapshot time (23:00:00)."""
        now = timezone.make_aware(datetime(2024, 1, 31, 23, 0, 0))
        secs = get_time_to_next_monthly_snapshot_saving(now)

        # Should be exactly 0
        self.assertEqual(secs, 0)

    def test_one_second_before_snapshot_time(self):
        """Test calculation one second before snapshot time."""
        now = timezone.make_aware(datetime(2024, 1, 31, 22, 59, 59))
        secs = get_time_to_next_monthly_snapshot_saving(now)

        # Should be exactly 1 second
        self.assertEqual(secs, 1)

    def test_december_to_january_transition(self):
        """Test time calculation for December (last day is 31st)."""
        now = timezone.make_aware(datetime(2024, 12, 1, 10, 0, 0))
        secs = get_time_to_next_monthly_snapshot_saving(now)

        # Should calculate correctly for December
        self.assertGreater(secs, 0)

    def test_month_with_30_days(self):
        """Test time calculation for months with 30 days."""
        now = timezone.make_aware(
            datetime(2024, 4, 1, 10, 0, 0))  # April has 30 days
        secs = get_time_to_next_monthly_snapshot_saving(now)

        save_dt = now.replace(
            day=30,
            hour=23,
            minute=0,
            second=0,
            microsecond=0
        )
        expected_secs = (save_dt - now).total_seconds()

        self.assertEqual(secs, expected_secs)

    def test_month_with_31_days(self):
        """Test time calculation for months with 31 days."""
        now = timezone.make_aware(
            datetime(2024, 5, 1, 10, 0, 0))  # May has 31 days
        secs = get_time_to_next_monthly_snapshot_saving(now)

        save_dt = now.replace(
            day=31,
            hour=23,
            minute=0,
            second=0,
            microsecond=0
        )
        expected_secs = (save_dt - now).total_seconds()

        self.assertEqual(secs, expected_secs)
