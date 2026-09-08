from datetime import datetime, timedelta, timezone

from odoo.tests.common import TransactionCase

from .common import mock_outgoing_email


class TestEmployeeAutocheckout(TransactionCase):
    """models/employees/employee_autocheckout.py (hr.attendance extension) — previously
    entirely untested despite real business consequences (auto-closing attendance,
    notifying managers)."""

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        # Approving an absence posts to the chatter and notifies its followers - see CLAUDE.md's
        # 'Email safety in tests'.
        mock_outgoing_email(cls)
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
        self._add_slot(0.0, 0.02)  # ~1 minute after midnight, already passed
        check_in = datetime.now(timezone.utc).replace(tzinfo=None) - timedelta(hours=2)
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
        self._add_slot(0.0, 0.02)
        check_in = datetime.now(timezone.utc).replace(tzinfo=None) - timedelta(hours=3)
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

    # --- Approved absences shorten the working day ------------------------------------------
    #
    # An auto check-out that reads the raw weekly timetable closes the attendance at the end of
    # a day the employee was partly on leave for, crediting hours they had permission to miss.
    # See docs/en/developers/employees/absence.md.

    def _approved_absence(self, day, hour_from=None, hour_to=None):
        vals = {
            'employee_id': self.teacher.id,
            'holiday_status_id': self.env.ref('ems.leave_type_justified').id,
            'request_date_from': day,
            'request_date_to': day,
            'ems_submitted': True,
            'ems_responsible_declaration': True,
        }
        if hour_from is None:
            vals['ems_full_day'] = True
        else:
            vals.update({'ems_full_day': False,
                         'request_hour_from': hour_from, 'request_hour_to': hour_to})
        leave = self.env['hr.leave'].create(vals)
        leave.action_approve()
        return leave

    def test_an_approved_afternoon_absence_moves_the_check_out_earlier(self):
        """The teacher leaves at 14:00 with the afternoon approved and forgets to check out:
        the attendance must close at 14:00, not at the untouched end of their timetable."""
        self._add_slot(8.0, 14.0)
        self._add_slot(15.0, 18.0)
        self._approved_absence(self.today, hour_from=15.0, hour_to=18.0)

        result = self.env['hr.attendance']._get_last_working_hour(self.teacher, self.today)

        utils = self.env['ems.datetime_utils']
        self.assertEqual(result, utils.datetime_to_odoo(
            utils.time_float_to_utc_datetime(self.today, 14.0)),
            "the afternoon was approved off, so 14:00 is the last hour actually expected")

    def test_without_any_absence_the_whole_timetable_still_counts(self):
        """The fix must not move the check-out on an ordinary day."""
        self._add_slot(8.0, 14.0)
        self._add_slot(15.0, 18.0)

        result = self.env['hr.attendance']._get_last_working_hour(self.teacher, self.today)

        utils = self.env['ems.datetime_utils']
        self.assertEqual(result, utils.datetime_to_odoo(
            utils.time_float_to_utc_datetime(self.today, 18.0)))

    def test_a_whole_day_absence_leaves_nothing_to_close_at(self):
        """Nothing was expected of them at all, so there is no scheduled hour to close at and
        the attendance is deliberately left open for a human to correct - inventing an hour
        here is exactly what this fix is removing."""
        self._add_slot(8.0, 14.0)
        self._approved_absence(self.today)

        self.assertIsNone(
            self.env['hr.attendance']._get_last_working_hour(self.teacher, self.today))

    def test_a_pending_request_does_not_move_the_check_out(self):
        """Only an approved absence frees the employee from those hours."""
        self._add_slot(8.0, 14.0)
        self._add_slot(15.0, 18.0)
        leave = self.env['hr.leave'].create({
            'employee_id': self.teacher.id,
            'holiday_status_id': self.env.ref('ems.leave_type_justified').id,
            'request_date_from': self.today, 'request_date_to': self.today,
            'ems_full_day': False, 'request_hour_from': 15.0, 'request_hour_to': 18.0,
            'ems_submitted': True, 'ems_responsible_declaration': True,
        })
        self.assertEqual(leave.state, 'confirm')

        result = self.env['hr.attendance']._get_last_working_hour(self.teacher, self.today)

        utils = self.env['ems.datetime_utils']
        self.assertEqual(result, utils.datetime_to_odoo(
            utils.time_float_to_utc_datetime(self.today, 18.0)))
