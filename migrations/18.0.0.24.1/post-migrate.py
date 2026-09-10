# -*- coding: utf-8 -*-
import logging

from odoo import SUPERUSER_ID, api

_logger = logging.getLogger(__name__)


def _heal_attendance_rosters(env):
    """Issue #435: re-adds to every active 'ems.attendance_schedule' the students who are enrolled
    in its template's (subject_id, group_ids) but are missing from its own 'student_ids' roster.

    Why any of them are missing: until this version, 'ems.enrollment.create()' 's roster cascade
    ran with the acting user's own rights, and both attendance models are access-restricted in
    ways 'ems.enrollment' is not - a teacher (or a secretary who also teaches) only sees the
    templates they teach themselves (rule_attendance_template_teacher_own /
    rule_attendance_schedule_teacher_own), so the search behind the cascade returned nothing and
    the whole thing was a silent no-op. The code fix (models/contacts/enrollment.py, this same
    version) stops it happening again; this heals the rows it already left behind. Measured on the
    2026-09-10 production dump: 189 entries missing across 51 active schedule lines, every one of
    them from enrollments created by a single non-admin user.

    ADD-ONLY, deliberately: a roster is allowed to be customised per line (a student sitting in, a
    student excused - see plans/calendar_driven_attendance_templates.md, point 1), so this never
    removes anybody, unlike 'reload_students()' which wipes first. It only restores what the
    cascade should have written at enrollment time. Confirmed against that same production dump
    that per-line customisation barely exists in practice (one single roster entry with no
    matching enrollment in the entire database), so the add-only direction is where all the real
    drift is.

    Only ACTIVE lines: an archived one is history and must stay exactly as attendance was taken.
    Idempotent - a second run finds nothing to add.

    No 'post_init_hook' counterpart, unlike most one-time actions (see CLAUDE.md's Migrations
    section): a brand-new installation has no enrollments and no schedule lines yet, so there is
    nothing for it to heal - the fixed cascade covers it from its very first enrollment onwards.
    """
    Enrollment = env['ems.enrollment']
    added = 0
    healed_lines = 0
    for schedule in env['ems.attendance_schedule'].search([]):
        template = schedule.attendance_template_id
        if not template.subject_id or not template.group_ids:
            continue
        # Same roster definition 'ems.attendance_schedule.fill_students()' uses, minus its wipe.
        students = Enrollment.search([
            ('group_id', 'in', template.group_ids.ids),
            ('subject_id', '=', template.subject_id.id),
        ]).mapped('student_id')
        missing = students - schedule.student_ids
        if not missing:
            continue
        schedule.student_ids = [(4, student.id) for student in missing]
        added += len(missing)
        healed_lines += 1
    _logger.info(
        "Migration 18.0.0.24.1: restored %d missing student(s) across %d attendance schedule "
        "line(s).", added, healed_lines)


def migrate(cr, _version):
    env = api.Environment(cr, SUPERUSER_ID, {})
    _heal_attendance_rosters(env)
