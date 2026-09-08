import json
from datetime import date, timedelta

from odoo.tests.common import TransactionCase

from .common import create_level_study, mock_outgoing_email


class TestGuardDutyBoard(TransactionCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        # Approving an absence posts to the chatter and notifies its followers - see
        # CLAUDE.md's 'Email safety in tests'.
        mock_outgoing_email(cls)
        cls.teacher_user = cls.env['res.users'].with_context(no_reset_password=True).create({
            'name': 'Test Teacher User (Guard Duty Board)',
            'login': 'test_teacher_for_guard_duty_board',
            'groups_id': [(4, cls.env.ref('base.group_user').id), (4, cls.env.ref('ems.group_teacher').id)],
        })
        # get_guard_duty_board_lines() is deliberately not course-scoped (see
        # models/attendance/guard_duty_board.py's own NOTE) - any ems.course record works to call
        # it on, this one is only ever used as that call target, never filtered against. Reusing
        # the dev DB's own current course avoids colliding with it on the unique_course_name
        # constraint (a freshly create()'d course defaults its start/end to this real year too).
        cls.course = cls.env.company.current_course_id
        if not cls.course:
            cls.course = cls.env['ems.course'].create({'start': 1999, 'end': 2000})
        # get_guard_duty_board_data()/get_current_course_data() read env.company.current_course_id
        # directly rather than taking a course argument (see guard_duty_board.py's own docstrings) -
        # a fresh DB (CI, unlike this box's own dev DB) has no "current course" configured at all,
        # so this must be set explicitly rather than assumed, matching every other test that needs
        # one (test_course_transition.py, test_year_record.py, test_em_grading_wizard.py...).
        cls.env.company.current_course_id = cls.course
        cls.level, cls.study = create_level_study(cls, 'TGDB', level={'name': 'Test Level (Guard Duty Board)'}, study={
            'code': 'TGDB001', 'name': 'Test Study (Guard Duty Board)', 'date': date.today(),
        })
        cls.subject = cls.env['ems.subject'].create({
            'code': 'TGDB001',
            'acronym': 'TGDB',
            'name': 'Test Subject (Guard Duty Board)',
            'study_ids': [(6, 0, [cls.study.id])],
        })
        cls.space = cls.env['ems.space'].create({
            'code': 'TGDB-A',
            'name': 'Test Space (Guard Duty Board)',
            'space_type_id': cls.env.ref('ems.space_type_classroom').id,
            'work_location_id': cls.env.ref('ems.work_location_main').id,
        })
        cls.space_b = cls.env['ems.space'].create({
            'code': 'TGDB-B',
            'name': 'Test Space B (Guard Duty Board)',
            'space_type_id': cls.env.ref('ems.space_type_classroom').id,
            'work_location_id': cls.env.ref('ems.work_location_main').id,
        })
        cls.group_a = cls.env['ems.group'].create({
            'course': 1, 'acronym': 'TGDBA', 'level_id': cls.level.id, 'study_id': cls.study.id,
            'space_id': cls.space.id, 'shift': 'morning',
        })
        cls.group_b = cls.env['ems.group'].create({
            'course': 1, 'acronym': 'TGDBB', 'level_id': cls.level.id, 'study_id': cls.study.id,
            'space_id': cls.space_b.id, 'shift': 'morning',
        })
        cls.non_teaching_guard = cls.env.ref('ems.non_teaching_g')
        cls.non_teaching_break = cls.env.ref('ems.non_teaching_br')
        cls.teacher_a = cls.env['hr.employee'].create({'name': 'Test Teacher A (Guard Duty Board)', 'employee_type': 'teacher'})
        cls.teacher_b = cls.env['hr.employee'].create({'name': 'Test Teacher B (Guard Duty Board)', 'employee_type': 'teacher'})
        cls.teacher_guard = cls.env['hr.employee'].create({'name': 'Test Teacher Guard (Guard Duty Board)', 'employee_type': 'teacher'})

    def _new_calendar(self, teacher, name):
        calendar = self.env['resource.calendar'].create({'name': name})
        teacher.resource_calendar_id = calendar
        return calendar

    def test_is_guard_seeded_on_guard_non_teaching_type(self):
        self.assertTrue(self.non_teaching_guard.is_guard)
        self.assertFalse(self.non_teaching_break.is_guard)

    def test_attendance_ids_aggregate_across_teachers(self):
        calendar_a = self._new_calendar(self.teacher_a, 'Test Calendar A (Aggregation)')
        calendar_a.apply_schedule_changes([{
            'dayofweek': '0', 'hour_from': 9, 'hour_to': 10, 'day_period': 'morning',
            'subject_id': self.subject.id, 'group_ids': [self.group_a.id], 'name': 'TGDBA: TGDB',
        }])
        calendar_b = self._new_calendar(self.teacher_b, 'Test Calendar B (Aggregation)')
        calendar_b.apply_schedule_changes([{
            'dayofweek': '0', 'hour_from': 9, 'hour_to': 10, 'day_period': 'morning',
            'subject_id': self.subject.id, 'group_ids': [self.group_b.id], 'name': 'TGDBB: TGDB',
        }])

        teaching = self.course._get_guard_duty_board_attendance_ids().filtered('subject_id')
        # Not assertEqual: this runs against the real dev DB, whose other real teachers/groups
        # also legitimately show up in this deliberately centre-wide (not course-scoped, see
        # models/attendance/guard_duty_board.py's own NOTE) aggregation - only assert OUR fixtures
        # are included, not that they're the only ones.
        self.assertLessEqual({self.teacher_a, self.teacher_b}, set(teaching.mapped('employee_id')))

    def test_attendance_ids_excludes_rows_on_an_archived_calendar(self):
        """Defense-in-depth (2026-09-01, see plans/course_transition_stale_teacher_assignments.md):
        a row can be active=True while its own parent calendar is archived - e.g. a leftover
        non-teaching commitment on a calendar that has since rolled over to a new one for a
        different course. Must never surface here regardless of the row's own active flag -
        deliberately reactivates the row AFTER archiving the calendar, so this test isolates
        the board's own filter from 'ems_working_schedule.action_archive()' 's cascade (covered
        separately in test_course_transition.py)."""
        calendar = self._new_calendar(self.teacher_guard, 'Test Calendar Archived (Aggregation)')
        guard_row = self.env['resource.calendar.attendance'].create({
            'calendar_id': calendar.id, 'name': 'Test Guard (Aggregation)',
            'dayofweek': '0', 'hour_from': 9, 'hour_to': 10, 'day_period': 'morning',
            'non_teaching': self.non_teaching_guard.id,
        })
        calendar.action_archive()
        guard_row.action_unarchive()

        rows = self.course._get_guard_duty_board_attendance_ids()

        self.assertNotIn(guard_row, rows)

    def test_get_guard_duty_board_lines_groups_are_columns(self):
        calendar_a = self._new_calendar(self.teacher_a, 'Test Calendar A (Columns)')
        calendar_a.apply_schedule_changes([{
            'dayofweek': '0', 'hour_from': 9, 'hour_to': 10, 'day_period': 'morning',
            'subject_id': self.subject.id, 'group_ids': [self.group_a.id], 'name': 'TGDBA: TGDB',
        }])
        calendar_b = self._new_calendar(self.teacher_b, 'Test Calendar B (Columns)')
        calendar_b.apply_schedule_changes([{
            'dayofweek': '0', 'hour_from': 9, 'hour_to': 10, 'day_period': 'morning',
            'subject_id': self.subject.id, 'group_ids': [self.group_b.id], 'name': 'TGDBB: TGDB',
        }])

        data = self.course.get_guard_duty_board_lines('0', 'morning')

        # Not assertEqual: real dev-DB groups with a Monday morning class legitimately show up
        # as columns too (see the NOTE in test_attendance_ids_aggregate_across_teachers).
        self.assertLessEqual({self.group_a.id, self.group_b.id}, set(data['groups'].mapped('id')))
        matching = [line for line in data['lines'] if line['time_label'] == '09:00-10:00']
        self.assertEqual(len(matching), 1)
        cell_by_group = {cell['group'].id: cell for cell in matching[0]['cells']}
        self.assertEqual(cell_by_group[self.group_a.id]['entries'].employee_id, self.teacher_a)
        self.assertEqual(cell_by_group[self.group_b.id]['entries'].employee_id, self.teacher_b)

    def test_get_guard_duty_board_lines_lists_guard_teachers_without_a_column(self):
        calendar_guard = self._new_calendar(self.teacher_guard, 'Test Calendar Guard (Guard List)')
        calendar_guard.apply_schedule_changes([{
            'dayofweek': '0', 'hour_from': 9, 'hour_to': 10, 'day_period': 'morning',
            'non_teaching': self.non_teaching_guard.id, 'name': 'Guard',
        }])

        data = self.course.get_guard_duty_board_lines('0', 'morning')

        matching = [line for line in data['lines'] if line['time_label'] == '09:00-10:00']
        self.assertEqual(len(matching), 1)
        self.assertIn(self.teacher_guard, matching[0]['guards'].mapped('employee_id'))
        # A guard-duty entry has no group of its own (see resource.calendar.attendance.group_ids'
        # own NOTE on non-teaching rows) - it must never show up in any group's cell either.
        cell_teachers = {teacher for cell in matching[0]['cells'] for teacher in cell['entries'].mapped('employee_id')}
        self.assertNotIn(self.teacher_guard, cell_teachers)

    def test_get_guard_duty_board_lines_respects_shift_window(self):
        calendar_a = self._new_calendar(self.teacher_a, 'Test Calendar A (Shift Window)')
        calendar_a.apply_schedule_changes([{
            'dayofweek': '0', 'hour_from': 16, 'hour_to': 17, 'day_period': 'afternoon',
            'subject_id': self.subject.id, 'group_ids': [self.group_a.id], 'name': 'TGDBA: TGDB (afternoon)',
        }])

        morning = self.course.get_guard_duty_board_lines('0', 'morning')
        afternoon = self.course.get_guard_duty_board_lines('0', 'afternoon')

        self.assertNotIn('16:00-17:00', {line['time_label'] for line in morning['lines']})
        self.assertIn('16:00-17:00', {line['time_label'] for line in afternoon['lines']})

    def test_get_guard_duty_board_lines_co_teaching_lists_every_teacher(self):
        """A co-taught cell (two teachers, same group, same period) must list BOTH names, not
        just whichever teacher's own resource.calendar.attendance row got filtered to first —
        each co-teacher has their own row for the shared class (see
        resource.calendar.attendance.employee_id's own NOTE), so naively picking cell['entries'][:1]
        would silently drop every co-teacher but one."""
        calendar_a = self._new_calendar(self.teacher_a, 'Test Calendar A (Co-teaching)')
        calendar_a.apply_schedule_changes([{
            'dayofweek': '0', 'hour_from': 9, 'hour_to': 10, 'day_period': 'morning',
            'subject_id': self.subject.id, 'group_ids': [self.group_a.id], 'name': 'TGDBA: TGDB',
        }])
        calendar_b = self._new_calendar(self.teacher_b, 'Test Calendar B (Co-teaching)')
        calendar_b.apply_schedule_changes([{
            'dayofweek': '0', 'hour_from': 9, 'hour_to': 10, 'day_period': 'morning',
            'subject_id': self.subject.id, 'group_ids': [self.group_a.id], 'name': 'TGDBA: TGDB',
        }])

        data = self.course.get_guard_duty_board_lines('0', 'morning')

        matching_line = next(line for line in data['lines'] if line['time_label'] == '09:00-10:00')
        cell = next(cell for cell in matching_line['cells'] if cell['group'].id == self.group_a.id)
        self.assertEqual(set(cell['teachers'].mapped('display_name')), {self.teacher_a.display_name, self.teacher_b.display_name})

    def test_get_guard_duty_board_data_is_json_safe_and_matches_current_course(self):
        """get_guard_duty_board_data() is @api.model and resolves 'the current course' itself
        (env.company.current_course_id) rather than taking a course argument - see
        models/attendance/guard_duty_board.py's own docstring for why. Also verifies the data is
        JSON-safe (no stray recordsets), and that the short 'acronym' (not the full subject
        title) and every co-teacher's name are used, matching the compact cell layout."""
        current_course = self.env.company.current_course_id
        self.assertTrue(current_course, "This dev DB must have a current course configured for this test to be meaningful.")

        calendar_a = self._new_calendar(self.teacher_a, 'Test Calendar A (JSON)')
        calendar_a.apply_schedule_changes([{
            'dayofweek': '0', 'hour_from': 9, 'hour_to': 10, 'day_period': 'morning',
            'subject_id': self.subject.id, 'group_ids': [self.group_a.id], 'name': 'TGDBA: TGDB',
        }])
        calendar_guard = self._new_calendar(self.teacher_guard, 'Test Calendar Guard (JSON)')
        calendar_guard.apply_schedule_changes([{
            'dayofweek': '0', 'hour_from': 9, 'hour_to': 10, 'day_period': 'morning',
            'non_teaching': self.non_teaching_guard.id, 'name': 'Guard',
        }])

        data = self.env['ems.course'].get_guard_duty_board_data('0', 'morning')
        json.dumps(data)  # raises TypeError if anything isn't JSON-safe (e.g. a stray recordset)

        matching_group = next(group for group in data['groups'] if group['id'] == self.group_a.id)
        self.assertIsInstance(matching_group['name'], str)
        matching_line = next(line for line in data['lines'] if line['time_label'] == '09:00-10:00')
        # Every teacher is reported as {'name', 'absence'}, never a bare name - see
        # _guard_duty_teacher_data(). With no date asked for, nobody can be absent.
        self.assertIn(self.teacher_guard.display_name,
                      [guard['name'] for guard in matching_line['guards']])
        cell = next(cell for cell in matching_line['cells'] if cell['group_id'] == self.group_a.id)
        self.assertEqual(cell['teachers'], [{'name': self.teacher_a.display_name, 'absence': False}])
        self.assertEqual(cell['subject'], self.subject.acronym)

    def test_get_current_course_data(self):
        current_course = self.env.company.current_course_id
        data = self.env['ems.course'].get_current_course_data()
        self.assertEqual(data, {'id': current_course.id, 'name': current_course.name})

    def test_teacher_can_call_board_methods(self):
        """A plain group_teacher user must be able to call every board method without an
        AccessError - colleagues' schedules aren't secret (see the developer's own feedback that
        drove this feature), and base Odoo's own ACL already grants every internal user read
        access to resource.calendar/resource.calendar.attendance; ems.course itself already
        grants group_teacher read access too (ems.access_ems_course_teacher in
        security/ir.model.access.csv) - no new ACL rows were needed for this feature at all."""
        calendar_a = self._new_calendar(self.teacher_a, 'Test Calendar A (Teacher Access)')
        calendar_a.apply_schedule_changes([{
            'dayofweek': '0', 'hour_from': 9, 'hour_to': 10, 'day_period': 'morning',
            'subject_id': self.subject.id, 'group_ids': [self.group_a.id], 'name': 'TGDBA: TGDB',
        }])

        course = self.course.with_user(self.teacher_user)
        data = course.get_guard_duty_board_lines('0', 'morning')
        self.assertTrue(data['lines'])
        json_data = self.env['ems.course'].with_user(self.teacher_user).get_guard_duty_board_data('0', 'morning')
        self.assertTrue(json_data['lines'])

    def test_report_guard_duty_board_renders(self):
        calendar_a = self._new_calendar(self.teacher_a, 'Test Calendar A (PDF)')
        calendar_a.apply_schedule_changes([{
            'dayofweek': '0', 'hour_from': 9, 'hour_to': 10, 'day_period': 'morning',
            'subject_id': self.subject.id, 'group_ids': [self.group_a.id], 'name': 'TGDBA: TGDB',
        }])
        calendar_guard = self._new_calendar(self.teacher_guard, 'Test Calendar Guard (PDF)')
        calendar_guard.apply_schedule_changes([{
            'dayofweek': '0', 'hour_from': 9, 'hour_to': 10, 'day_period': 'morning',
            'non_teaching': self.non_teaching_guard.id, 'name': 'Guard',
        }])

        content, content_type = self.env['ir.actions.report']._render_qweb_pdf('ems.report_guard_duty_board', [self.course.id])

        self.assertTrue(content)
        self.assertIn(content_type, ('pdf', 'html'))
        self.assertIn(self.teacher_a.name.encode(), content)
        self.assertIn(self.teacher_guard.name.encode(), content)

    def test_report_guard_duty_board_scopes_to_one_day_via_context(self):
        """The "Download PDF" button (guard_duty_board.js) always passes a 'guard_duty_weekday'
        context key so the PDF only ever covers the day the user was looking at, not the whole
        week - confirmed here two ways: the requested day's teacher IS in the output, and a
        DIFFERENT day's teacher (created on Tuesday, while the PDF is requested for Monday) is
        NOT - proving the report doesn't fall back to rendering every weekday regardless."""
        calendar_monday = self._new_calendar(self.teacher_a, 'Test Calendar A (PDF Monday)')
        calendar_monday.apply_schedule_changes([{
            'dayofweek': '0', 'hour_from': 9, 'hour_to': 10, 'day_period': 'morning',
            'subject_id': self.subject.id, 'group_ids': [self.group_a.id], 'name': 'TGDBA: TGDB (Monday)',
        }])
        calendar_tuesday = self._new_calendar(self.teacher_b, 'Test Calendar B (PDF Tuesday)')
        calendar_tuesday.apply_schedule_changes([{
            'dayofweek': '1', 'hour_from': 9, 'hour_to': 10, 'day_period': 'morning',
            'subject_id': self.subject.id, 'group_ids': [self.group_a.id], 'name': 'TGDBA: TGDB (Tuesday)',
        }])

        content, _content_type = self.env['ir.actions.report'].with_context(
            guard_duty_weekday='0').\
            _render_qweb_pdf('ems.report_guard_duty_board', [self.course.id])

        self.assertIn(self.teacher_a.name.encode(), content)
        self.assertNotIn(self.teacher_b.name.encode(), content)

    def test_report_guard_duty_board_scopes_to_one_shift_via_context(self):
        """Same as the weekday-scoping test above, but for 'guard_duty_shift': the PDF button
        also passes whichever shift the dropdown had selected, so printing while looking at
        Morning must not also render the Afternoon table (and vice versa)."""
        calendar_morning = self._new_calendar(self.teacher_a, 'Test Calendar A (PDF Morning)')
        calendar_morning.apply_schedule_changes([{
            'dayofweek': '0', 'hour_from': 9, 'hour_to': 10, 'day_period': 'morning',
            'subject_id': self.subject.id, 'group_ids': [self.group_a.id], 'name': 'TGDBA: TGDB (morning)',
        }])
        calendar_afternoon = self._new_calendar(self.teacher_b, 'Test Calendar B (PDF Afternoon)')
        calendar_afternoon.apply_schedule_changes([{
            'dayofweek': '0', 'hour_from': 16, 'hour_to': 17, 'day_period': 'afternoon',
            'subject_id': self.subject.id, 'group_ids': [self.group_a.id], 'name': 'TGDBA: TGDB (afternoon)',
        }])

        content, _content_type = self.env['ir.actions.report'].with_context(
            guard_duty_weekday='0', guard_duty_shift='morning').\
            _render_qweb_pdf('ems.report_guard_duty_board', [self.course.id])

        self.assertIn(self.teacher_a.name.encode(), content)
        self.assertNotIn(self.teacher_b.name.encode(), content)
        self.assertNotIn(b'Afternoon', content)

    # --- Absences on the board --------------------------------------------------------------
    #
    # The board is keyed by weekday, absences by real date, so every one of these has to hand
    # 'get_guard_duty_board_lines' a concrete Monday for the two to meet - see the 'day'
    # argument's own docstring in models/attendance/guard_duty_board.py.

    def _monday(self):
        """A Monday inside the current course's window, matching the '0' weekday these fixtures
        use. Inside the window because the absence form's own health-allowance computation
        filters on it (see hr.leave._compute_ems_health_allowance)."""
        window = self.env.company.current_course_id.date_range()
        day = window[0] + timedelta(days=30)
        while day.weekday() != 0:
            day += timedelta(days=1)
        return day

    def _absence(self, employee, day, hour_from=None, hour_to=None, approve=True):
        vals = {
            'employee_id': employee.id,
            'holiday_status_id': self.env.ref('ems.leave_type_justified').id,
            'request_date_from': day,
            'request_date_to': day,
            # What the "Send request" button does - a request that was never sent cannot be
            # saved at all (see hr.leave._check_ems_submitted).
            'ems_submitted': True,
            'ems_responsible_declaration': True,
        }
        if hour_from is None:
            # 'leave_type_justified' does not seed 'Whole day?' on its own (its
            # ems_full_day_default is False), and a request that is neither a whole day nor a
            # span of hours is worth zero - which hr_holidays itself refuses to approve.
            vals['ems_full_day'] = True
        else:
            vals.update({'ems_full_day': False,
                         'request_hour_from': hour_from, 'request_hour_to': hour_to})
        leave = self.env['hr.leave'].create(vals)
        if approve:
            leave.action_approve()
        return leave

    def _teaching_line(self, day, hour_from=9, hour_to=10):
        """The board row for one period of `day`'s weekday, morning shift."""
        data = self.course.get_guard_duty_board_lines(str(day.weekday()), 'morning', day=day)
        label = '%02d:00-%02d:00' % (hour_from, hour_to)
        return next(line for line in data['lines'] if line['time_label'] == label)

    def _schedule_class(self, teacher, group, name, periods=((9, 10),), dayofweek='0'):
        """One calendar for `teacher` holding exactly `periods` as lessons of `group`.

        Every period in one call: apply_schedule_changes() replaces the calendar's whole Mon-Fri
        week each time it runs (it is fed the schedule grid's full buffer, see its own
        docstring), so calling it twice would leave only the second period behind.
        """
        calendar = self._new_calendar(teacher, name)
        calendar.apply_schedule_changes([{
            'dayofweek': dayofweek, 'hour_from': hour_from, 'hour_to': hour_to,
            'day_period': 'morning', 'subject_id': self.subject.id,
            'group_ids': [group.id], 'name': f'{group.acronym}: TGDB',
        } for hour_from, hour_to in periods])
        return calendar

    def test_without_a_date_no_absence_is_resolved_at_all(self):
        """The PDF still calls this with no date (see reports/attendance/report_guard_duty_board.xml),
        and a weekday on its own can never say who is absent - the board has to keep working,
        marking nobody, rather than guessing a date of its own."""
        monday = self._monday()
        self._schedule_class(self.teacher_a, self.group_a, 'Test Calendar A (No Date)')
        self._absence(self.teacher_a, monday)

        data = self.course.get_guard_duty_board_lines('0', 'morning')

        line = next(line for line in data['lines'] if line['time_label'] == '09:00-10:00')
        cell = next(cell for cell in line['cells'] if cell['group'].id == self.group_a.id)
        self.assertEqual(cell['absences'], {})
        self.assertEqual(line['absences'], [])

    def test_an_approved_whole_day_absence_marks_the_teacher_in_their_own_cell(self):
        monday = self._monday()
        self._schedule_class(self.teacher_a, self.group_a, 'Test Calendar A (Whole Day)')
        self._absence(self.teacher_a, monday)

        line = self._teaching_line(monday)

        cell = next(cell for cell in line['cells'] if cell['group'].id == self.group_a.id)
        self.assertEqual(cell['absences'], {self.teacher_a.id: 'approved'})

    def test_a_partial_absence_only_marks_the_periods_it_overlaps(self):
        """Arriving an hour late leaves the rest of the morning covered."""
        monday = self._monday()
        self._schedule_class(self.teacher_a, self.group_a, 'Test Calendar A (Partial)',
                             periods=((9, 10), (11, 12)))
        self._absence(self.teacher_a, monday, hour_from=8.5, hour_to=10.5)

        missed = self._teaching_line(monday, 9, 10)
        covered = self._teaching_line(monday, 11, 12)

        missed_cell = next(cell for cell in missed['cells'] if cell['group'].id == self.group_a.id)
        covered_cell = next(cell for cell in covered['cells'] if cell['group'].id == self.group_a.id)
        self.assertEqual(missed_cell['absences'], {self.teacher_a.id: 'approved'})
        self.assertEqual(covered_cell['absences'], {})

    def test_a_request_still_pending_is_marked_apart_from_an_approved_one(self):
        """Whoever plans the guards wants to see what is coming, but must not confuse a request
        nobody has decided on yet with an absence that is going to happen."""
        monday = self._monday()
        self._schedule_class(self.teacher_a, self.group_a, 'Test Calendar A (Pending)')
        leave = self._absence(self.teacher_a, monday, approve=False)

        self.assertEqual(leave.state, 'confirm')
        line = self._teaching_line(monday)

        cell = next(cell for cell in line['cells'] if cell['group'].id == self.group_a.id)
        self.assertEqual(cell['absences'], {self.teacher_a.id: 'pending'})

    def test_a_refused_request_marks_nobody(self):
        monday = self._monday()
        self._schedule_class(self.teacher_a, self.group_a, 'Test Calendar A (Refused)')
        leave = self._absence(self.teacher_a, monday, approve=False)
        leave.action_refuse()

        line = self._teaching_line(monday)

        cell = next(cell for cell in line['cells'] if cell['group'].id == self.group_a.id)
        self.assertEqual(cell['absences'], {})

    def test_an_absent_guard_teacher_is_marked_in_the_guard_column(self):
        """The one who was going to cover for somebody else is the one missing - the column has
        to say so, or the period looks staffed when it is not."""
        monday = self._monday()
        calendar = self._new_calendar(self.teacher_guard, 'Test Calendar Guard (Absent)')
        calendar.apply_schedule_changes([{
            'dayofweek': '0', 'hour_from': 9, 'hour_to': 10, 'day_period': 'morning',
            'non_teaching': self.non_teaching_guard.id, 'name': 'Guard',
        }])
        self._absence(self.teacher_guard, monday)

        line = self._teaching_line(monday)

        self.assertEqual(line['guard_absences'].get(self.teacher_guard.id), 'approved')

    def test_the_absence_rows_carry_the_class_that_needs_covering(self):
        """The second tab's whole point: not just who is missing, but what has to be covered -
        group, subject and room, so a guard can be sent without opening another screen."""
        monday = self._monday()
        self._schedule_class(self.teacher_a, self.group_a, 'Test Calendar A (Rows)')
        self._absence(self.teacher_a, monday)

        line = self._teaching_line(monday)

        row = next(row for row in line['absences'] if row['teacher'] == self.teacher_a)
        self.assertEqual(row['state'], 'approved')
        self.assertEqual(row['group'], self.group_a)
        self.assertEqual(row['subject'], self.subject)
        self.assertEqual(row['room'], self.space)

    def test_a_guard_teacher_absence_produces_no_row_to_cover(self):
        """An absent guard has nothing for anyone to cover - they are missing from the guard
        column (tested above), not a class left without a teacher."""
        monday = self._monday()
        calendar = self._new_calendar(self.teacher_guard, 'Test Calendar Guard (No Row)')
        calendar.apply_schedule_changes([{
            'dayofweek': '0', 'hour_from': 9, 'hour_to': 10, 'day_period': 'morning',
            'non_teaching': self.non_teaching_guard.id, 'name': 'Guard',
        }])
        self._absence(self.teacher_guard, monday)

        line = self._teaching_line(monday)

        self.assertNotIn(self.teacher_guard, [row['teacher'] for row in line['absences']])

    def test_get_guard_duty_board_data_is_json_safe_with_absences(self):
        monday = self._monday()
        self._schedule_class(self.teacher_a, self.group_a, 'Test Calendar A (JSON Absences)')
        calendar_guard = self._new_calendar(self.teacher_guard, 'Test Calendar Guard (JSON Absences)')
        calendar_guard.apply_schedule_changes([{
            'dayofweek': '0', 'hour_from': 9, 'hour_to': 10, 'day_period': 'morning',
            'non_teaching': self.non_teaching_guard.id, 'name': 'Guard',
        }])
        self._absence(self.teacher_a, monday)

        data = self.env['ems.course'].get_guard_duty_board_data(
            str(monday.weekday()), 'morning', day=str(monday))
        json.dumps(data)  # raises TypeError if anything isn't JSON-safe (e.g. a stray recordset)

        line = next(line for line in data['lines'] if line['time_label'] == '09:00-10:00')
        cell = next(cell for cell in line['cells'] if cell['group_id'] == self.group_a.id)
        absent = next(teacher for teacher in cell['teachers']
                      if teacher['name'] == self.teacher_a.display_name)
        self.assertEqual(absent['absence'], 'approved')
        guard = next(guard for guard in line['guards']
                     if guard['name'] == self.teacher_guard.display_name)
        self.assertFalse(guard['absence'])
        row = next(row for row in line['absences']
                   if row['teacher'] == self.teacher_a.display_name)
        self.assertEqual(row['group'], self.group_a.name)
        self.assertEqual(row['subject'], self.subject.acronym)
        self.assertEqual(row['room'], self.space.display_name)
