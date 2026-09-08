# -*- coding: utf-8 -*-

from odoo import models

# Two hour_from/hour_to values meant to represent the exact same moment can differ by a tiny
# float remainder depending on how each was computed/entered (e.g. a framework's break stored as
# the literal '11.416667' vs a real period's own hour_from computed as '11 + 25/60' ==
# 11.416666666666666) — a strict '<'/'==' comparison would misread that hair's-width gap as a
# real difference. 1/120 hour (30s) safely absorbs that noise without being large enough to treat
# two genuinely distinct, minutes-apart periods as touching. Shared here (not private to one
# model) because both 'hr.employee._get_derived_break_entries' (employees/employee.py) and
# 'ems.course._merge_absorbed_periods' (attendance/guard_duty_board.py) need the exact same
# tolerance for the same kind of comparison.
HOUR_EPSILON = 1 / 120


class EmsScheduleReportMixin(models.AbstractModel):
    _name = 'ems.schedule_report_mixin'
    _description = "Shared coloring/time-formatting helpers for weekly schedule PDF reports."

    # NOTE: assigned in first-seen order to the distinct items on a schedule, so two unrelated
    # items only ever share a color once the palette itself runs out.
    REPORT_COLOR_PALETTE = [
        '#5b8def', '#f4a261', '#2a9d8f', '#e76f51', '#8ecae6', '#ffb703',
        '#c77dff', '#06d6a0', '#ef476f', '#118ab2', '#bc6c25', '#9d4edd',
    ]

    def _report_color_key(self, attendance):
        return ('non_teaching', attendance.non_teaching.id) if attendance.non_teaching else ('subject', attendance.subject_id.id)

    def _format_report_time(self, value):
        hour, minutes = divmod(round(value * 60), 60)
        return f"{hour:02d}:{minutes:02d}"
