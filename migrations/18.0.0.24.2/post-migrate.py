# -*- coding: utf-8 -*-
import logging

from odoo import SUPERUSER_ID, api

_logger = logging.getLogger(__name__)


def _default_teachers_to_passlist(env):
    """Every teaching employee's user should land on "Current" (pasar lista) on login, not
    "History" - found 2026-09-11 while diagnosing why a secretary account defaulted there
    instead: no EMS code has ever set res.users.action_id, so the 32 real teacher accounts that
    already had one explicitly set had it pointing at action_attendance_session_tree
    ("History") instead, presumably set by hand at account creation time. Also fixes
    base.default_user (the template duplicated when onboarding new teachers, confirmed by the
    developer 2026-09-11) so future accounts inherit the right default without manual
    intervention."""
    passlist_action = env.ref('ems.action_attendance_passlist')
    teacher_users = env['res.users'].search([
        ('employee_ids.employee_type', '=', 'teacher'),
    ])
    (teacher_users | env.ref('base.default_user')).write({'action_id': passlist_action.id})
    _logger.info(
        "Migration 18.0.0.24.2: set action_id=action_attendance_passlist for %s teacher "
        "account(s) plus base.default_user.", len(teacher_users))


def _default_secretary_to_community(env):
    """Backfill for the same issue #440 fix as hr.employee._sync_secretary_home_action() (added
    the same version): re-runs that logic once for every employee whose job already maps to
    ems.group_secretary, so accounts created before this fix existed (Alba Martín's real
    account among them) get the same "Educational Community" default too, not just future
    ones."""
    secretary_job = env.ref('ems.job_secretary')
    employees = env['hr.employee'].search([('job_id', '=', secretary_job.id)])
    employees._sync_security_groups()
    _logger.info(
        "Migration 18.0.0.24.2: re-ran the secretary home-action default for %s employee(s).",
        len(employees))


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
        "Migration 18.0.0.24.2: restored %d missing student(s) across %d attendance schedule "
        "line(s).", added, healed_lines)


def migrate(cr, _version):
    env = api.Environment(cr, SUPERUSER_ID, {})
    _default_teachers_to_passlist(env)
    _default_secretary_to_community(env)
    _heal_attendance_rosters(env)
