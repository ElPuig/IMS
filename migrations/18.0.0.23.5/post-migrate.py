# -*- coding: utf-8 -*-
import logging

from odoo import SUPERUSER_ID, api

_logger = logging.getLogger(__name__)


def _regenerate_attendance_templates_from_calendars(env):
    """Fixes production data left behind by the bug fixed in this same version
    (`ems.attendance_template._plan_schedule_sync`, see models/attendance/attendance_template.py):
    a solo teacher who taught one subject to two or more different groups (no co-teaching) could
    have every one of their templates for that subject silently archived, with nothing recreated
    in their place, the next time their schedule was resynced (a working-schedules re-import, or a
    live edit on their own Schedule tab) - even though their calendar stayed completely correct.

    Rather than trying to detect which teachers were actually hit (a targeted detection would risk
    fragmenting a co-taught template if it missed one side of it - a real teacher who splits a
    reconstructed group differently from before), this reuses the exact same
    `regenerate_all_from_calendars()` full rebuild already used by `migrations/18.0.0.22.0` for the
    original calendar-driven-templates rollout: archive every active template, rebuild an
    equivalent set from each teacher's CURRENT (correct) calendar. Safe to run again - archiving
    never touches real attendance-session history (see that method's own docstring) - at the cost
    of every already-correct template also getting a new id/color even though nothing about it
    actually changes."""
    skipped = env['ems.attendance_template'].regenerate_all_from_calendars()
    _logger.info(
        "Migration 18.0.0.23.5: archived every pre-existing ems.attendance_template and "
        "regenerated a fresh, calendar-backed set from each teacher's current working schedule "
        "(repair for the same-subject/several-groups sync bug fixed in this version).")
    if not skipped:
        return

    weekdays = dict(env['ems.attendance_schedule'].weekdays_selection)
    for item in skipped:
        entry, other = item['entry'], item['conflicts_with_entry']
        _logger.warning(
            "Migration 18.0.0.23.5: SKIPPED regenerating a template for %s (%s, %s %s-%s, %s) - "
            "unresolved room conflict with %s (%s, %s %s-%s, %s). This is not corrected "
            "automatically - review both teachers' real working schedules by hand and re-sync "
            "the one that's wrong.",
            item['teacher'].display_name, env['ems.subject'].browse(entry['subject_id']).display_name,
            weekdays.get(entry['dayofweek']), entry['hour_from'], entry['hour_to'],
            env['ems.space'].browse(entry['space_id']).display_name,
            item['conflicts_with_teacher'].display_name,
            env['ems.subject'].browse(other['subject_id']).display_name,
            weekdays.get(other['dayofweek']), other['hour_from'], other['hour_to'],
            env['ems.space'].browse(other['space_id']).display_name,
        )
    _logger.warning(
        "Migration 18.0.0.23.5: %d entrie(s) skipped due to unresolved room conflicts - see the "
        "warnings above for exactly which ones and what each one conflicted with.", len(skipped))


def migrate(cr, _version):
    env = api.Environment(cr, SUPERUSER_ID, {})
    _regenerate_attendance_templates_from_calendars(env)
