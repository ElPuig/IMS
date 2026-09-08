# -*- coding: utf-8 -*-

from collections import defaultdict

from odoo import api, fields, models

WEEKDAYS = ('0', '1', '2', '3', '4')
# Mirrors ems.group's own SHIFT_HOURS (models/contacts/group_schedule.py) — the guard duty board
# needs the same morning/afternoon split, but rendered as weekday x shift tables with one column
# per group rather than one column per weekday, so it can't reuse that method as-is.
SHIFT_HOURS = {
    'morning': (8, 15),
    'afternoon': (15, 22),
}

# Which absence requests are worth putting on the board, and how each one is reported to the
# screen. 'approved' is a fact to plan around; 'pending' is a warning that one may be coming -
# hr_holidays' two pre-approval states are deliberately collapsed into a single one here,
# because the difference between "waiting for the first approver" and "waiting for the second"
# changes nothing for whoever is assigning guards. Refused and cancelled requests are absent
# from this mapping entirely, which is what keeps them off the board.
ABSENCE_STATES = {
    'confirm': 'pending',
    'validate1': 'pending',
    'validate': 'approved',
}

# A whole-day absence, as an hour interval, so it can be compared against a schedule period the
# same way a partial one is - no special case anywhere downstream.
WHOLE_DAY = (0.0, 24.0)


class EmsCourseGuardDutyBoard(models.Model):
    # NOTE: extends 'ems.course' in place (not a new model) — a 2-item '_inherit' list without an
    # explicit '_name' would make Odoo's metaclass define a brand-new model instead (see MetaModel
    # in odoo/models.py). Same pattern as ems_working_schedule/resource.calendar and
    # ems_group_schedule/ems.group.
    #
    # This lives on 'ems.course' (a real, always-existing, already-readable-by-every-teacher
    # model — see security/ir.model.access.csv's ems.access_ems_course_teacher) rather than a
    # dedicated TransientModel wizard, deliberately: an earlier version used a TransientModel
    # opened via a dynamic ir.actions.server, which meant the URL bar showed a raw
    # "ems.guard_duty_board/<id>" instead of a stable "action-<xmlid>" like every other EMS
    # screen — Odoo can only put a real xmlid in the URL for a *statically declared* action, and
    # a server action that returns a dynamically-built act_window dict has no xmlid of its own to
    # show. Binding to 'ems.course' instead means the board's own screen is a plain
    # ir.actions.client (a real, static, URL-addressable action — see
    # views/attendance/guard_duty_board/menu.xml) with no per-visit record to create/open at all.
    _name = 'ems.course'
    _inherit = ['ems.course', 'ems.schedule_report_mixin']

    def _get_guard_duty_board_attendance_ids(self):
        """Every real (non-framework) teacher's Mon-Fri attendance row, across every teacher —
        same aggregation idea as ems.group._compute_schedule_attendance_ids
        (models/contacts/group_schedule.py), generalized from "this group" to "the whole centre".
        Deliberately not filtered by 'calendar_id.course_id' — mirrors that same precedent, which
        aggregates the same way without a course filter either: a course-transitioned-out
        calendar/attendance row is archived (active=False, see
        ems_working_schedule_assignation.active's own NOTE), so this plain search() already only
        ever returns the current course's real, active schedules, and stays correct even for a
        legacy calendar whose 'course_id' was never backfilled (added 2026-08-06, not every
        pre-existing row necessarily has it set).

        The explicit 'calendar_id.active' check below is defense-in-depth, not redundant with the
        above: 'ems_working_schedule.action_archive()' now cascades to every remaining attendance
        row when a calendar itself is retired, but this search must not silently start trusting
        that invariant everywhere it's ever established - a calendar could in principle end up
        archived by some other path without its own attendance rows following (found 2026-09-01:
        before that cascade existed, a rolled-over teacher's ARCHIVED calendar kept showing
        active non-teaching rows here indefinitely, since a bare 'active=True' row search never
        looks at its own parent calendar's active state at all)."""
        return self.env['resource.calendar.attendance'].search([
            ('calendar_id.is_framework', '=', False),
            ('calendar_id.active', '=', True),
            ('dayofweek', 'in', WEEKDAYS),
        ])

    def _get_guard_duty_absence_intervals(self, day, employees):
        """`{employee.id: [(hour_from, hour_to, state)]}` - the absences covering `day`.

        Resolved on demand rather than stored anywhere: an absence is an 'hr.leave' keyed to a
        real date, the board is keyed to a weekday, and nothing joins the two until a date is
        actually asked for. Returns `{}` for no date at all, which is what lets the PDF (and any
        other weekday-only caller) keep working unchanged.

        sudo() because a guard-duty absence is not private to its own approval chain: whoever
        reads this board legitimately needs to know that a colleague is not coming, which is
        exactly the same justification 'get_guard_sessions()' carries for reading schedules that
        are not the reader's own. Only the fact and the interval are ever exposed - never the
        absence type, its reason, or its attachments.
        """
        if not day or not employees:
            return {}
        leaves = self.env['hr.leave'].sudo().search([
            ('employee_id', 'in', employees.ids),
            ('state', 'in', list(ABSENCE_STATES)),
            ('request_date_from', '<=', day),
            ('request_date_to', '>=', day),
        ])
        intervals = defaultdict(list)
        for leave in leaves:
            # 'request_unit_hours' rather than 'ems_full_day': it is the field that actually
            # decides whether request_hour_from/to carry anything (see hr.leave's own
            # _compute_request_unit_hours and EMS's override of it), and a multi-day request is
            # a whole day on each of its days regardless of how it was filled in.
            partial = leave.request_unit_hours and leave.request_date_from == leave.request_date_to
            hours = (leave.request_hour_from, leave.request_hour_to) if partial else WHOLE_DAY
            intervals[leave.employee_id.id].append((*hours, ABSENCE_STATES[leave.state]))
        return intervals

    @staticmethod
    def _guard_duty_absence_state(intervals, employees, hour_from, hour_to):
        """`{employee.id: 'approved'|'pending'}` for those of `employees` absent in the period.

        An approved absence outranks a pending one when the same teacher has both overlapping
        the same period: the period is going to need covering either way, so reporting it as
        merely "requested" would understate it.
        """
        states = {}
        for employee in employees:
            overlapping = {state for start, stop, state in intervals.get(employee.id, ())
                           if start < hour_to and stop > hour_from}
            if overlapping:
                states[employee.id] = 'approved' if 'approved' in overlapping else 'pending'
        return states

    def get_guard_duty_board_lines(self, weekday, shift, day=None):
        """Board rows for one weekday + shift: the ordered list of group columns actually taught in
        that slot, one row per distinct time period (chronological), each with one cell per group
        (teacher(s) + room, or empty) plus the guard-duty teacher(s) for that period. A guard row
        carries no group of its own (see 'non_teaching'), so it's reported separately from the
        group columns instead of as one more column. No per-subject colour is computed here (an
        earlier version reused ems.schedule_report_mixin's REPORT_COLOR_PALETTE the same way the
        teacher/group schedule PDFs do) - removed per developer feedback (2026-09-01): with every
        group already its own column and the subject spelled out as a short acronym in the cell,
        a colour-per-subject wash added visual noise without adding information a plain table
        didn't already convey.

        `day`, when given, is the concrete date the weekday stands for, and is what adds the
        absence information: every cell gains an 'absences' map of which of its own teachers are
        away, each row gains 'guard_absences' for the same question asked of the guard column,
        and 'absences' - the list of classes actually left without a teacher, which is what the
        board's second tab is built from. Without a date none of that can be resolved at all, so
        every one of those comes back empty and the board is the plain timetable it was before.
        """
        self.ensure_one()
        day = fields.Date.to_date(day)
        shift_start, shift_end = SHIFT_HOURS[shift]
        entries = self._get_guard_duty_board_attendance_ids().filtered(
            lambda attendance: attendance.dayofweek == weekday
                and attendance.hour_from >= shift_start and attendance.hour_to <= shift_end)
        teaching_entries = entries.filtered(lambda attendance: attendance.subject_id or attendance.group_ids)
        guard_entries = entries.filtered(lambda attendance: attendance.non_teaching_is_guard)

        groups = teaching_entries.group_ids.sorted(key=lambda group: group.name)
        periods = sorted({(attendance.hour_from, attendance.hour_to) for attendance in entries})
        intervals = self._get_guard_duty_absence_intervals(day, entries.employee_id)

        lines = []
        for hour_from, hour_to in periods:
            cells = []
            covering = []
            for group in groups:
                cell_entries = teaching_entries.filtered(
                    lambda attendance, group=group, hour_from=hour_from, hour_to=hour_to:
                        group in attendance.group_ids and attendance.hour_from == hour_from and attendance.hour_to == hour_to
                )
                # Every co-teacher for this cell, deduped (a plain recordset union already
                # does that) - a co-taught slot has one 'resource.calendar.attendance' row
                # per teacher, all sharing the same group/period, so 'entries' alone would
                # silently drop every name but the first one picked for display.
                cell_teachers = cell_entries.mapped('employee_id')
                cell_absences = self._guard_duty_absence_state(
                    intervals, cell_teachers, hour_from, hour_to)
                cells.append({
                    'group': group,
                    'entries': cell_entries,
                    'teachers': cell_teachers,
                    'absences': cell_absences,
                })
                # One row per absent teacher AND per class of theirs in this period: a teacher
                # splitting the period across two groups leaves two classes uncovered, and each
                # one has to be assigned its own guard.
                first = cell_entries[:1]
                covering += [{
                    'teacher': teacher,
                    'state': cell_absences[teacher.id],
                    'group': group,
                    'subject': first.subject_id,
                    'room': first.space_id,
                } for teacher in cell_teachers if teacher.id in cell_absences]
            guards = guard_entries.filtered(
                lambda attendance, hour_from=hour_from, hour_to=hour_to:
                    attendance.hour_from == hour_from and attendance.hour_to == hour_to)
            lines.append({
                'time_label': "%s-%s" % (self._format_report_time(hour_from), self._format_report_time(hour_to)),
                'cells': cells,
                'guards': guards,
                # Not folded into 'absences' below: an absent guard has no class of their own for
                # anyone to cover, they are simply one fewer person available to cover somebody
                # else's - a subtraction from the guard column, not an addition to the work.
                'guard_absences': self._guard_duty_absence_state(
                    intervals, guards.mapped('employee_id'), hour_from, hour_to),
                'absences': covering,
            })
        return {'groups': groups, 'lines': lines}

    @api.model
    def get_guard_duty_board_data(self, weekday, shift, day=None):
        """JSON-safe wrapper around get_guard_duty_board_lines(), for the guard duty board client
        action's own RPC call (static/src/js/backend/guard_duty_board.js). @api.model: resolves
        "the current course" itself (env.company.current_course_id), so the JS side never needs
        to know or pass a specific ems.course id — matches how the aggregation itself is scoped
        (see _get_guard_duty_board_attendance_ids' own NOTE: not actually course-filtered).

        `day` (an ISO date string from the screen's own date picker) is passed straight through -
        see get_guard_duty_board_lines(). Every teacher is reported as {'name', 'absence'} rather
        than a bare name, so both of the screen's tabs read absences the same way, off the same
        payload, instead of the client having to match names back against a separate list."""
        course = self.env.company.get_current_course_or_raise()
        data = course.get_guard_duty_board_lines(weekday, shift, day=day)
        groups = [{'id': group.id, 'name': group.name} for group in data['groups']]
        lines = []
        for line in data['lines']:
            cells = []
            for cell in line['cells']:
                first = cell['entries'][:1]
                # 'acronym' (e.g. "MP 0440"), not 'display_name' (which also spells out the full
                # subject name) - the cell is tight on space, the full name is one click away on
                # the teacher's own schedule.
                cells.append({
                    'group_id': cell['group'].id,
                    'subject': first.subject_id.acronym if first else False,
                    'teachers': self._guard_duty_teacher_data(cell['teachers'], cell['absences']),
                    'room': first.space_id.display_name if first and first.space_id else False,
                })
            lines.append({
                'time_label': line['time_label'],
                'cells': cells,
                'guards': self._guard_duty_teacher_data(
                    line['guards'].mapped('employee_id'), line['guard_absences']),
                'absences': [{
                    'teacher': row['teacher'].display_name,
                    'state': row['state'],
                    'group': row['group'].name,
                    'subject': row['subject'].acronym if row['subject'] else False,
                    'room': row['room'].display_name if row['room'] else False,
                } for row in line['absences']],
            })
        return {'groups': groups, 'lines': lines}

    @staticmethod
    def _guard_duty_teacher_data(teachers, absences):
        """Teachers as `[{'name', 'absence'}]` - 'absence' being False, 'approved' or 'pending'."""
        return [{'name': teacher.display_name, 'absence': absences.get(teacher.id, False)}
                for teacher in teachers]

    @api.model
    def get_current_course_data(self):
        """Small helper for the guard duty board's client action: the page has no bound record of
        its own to read 'the current course' from (see the class docstring above for why), so it
        asks for it explicitly instead — used both to label the page and to supply the PDF
        button's own 'active_ids'."""
        course = self.env.company.get_current_course_or_raise()
        return {'id': course.id, 'name': course.name}
