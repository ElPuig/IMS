# -*- coding: utf-8 -*-

from odoo import api, fields, models


class ems_group_schedule(models.Model):
    # NOTE: an explicit '_name' is required here — a 2-item '_inherit' list without one would make
    # Odoo's metaclass define a brand-new model named after this Python class instead of extending
    # 'ems.group' in place (see MetaModel in odoo/models.py).
    _name = 'ems.group'
    _inherit = ['ems.group', 'ems.schedule_report_mixin']

    # Union of two sources: the group's real teaching slots, aggregated from every teacher's
    # calendar whose 'group_ids' includes this group, and — when derivable — the group's break
    # period, taken from its level's schedule framework (see '_get_break_entries'). Not stored,
    # same pattern already used for 'enrolled_student_ids'.
    schedule_attendance_ids = fields.Many2many(string="Schedule", comodel_name="resource.calendar.attendance",
        compute="_compute_schedule_attendance_ids")

    # A real dependency on 'resource.calendar.attendance' itself can't be expressed (a cross-model
    # search) - see the equivalent note on res.partner (student)._compute_schedule_attendance_ids
    # for why this still matters even so (invalidating a value the SAME transaction cached before
    # 'level_id'/'shift' changed - a fresh web request always recomputes regardless).
    @api.depends('level_id', 'shift')
    def _compute_schedule_attendance_ids(self):
        # 'active_test=True' forced explicitly, not left to the ORM's own default: this compute
        # can run under a caller context that already set active_test=False for an unrelated
        # reason (found 2026-09-10 on the student's own version of this field, opened from
        # ems.action_student_kanban - its context turns active_test off so archived/withdrawn
        # students still show up in that list). Without forcing it back on here, a stale/archived
        # calendar's own leftover attendance rows (never deleted, only archived, by course
        # transition's calendar rollover) would resurface as if they were still part of this
        # group's CURRENT schedule - duplicated against, and often overlapping, the real one.
        Attendance = self.env['resource.calendar.attendance'].with_context(active_test=True)
        for group in self:
            teaching = Attendance.search([('group_ids', '=', group.id)])
            group.schedule_attendance_ids = teaching | group._get_break_entries()

    def _get_break_entries(self):
        """The group's break/patio period, derived from its level's schedule framework — see
        'ems.schedule_report_mixin._get_level_break_entries' for the actual derivation."""
        self.ensure_one()
        return self._get_level_break_entries(self.level_id, self.shift)

    # 'get_schedule_report_lines()'/'get_subject_teachers_summary()' are inherited as-is from
    # 'ems.schedule_report_mixin' — a group's own 'shift' field is exactly what
    # 'ems.schedule_report_mixin._schedule_report_shift()' already defaults to, so no override is
    # needed here (compare with res.partner (student), which does need one).
