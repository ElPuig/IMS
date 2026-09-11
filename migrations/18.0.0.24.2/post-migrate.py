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


def migrate(cr, _version):
    env = api.Environment(cr, SUPERUSER_ID, {})
    _default_teachers_to_passlist(env)
    _default_secretary_to_community(env)
