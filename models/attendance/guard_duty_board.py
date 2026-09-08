# -*- coding: utf-8 -*-

from odoo import api, models

from ..shared.schedule_report_mixin import HOUR_EPSILON

WEEKDAYS = ('0', '1', '2', '3', '4')
# Mirrors ems.group's own SHIFT_HOURS (models/contacts/group_schedule.py) — the guard duty board
# needs the same morning/afternoon split, but rendered as weekday x shift tables with one column
# per group rather than one column per weekday, so it can't reuse that method as-is.
SHIFT_HOURS = {
    'morning': (8, 15),
    'afternoon': (15, 22),
}


def _period_contains(container, period):
    """True when 'period' (hour_from, hour_to) is fully covered by 'container' - same
    containment check '_merge_absorbed_periods' below needs inline, extracted so the level
    filter's guard/break folding (issue #390) can reuse it against a period that isn't
    necessarily a member of the same 'periods' list (see 'get_guard_duty_board_lines' docstring).
    Uses HOUR_EPSILON for the same float-noise reason as '_merge_absorbed_periods'."""
    return container[0] <= period[0] + HOUR_EPSILON and container[1] >= period[1] - HOUR_EPSILON


def _merge_absorbed_periods(periods):
    """Groups 'periods' (a list of distinct (hour_from, hour_to) tuples) into
    {period: [period, *periods absorbed into it]}, one entry per period that keeps its own row -
    an absorbed period is never a key of the returned dict.

    A period is absorbed into another one from the same list when its own hour range is fully
    contained in the other's (found 2026-09 as issue #410: a teacher's own personal schedule can
    end a guard-duty slot early - e.g. a shorter working day that block - while a colleague's
    guard for the same start time runs the full period; the same thing happens for any other
    non-teaching activity, like a 35-minute coordination duty sitting next to a 60-minute class.
    Before this, get_guard_duty_board_lines() rendered the short period as its own row, almost or
    entirely empty). If several periods could contain a given one, the smallest (shortest) is
    preferred, to avoid folding into an unnecessarily wide row should several levels of
    containment ever coexist.

    Uses HOUR_EPSILON (see its own NOTE) since two periods that are conceptually "the same" can
    still differ by a hair's-width float remainder depending on how each was computed."""
    containers = {}
    for period in periods:
        candidates = [
            other for other in periods
            if other != period and _period_contains(other, period)
        ]
        if candidates:
            containers[period] = min(candidates, key=lambda other: other[1] - other[0])

    def root(period):
        # 'seen' guards against a cycle between two periods that both fall within HOUR_EPSILON of
        # each other in both bounds (so each looks like a - vanishingly narrow - "container" of
        # the other) - not a real containment relation, just float noise; without this a cycle
        # would loop root() forever instead of just resolving to whichever period was reached
        # first.
        seen = set()
        while period in containers and period not in seen:
            seen.add(period)
            period = containers[period]
        return period

    members = {}
    for period in periods:
        members.setdefault(root(period), []).append(period)
    return members


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
        looks at its own parent calendar's active state at all).

        'calendar_id.employee_id != False' excludes any calendar that isn't a specific teacher's
        own personal working schedule - concretely, Odoo's own generic default calendar (e.g.
        "Standard 40 hours/week", auto-created with its own Mon-Fri 8-12/13-17 attendance rows
        the first time anything needs 'res.company.resource_calendar_id' and nothing has been
        customized yet). That calendar is never itself is_framework=True, so the check above
        alone doesn't exclude it, and on a clean install with no real schedules configured yet
        it silently shows up here and corrupts period computation (found 2026-09-08 via CI: the
        generic 8-12 block contains/absorbs a real, narrower test period into itself)."""
        return self.env['resource.calendar.attendance'].search([
            ('calendar_id.is_framework', '=', False),
            ('calendar_id.active', '=', True),
            ('calendar_id.employee_id', '!=', False),
            ('dayofweek', 'in', WEEKDAYS),
        ])

    def get_guard_duty_board_lines(self, weekday, shift, level_ids=None):
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

        A period whose hour range is fully absorbed by another period starting at the same time
        (or earlier) never gets a row of its own - see _merge_absorbed_periods() - its cells/
        guards are folded into the row of the period that contains it instead (issue #410).

        A period left with no teaching cell AND no guard after that merge (e.g. a coordination
        duty/meeting nobody's actual class or guard shift overlaps) is dropped entirely - a row
        with nothing in it but a time range adds no information (developer follow-up on #410,
        2026-09-07).

        'level_ids' (issue #390, falsy/omitted = "All levels", the previous, still-default
        behaviour): a list of 'ems.level' ids to narrow the board down to. See "Level filter" in
        docs/en/developers/attendance/guard_duty_board.md for the full design. When set:
        - 'teaching_entries'/'groups'/'periods' only ever come from a group whose own 'level_id'
          (see ems.group's own field) is in 'level_ids' - a "reinforcement" group (no level_id by
          design) can never match. This is the only thing the filter actually controls: which
          time blocks (rows) exist at all.
        - A guard is shown on whichever ROW its own period overlaps, full stop - there is no way
          to know, and no need to know, which level a guard-duty teacher "belongs" to (developer
          feedback, 2026-09-07, after an earlier version tried deriving it from the teacher's own
          other classes that day and got it backwards for a guard who simply doesn't teach
          anything that day - see [[project_guard_duty_board_level_filter]] in memory): once a
          time block is visible for this level (because some class of it runs then), every guard
          on duty then is relevant, regardless of what they otherwise teach.
        - A guard whose own period isn't covered by any of the rows above still gets a shot at a
          dedicated "Patio" row if it falls inside that level's own break period - see
          _get_guard_duty_board_break_lines(). One left over after that simply has no visible
          block to attach to under this level and isn't shown (still visible under "All levels").

        Checking every existing level in the client's own filter dropdown is normalized to the
        same "All levels" (falsy) path below, not treated as a real filter: even with the guard
        rule above, a level-filtered view only ever builds rows from teaching entries (never from
        a guard-only or "reinforcement"-group period the way the unfiltered path's own 'entries'-
        wide 'periods' does) - checking literally every level is meant to mean "show everything",
        indistinguishable from checking none at all."""
        self.ensure_one()
        if level_ids and set(level_ids) >= set(self.env['ems.level'].search([]).ids):
            level_ids = None
        shift_start, shift_end = SHIFT_HOURS[shift]
        entries = self._get_guard_duty_board_attendance_ids().filtered(
            lambda attendance: attendance.dayofweek == weekday
                and attendance.hour_from >= shift_start and attendance.hour_to <= shift_end)
        teaching_entries = entries.filtered(lambda attendance: attendance.subject_id or attendance.group_ids)
        guard_entries = entries.filtered(lambda attendance: attendance.non_teaching_is_guard)

        if level_ids:
            teaching_entries = teaching_entries.filtered(
                lambda attendance: attendance.group_ids.filtered(lambda group: group.level_id.id in level_ids))
            groups = teaching_entries.group_ids.filtered(lambda group: group.level_id.id in level_ids).sorted(key=lambda group: group.name)
            periods = sorted({(attendance.hour_from, attendance.hour_to) for attendance in teaching_entries})
        else:
            groups = teaching_entries.group_ids.sorted(key=lambda group: group.name)
            periods = sorted({(attendance.hour_from, attendance.hour_to) for attendance in entries})
        period_members = _merge_absorbed_periods(periods)

        dated_lines = []
        remaining_guards = guard_entries
        for hour_from, hour_to in periods:
            if (hour_from, hour_to) not in period_members:
                continue  # absorbed - already folded into its container's row below
            member_periods = period_members[(hour_from, hour_to)]
            cells = []
            for group in groups:
                cell_entries = teaching_entries.filtered(
                    lambda attendance, group=group, member_periods=member_periods:
                        group in attendance.group_ids and (attendance.hour_from, attendance.hour_to) in member_periods
                )
                cells.append({
                    'group': group,
                    'entries': cell_entries,
                    # Every co-teacher for this cell, deduped (a plain recordset union already
                    # does that) - a co-taught slot has one 'resource.calendar.attendance' row
                    # per teacher, all sharing the same group/period, so 'entries' alone would
                    # silently drop every name but the first one picked for display.
                    'teachers': cell_entries.mapped('employee_id'),
                })
            if level_ids:
                # A guard's own period is no longer necessarily one of 'periods' above (those now
                # only come from teaching_entries) - fold it into whichever row's range genuinely
                # contains it, not just an exact-tuple match.
                guards = remaining_guards.filtered(
                    lambda attendance, hour_from=hour_from, hour_to=hour_to:
                        _period_contains((hour_from, hour_to), (attendance.hour_from, attendance.hour_to)))
            else:
                guards = guard_entries.filtered(
                    lambda attendance, member_periods=member_periods:
                        (attendance.hour_from, attendance.hour_to) in member_periods)
            remaining_guards -= guards
            if not guards and not any(cell['entries'] for cell in cells):
                continue  # nothing scheduled anywhere in this period - no row worth showing
            dated_lines.append((hour_from, hour_to, {
                'time_label': "%s-%s" % (self._format_report_time(hour_from), self._format_report_time(hour_to)),
                'cells': cells,
                'guards': guards,
            }))

        if level_ids:
            dated_lines += self._get_guard_duty_board_break_lines(
                level_ids, weekday, shift_start, shift_end, groups, remaining_guards)
            dated_lines.sort(key=lambda dated_line: (dated_line[0], dated_line[1]))
        return {'groups': groups, 'lines': [line for _hour_from, _hour_to, line in dated_lines]}

    def _get_guard_duty_board_break_lines(self, level_ids, weekday, shift_start, shift_end, groups, unmatched_guards):
        """Once a level filter is active, that level's own break ("Patio") period has no real
        teaching entry of its own to build a row from (a teacher's own calendar spans one
        continuous block across it - see hr.employee._get_derived_break_entries' own docstring),
        so a guard duty scheduled specifically for a break would otherwise simply disappear once
        'get_guard_duty_board_lines' restricts its rows to the filtered level's teaching periods
        only. Any leftover 'unmatched_guards' entry (any guard not already folded into a row
        above - see the caller, which no longer derives a guard's own level at all) that falls
        inside one of that level's own framework(s)' break periods gets a dedicated row instead -
        marked 'is_break' for the client to label distinctly. A
        break period with no guard inside it renders nothing, same "nothing to show" rule every
        other row already follows. Not meaningful under "All levels" - a break's own hours differ
        per level (see docs/en/developers/attendance/guard_duty_board.md's own "Level filter"
        section), so the caller only ever invokes this once a level filter narrows down which
        break(s) apply."""
        frameworks = self.env['resource.calendar'].search([
            ('is_framework', '=', True), ('level_id', 'in', level_ids),
        ])
        if not frameworks:
            return []
        break_periods = sorted({
            (attendance.hour_from, attendance.hour_to)
            for attendance in self.env['resource.calendar.attendance'].search([
                ('calendar_id', 'in', frameworks.ids),
                ('dayofweek', '=', weekday),
                ('non_teaching_is_break', '=', True),
                ('hour_from', '>=', shift_start), ('hour_to', '<=', shift_end),
            ])
        })
        empty_entries = self.env['resource.calendar.attendance']
        dated_lines = []
        for hour_from, hour_to in break_periods:
            guards = unmatched_guards.filtered(
                lambda attendance, hour_from=hour_from, hour_to=hour_to:
                    _period_contains((hour_from, hour_to), (attendance.hour_from, attendance.hour_to)))
            if not guards:
                continue  # nothing to show for this break slot
            unmatched_guards -= guards
            dated_lines.append((hour_from, hour_to, {
                'time_label': "%s-%s" % (self._format_report_time(hour_from), self._format_report_time(hour_to)),
                'cells': [{'group': group, 'entries': empty_entries, 'teachers': empty_entries.employee_id} for group in groups],
                'guards': guards,
                'is_break': True,
            }))
        return dated_lines

    @api.model
    def get_guard_duty_board_data(self, weekday, shift, level_ids=None):
        """JSON-safe wrapper around get_guard_duty_board_lines(), for the guard duty board client
        action's own RPC call (static/src/js/backend/guard_duty_board.js). @api.model: resolves
        "the current course" itself (env.company.current_course_id), so the JS side never needs
        to know or pass a specific ems.course id — matches how the aggregation itself is scoped
        (see _get_guard_duty_board_attendance_ids' own NOTE: not actually course-filtered).
        'level_ids' (issue #390) is forwarded as-is - see get_guard_duty_board_lines()'s own
        docstring."""
        course = self.env.company.get_current_course_or_raise()
        data = course.get_guard_duty_board_lines(weekday, shift, level_ids=level_ids)
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
                    'teachers': cell['teachers'].mapped('display_name'),
                    'room': first.space_id.display_name if first and first.space_id else False,
                })
            lines.append({
                'time_label': line['time_label'],
                'cells': cells,
                'guards': line['guards'].mapped('employee_id.display_name'),
                'is_break': line.get('is_break', False),
            })
        return {'groups': groups, 'lines': lines}

    @api.model
    def get_guard_duty_board_levels(self):
        """Every 'ems.level', for the guard duty board's own level filter (issue #390) - plain
        id/name pairs, JSON-safe like get_guard_duty_board_data(). No course scoping: a level is
        centre-wide curriculum data, not tied to any one ems.course."""
        return [{'id': level.id, 'name': level.name} for level in self.env['ems.level'].search([])]

    @api.model
    def get_current_course_data(self):
        """Small helper for the guard duty board's client action: the page has no bound record of
        its own to read 'the current course' from (see the class docstring above for why), so it
        asks for it explicitly instead — used both to label the page and to supply the PDF
        button's own 'active_ids'."""
        course = self.env.company.get_current_course_or_raise()
        return {'id': course.id, 'name': course.name}
