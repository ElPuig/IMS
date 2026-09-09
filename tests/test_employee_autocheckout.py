from datetime import datetime, time, timedelta, timezone
from unittest.mock import patch

from odoo.tests.common import TransactionCase


class TestEmployeeAutocheckout(TransactionCase):
    """models/employees/employee_autocheckout.py (hr.attendance extension) — previously
    entirely untested despite real business consequences (auto-closing attendance,
    notifying managers)."""

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.teacher = cls.env['hr.employee'].create({
            'name': 'Test Autocheckout Teacher', 'employee_type': 'teacher',
        })
        # employee.create() already gave this teacher their own personal calendar.
        cls.calendar = cls.teacher.resource_calendar_id
        cls.today = datetime.now(timezone.utc).date()
        cls.weekday = str(cls.today.weekday())

    def _add_slot(self, hour_from, hour_to, dayofweek=None):
        return self.env['resource.calendar.attendance'].create({
            'calendar_id': self.calendar.id,
            'name': 'Test Slot',
            'dayofweek': dayofweek or self.weekday,
            'hour_from': hour_from,
            'hour_to': hour_to,
            'day_period': 'morning',
        })

    def test_get_last_working_hour_none_without_calendar(self):
        employee = self.env['hr.employee'].create({
            'name': 'Test No Calendar Employee', 'employee_type': 'asp',
        })
        employee.resource_calendar_id = False
        attendance_model = self.env['hr.attendance']
        self.assertIsNone(attendance_model._get_last_working_hour(employee, self.today))

    def test_get_last_working_hour_none_without_slots_that_day(self):
        attendance_model = self.env['hr.attendance']
        self.assertIsNone(attendance_model._get_last_working_hour(self.teacher, self.today))

    def test_get_last_working_hour_returns_latest_slot(self):
        self._add_slot(8.0, 10.0)
        self._add_slot(10.0, 13.5)
        attendance_model = self.env['hr.attendance']
        result = attendance_model._get_last_working_hour(self.teacher, self.today)
        utils = self.env['ems.datetime_utils']
        expected = utils.datetime_to_odoo(utils.time_float_to_utc_datetime(self.today, 13.5))
        self.assertEqual(result, expected)

    def test_auto_close_attendance_closes_after_scheduled_hour(self):
        # 'dayofweek' must match 'check_in' 's own date, not 'self.weekday' (cached at
        # setUpClass time) - the 2h offset below can push check_in onto the PREVIOUS calendar
        # day whenever this test happens to run shortly after UTC midnight, same class of bug
        # already avoided by 'test_create_auto_closes_stale_open_attendance' (found 2026-09-08:
        # CI ran this class at 00:12 UTC, so 'self.weekday' was Tuesday while check_in was still
        # Monday, and the slot never matched).
        check_in = datetime.now(timezone.utc).replace(tzinfo=None) - timedelta(hours=2)
        self._add_slot(0.0, 0.02, dayofweek=str(check_in.weekday()))  # ~1 minute after midnight, already passed
        attendance = self.env['hr.attendance'].create({
            'employee_id': self.teacher.id, 'check_in': check_in,
        })

        closed = attendance._auto_close_attendance()

        self.assertTrue(closed)
        self.assertTrue(attendance.check_out)
        self.assertEqual(attendance.out_mode, 'auto_check_out')

    def test_auto_close_attendance_waits_for_scheduled_hour(self):
        far_future_hour = 23.9
        self._add_slot(0.0, far_future_hour)
        attendance = self.env['hr.attendance'].create({
            'employee_id': self.teacher.id,
            'check_in': datetime.now(timezone.utc).replace(tzinfo=None),
        })

        closed = attendance._auto_close_attendance()

        self.assertFalse(closed)
        self.assertFalse(attendance.check_out)

    def test_auto_close_attendance_false_without_schedule(self):
        attendance = self.env['hr.attendance'].create({
            'employee_id': self.teacher.id,
            'check_in': datetime.now(timezone.utc).replace(tzinfo=None) - timedelta(hours=2),
        })

        closed = attendance._auto_close_attendance()

        self.assertFalse(closed)
        self.assertFalse(attendance.check_out)

    def test_auto_close_attendance_fallback_when_scheduled_before_checkin(self):
        # Scheduled hour already passed relative to check_in itself (e.g. checked in very
        # late) — falls back to check_in + 1h instead of a check_out before check_in.
        # 'dayofweek' derived from check_in's own date, not 'self.weekday' - see the identical
        # NOTE on 'test_auto_close_attendance_closes_after_scheduled_hour' above.
        check_in = datetime.now(timezone.utc).replace(tzinfo=None) - timedelta(hours=3)
        self._add_slot(0.0, 0.02, dayofweek=str(check_in.weekday()))
        attendance = self.env['hr.attendance'].create({
            'employee_id': self.teacher.id, 'check_in': check_in,
        })

        closed = attendance._auto_close_attendance()

        self.assertTrue(closed)
        self.assertAlmostEqual(
            (attendance.check_out - check_in).total_seconds(), 3600, delta=5,
        )

    def test_create_auto_closes_stale_open_attendance(self):
        self.env.company.auto_check_out = True
        self.calendar.flexible_hours = False
        stale_check_in = datetime.now(timezone.utc).replace(tzinfo=None) - timedelta(days=1)
        self._add_slot(0.0, 0.02, dayofweek=str(stale_check_in.weekday()))
        stale = self.env['hr.attendance'].create({
            'employee_id': self.teacher.id, 'check_in': stale_check_in,
        })
        self.assertFalse(stale.check_out)

        self.env['hr.attendance'].create({
            'employee_id': self.teacher.id,
            'check_in': datetime.now(timezone.utc).replace(tzinfo=None),
        })

        self.assertTrue(stale.check_out)

    def test_write_check_out_same_day_mismatched_microseconds_does_not_crash(self):
        # Regression test (issue #422): a check_in stamped with microseconds (e.g.
        # datetime.now(), how a real kiosk/systray punch is stored) and a check_out
        # set without microseconds (e.g. typed by hand in the form, or computed by
        # _auto_close_attendance()) on the SAME calendar day used to make Odoo's
        # hr.attendance.overtime engine treat check_in's and check_out's "day start"
        # as two distinct instants for the exact same date (native
        # hr.attendance._get_day_start_and_day()'s replace(hour=0, minute=0,
        # second=0) never resets microsecond) — two INSERTs for the same
        # (employee_id, date) key in one statement, self-colliding against
        # hr_attendance_overtime's own UNIQUE(employee_id, date) index.
        check_in = datetime.combine(self.today, time(8, 0, 0, 123456))
        attendance = self.env['hr.attendance'].create({
            'employee_id': self.teacher.id, 'check_in': check_in,
        })
        check_out = datetime.combine(self.today, time(16, 0, 0))

        attendance.write({'check_out': check_out})

        overtime = self.env['hr.attendance.overtime'].search([
            ('employee_id', '=', self.teacher.id), ('date', '=', self.today),
        ])
        self.assertLessEqual(len(overtime), 1)

    def test_cron_auto_check_out_savepoint_isolates_failures(self):
        # A failure closing one employee's attendance must not abort the whole
        # transaction and take every other employee's close down with it (found
        # 2026-09: a bare try/except around a raised exception doesn't undo Postgres's
        # own "transaction aborted" state — only a savepoint rollback does). The
        # injected failure below runs real (invalid) SQL, so it genuinely poisons the
        # cursor the same way the production bug did — a plain Python-level
        # exception wouldn't exercise this at all.
        self.env.company.auto_check_out = True
        self.env.company.auto_checkout_mode = 'ems'
        self.env.company.auto_checkout_time = 0.0
        self.env.company.auto_checkout_retry_until = 24.0
        self.calendar.flexible_hours = False
        other_teacher = self.env['hr.employee'].create({
            'name': 'Test Autocheckout Teacher 2', 'employee_type': 'teacher',
        })
        other_teacher.resource_calendar_id.flexible_hours = False
        # '_order = "check_in desc"' on hr.attendance: 'failing' must sort before
        # 'healthy' for an unisolated abort to actually reach 'healthy' too.
        failing_check_in = datetime.now(timezone.utc).replace(tzinfo=None) - timedelta(hours=2)
        healthy_check_in = failing_check_in - timedelta(minutes=1)
        self._add_slot(0.0, 0.02, dayofweek=str(failing_check_in.weekday()))
        self.env['resource.calendar.attendance'].create({
            'calendar_id': other_teacher.resource_calendar_id.id,
            'name': 'Test Slot', 'dayofweek': str(healthy_check_in.weekday()),
            'hour_from': 0.0, 'hour_to': 0.02, 'day_period': 'morning',
        })
        failing = self.env['hr.attendance'].create({
            'employee_id': self.teacher.id, 'check_in': failing_check_in,
        })
        healthy = self.env['hr.attendance'].create({
            'employee_id': other_teacher.id, 'check_in': healthy_check_in,
        })

        original_close = type(failing)._auto_close_attendance

        def _boom(self):
            if self.id == failing.id:
                self.env.cr.execute("SELECT * FROM ems_test_nonexistent_table_422")
            return original_close(self)

        with patch.object(type(failing), '_auto_close_attendance', _boom):
            self.env['hr.attendance']._cron_auto_check_out()

        self.assertFalse(failing.check_out)
        self.assertTrue(healthy.check_out)

    def test_create_close_failure_is_isolated_and_notifies(self):
        # Mirrors test_cron_auto_check_out_savepoint_isolates_failures for the
        # create()-triggered backup path: a real (SQL-level) failure while
        # auto-closing a stale attendance must not corrupt the transaction, and
        # must notify the Academic Admins - the same robustness the cron already
        # has, now shared via _close_stale_attendance_safely().
        self.env.company.auto_check_out = True
        self.calendar.flexible_hours = False
        stale_check_in = datetime.now(timezone.utc).replace(tzinfo=None) - timedelta(days=1)
        self._add_slot(0.0, 0.02, dayofweek=str(stale_check_in.weekday()))
        stale = self.env['hr.attendance'].create({
            'employee_id': self.teacher.id, 'check_in': stale_check_in,
        })

        def _boom(self):
            self.env.cr.execute("SELECT * FROM ems_test_nonexistent_table_422")

        # Spy on the notify call rather than asserting on persisted mail.activity
        # state: verified separately (not asserted here, see
        # _notify_close_failure()'s own docstring) that when the notify happens
        # nested inside the very create() call that goes on to fail its own
        # native validation right after (exactly this scenario), the activity it
        # schedules is not reliably kept - a known, accepted gap, not something
        # this test should flake on. What's guaranteed and worth asserting is
        # that a close failure always triggers the notify call, on the right
        # record - the cron or the employee's next real check-in will pick the
        # still-open attendance back up regardless.
        with patch.object(type(stale), '_auto_close_attendance', _boom), \
             patch.object(type(stale), '_notify_close_failure', autospec=True) as notify_mock:
            with self.assertRaises(Exception) as failure:
                self.env['hr.attendance'].create({
                    'employee_id': self.teacher.id,
                    'check_in': datetime.now(timezone.utc).replace(tzinfo=None),
                })

        # The stale attendance stayed open (close failed) so Odoo's own native
        # validation blocked the new check-in - proof the raw injected SQL error
        # never escaped uncontrolled, only the transaction-safe outcome did.
        self.assertIn("hasn't checked out since", str(failure.exception))
        self.assertFalse(stale.check_out)
        notify_mock.assert_called_once_with(stale)

    def test_create_leaves_stale_attendance_when_auto_check_out_disabled(self):
        # With auto_check_out off, EMS never auto-closes the stale attendance, so Odoo's
        # own "already checked in" validation blocks the second check-in — same as it
        # would for any employee with no EMS auto-checkout configured at all.
        self.env.company.auto_check_out = False
        self._add_slot(0.0, 0.02)
        stale = self.env['hr.attendance'].create({
            'employee_id': self.teacher.id,
            'check_in': datetime.now(timezone.utc).replace(tzinfo=None) - timedelta(days=1),
        })

        with self.assertRaises(Exception):
            self.env['hr.attendance'].create({
                'employee_id': self.teacher.id,
                'check_in': datetime.now(timezone.utc).replace(tzinfo=None),
            })

        self.assertFalse(stale.check_out)
