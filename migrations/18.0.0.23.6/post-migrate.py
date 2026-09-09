# -*- coding: utf-8 -*-
import logging
from datetime import timedelta

from odoo import SUPERUSER_ID, api

_logger = logging.getLogger(__name__)


def _find_stale_attendance_ids(cr):
    """Candidates: still open, or closed on a different calendar day than they were
    opened (both symptoms of the bug fixed in this same version - see
    'employee_autocheckout.py::_get_day_start_and_day'). Restricted to the same
    eligibility criteria the feature itself already uses, so an employee
    deliberately excluded from auto-checkout is never touched here either."""
    cr.execute("""
        SELECT a.id
          FROM hr_attendance a
          JOIN hr_employee e ON e.id = a.employee_id
          JOIN res_company c ON c.id = e.company_id
     LEFT JOIN resource_calendar rc ON rc.id = e.resource_calendar_id
         WHERE c.auto_check_out = true
           AND COALESCE(rc.flexible_hours, false) = false
           AND (a.check_out IS NULL OR a.check_in::date != a.check_out::date)
    """)
    return [row[0] for row in cr.fetchall()]


def _close_stale_attendances_same_day(env):
    """Repair for production data left behind by issue #422: attendances that stayed
    open for real, or that only got closed days later by the employee's own next
    kiosk badge-in (a different calendar day), producing nonsensical multi-day
    worked_hours (e.g. 60+ hours in one day). Per the developer (2026-09-09): force
    each one closed on the SAME calendar day it was opened, at the employee's last
    scheduled working hour that day, or 14:00 local time if no schedule is found for
    that day - "no pasa nada si hay días sin fichar, estamos en pruebas."."""
    attendance_ids = _find_stale_attendance_ids(env.cr)
    if not attendance_ids:
        _logger.info("Migration 18.0.0.23.6: no stale attendances found, nothing to do.")
        return

    _logger.info("Migration 18.0.0.23.6: closing %d stale attendance(s) same-day.", len(attendance_ids))
    utils = env['ems.datetime_utils']
    fixed, failed = 0, 0

    for attendance in env['hr.attendance'].browse(attendance_ids):
        work_date = attendance.check_in.date()
        check_out = attendance._get_last_working_hour(attendance.employee_id, work_date)
        if not check_out or check_out <= attendance.check_in:
            check_out = utils.datetime_to_odoo(utils.time_float_to_utc_datetime(work_date, 14.0))
        if check_out <= attendance.check_in:
            # 14:00 fallback still before check_in (e.g. an evening check-in) -
            # same "check_in + 1h" fallback _auto_close_attendance() itself uses.
            check_out = attendance.check_in + timedelta(hours=1)

        try:
            with env.cr.savepoint():
                attendance.write({'check_out': check_out, 'out_mode': 'auto_check_out'})
            fixed += 1
        except Exception:
            failed += 1
            _logger.exception(
                "Migration 18.0.0.23.6: could not close attendance id=%d, left as-is.",
                attendance.id,
            )

    _logger.info("Migration 18.0.0.23.6: closed %d attendance(s), %d left unfixed.", fixed, failed)


def migrate(cr, version):
    env = api.Environment(cr, SUPERUSER_ID, {})
    _close_stale_attendances_same_day(env)
