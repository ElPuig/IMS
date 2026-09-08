# -*- coding: utf-8 -*-
import logging

from odoo import SUPERUSER_ID, api

_logger = logging.getLogger(__name__)


def _backfill_calendar_to_schedule_link(env):
    """Bottom-up sync redesign (see models/attendance/attendance_schedule.py's
    '_relocate_via_calendar_blocks'/'_archive_via_calendar_blocks' docstrings and
    docs/en/developers/attendance/attendance_template.md's "Bottom-up sync redesign" section):
    the design invariant those two shared methods (and 'ems.group._resolve_or_flag_pending_block')
    now rely on is that every active 'ems.attendance_schedule' line always has at least one real
    'resource.calendar.attendance' row pointing at it via 'attendance_schedule_id' - the calendar is
    always the entry point, never the other way round.

    That FK is only ever set by 'ems.attendance_template._link_calendar_attendance', called at the
    end of 'sync_from_schedule_batch' - a calendar block created or resynced before this FK column
    existed (added 2026-08-11) or before the automatic create/write/unlink hook existed (added the
    same day as this migration, see the bottom-up sync redesign's Phase 4) never went through that
    step, so it can be missing the link even though a matching schedule line genuinely exists.

    Rather than writing a bespoke matching query here, this reuses the exact same full
    archive-and-rebuild-from-calendar tool already used by 'migrations/18.0.0.22.0' and
    'migrations/18.0.0.23.1'/'18.0.0.23.5' for the original calendar-driven-templates rollout -
    'regenerate_all_from_calendars()' rebuilds every active template/line straight from each
    teacher's current calendar and links every calendar row it touches by construction, so running
    it once more here closes this exact gap without inventing new logic. Confirmed via a dry run
    against this project's own dev database (2026-09-08, rolled back, never committed): 11
    pre-existing unlinked lines dropped to 0, with zero unresolved room conflicts."""
    skipped = env['ems.attendance_template'].regenerate_all_from_calendars()
    _logger.info(
        "Migration 18.0.0.23.6: archived every pre-existing ems.attendance_template and "
        "regenerated a fresh, calendar-linked set from each teacher's current working schedule "
        "(backfill for calendar blocks that predate the attendance_schedule_id FK/automatic sync "
        "hook).")
    if not skipped:
        return

    weekdays = dict(env['ems.attendance_schedule'].weekdays_selection)
    for item in skipped:
        entry, other = item['entry'], item['conflicts_with_entry']
        _logger.warning(
            "Migration 18.0.0.23.6: SKIPPED regenerating a template for %s (%s, %s %s-%s, %s) - "
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
        "Migration 18.0.0.23.6: %d entrie(s) skipped due to unresolved room conflicts - see the "
        "warnings above for exactly which ones and what each one conflicted with.", len(skipped))


def migrate(cr, _version):
    env = api.Environment(cr, SUPERUSER_ID, {})
    _backfill_calendar_to_schedule_link(env)
