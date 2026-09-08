# -*- coding: utf-8 -*-

from datetime import date

from odoo.exceptions import AccessError
from odoo.tests.common import TransactionCase

from .common import create_level_study_group, create_student_academic_file, mock_outgoing_email

# Every model the guidance (Orientació) and coexistence posts must be able to read
# centre-wide - see docs/en/developers/employees/role_hierarchy.md, "Transversal read-only
# access to student data" (issue #393).
STUDENT_DATA_MODELS = (
    'res.partner',
    'ems.enrollment',
    'ems.authorization',
    'ems.grade_session',
    'ems.grade_subject_line',
    'ems.grade_outcome_line',
    'ems.student.year_record',
    'ems.student.year_record.subject',
    'ems.student.year_record.outcome',
    'ems.attendance_session_header',
    'ems.attendance_session_line',
    'ems.attendance_justification',
    'ems.attendance_issue_tutor',
    'ems.attendance_issue_student',
    'ems.attendance_issue_status',
    'ems.strike',
    'ems.strike.reason',
    # An EMS enrolment IS a sale.order, and the Secretary tab's authorizations hang off it -
    # see rule_sale_order_student_data_reader for why read access here is not optional.
    'sale.order',
    'sale.order.line',
)

# Deliberately out of scope: neither post has a reason to see invoices or payments. sale.order
# itself is NOT here - it is the enrolment record, not an accounting document (see above).
FINANCIAL_MODELS = ('account.move', 'account.payment')

# The screens the data above actually renders in - a permission with no route to it is
# invisible, so the menus are part of the feature, not an afterthought.
STUDENT_DATA_MENU_XMLIDS = (
    'ems.menu_ems_academic_management',
    'ems.menu_students_tutor',
    'ems.menu_grade_sessions',
    'ems.menu_year_record',
)


class TestStudentDataReader(TransactionCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        # ems.strike sends a real email synchronously on create() - see CLAUDE.md's
        # "Email safety in tests".
        mock_outgoing_email(cls)

        cls.group_user = cls.env.ref('base.group_user')
        cls.group_teacher = cls.env.ref('ems.group_teacher')
        cls.group_tutor = cls.env.ref('ems.group_tutor')
        cls.group_coexistence = cls.env.ref('ems.group_coexistence')
        cls.group_reader = cls.env.ref('ems.group_student_data_reader')
        cls.group_orientation = cls.env.ref('ems.group_orientation')
        cls.group_orientation_admin = cls.env.ref('ems.group_orientation_admin')

        cls.role_orientation = cls.env.ref('ems.role_orientation')
        # The post is held by a team; clear any pre-existing assignment so the tests are
        # self-contained regardless of what this database already carries.
        cls.role_orientation.sudo().write({'employee_ids': [(5, 0, 0)]})

        # A tutor owning the group every fixture below hangs from: the whole point of the
        # feature is that guidance/coexistence read this data without being that tutor.
        cls.tutor_user = cls.env['res.users'].with_context(no_reset_password=True).create({
            'name': 'Test Tutor (Reader)', 'login': 'test_tutor_reader',
            'email': 'test_tutor_reader@example.com', 'lang': 'en_US',
            'groups_id': [(4, cls.group_tutor.id), (4, cls.group_user.id)],
        })
        cls.tutor_employee = cls.env['hr.employee'].create({
            'name': 'Test Tutor Employee (Reader)', 'employee_type': 'teacher',
            'user_id': cls.tutor_user.id,
        })

        cls.orientation_user = cls.env['res.users'].with_context(no_reset_password=True).create({
            'name': 'Test Orientation (Reader)', 'login': 'test_orientation_reader',
            'email': 'test_orientation_reader@example.com', 'lang': 'en_US',
            'groups_id': [(4, cls.group_orientation.id), (4, cls.group_user.id)],
        })
        cls.orientation_employee = cls.env['hr.employee'].create({
            'name': 'Test Orientation Employee (Reader)', 'employee_type': 'teacher',
            'user_id': cls.orientation_user.id,
        })

        cls.coexistence_user = cls.env['res.users'].with_context(no_reset_password=True).create({
            'name': 'Test Coexistence (Reader)', 'login': 'test_coexistence_reader',
            'email': 'test_coexistence_reader@example.com', 'lang': 'en_US',
            'groups_id': [(4, cls.group_coexistence.id), (4, cls.group_user.id)],
        })

        # Holds the technical group and nothing else: proves the group stands on its own
        # (group_coexistence does not imply group_teacher) and grants read only.
        cls.reader_only_user = cls.env['res.users'].with_context(no_reset_password=True).create({
            'name': 'Test Reader Only', 'login': 'test_reader_only',
            'email': 'test_reader_only@example.com', 'lang': 'en_US',
            'groups_id': [(4, cls.group_reader.id), (4, cls.group_user.id)],
        })

        # Sees every student centre-wide by design - the yardstick the reader is compared to.
        cls.academic_admin_user = cls.env['res.users'].with_context(no_reset_password=True).create({
            'name': 'Test Academic Admin (Reader)', 'login': 'test_academic_admin_reader',
            'email': 'test_academic_admin_reader@example.com', 'lang': 'en_US',
            'groups_id': [(4, cls.env.ref('ems.group_academic_admin').id), (4, cls.group_user.id)],
        })

        # A plain teacher, neither tutor of the group below nor guidance/coexistence: the
        # control case proving the fixtures really are out of a normal teacher's reach.
        cls.plain_teacher_user = cls.env['res.users'].with_context(no_reset_password=True).create({
            'name': 'Test Plain Teacher (Reader)', 'login': 'test_plain_teacher_reader',
            'email': 'test_plain_teacher_reader@example.com', 'lang': 'en_US',
            'groups_id': [(4, cls.group_teacher.id), (4, cls.group_user.id)],
        })

        cls.level, cls.study, cls.group_record = create_level_study_group(
            cls, 'TSDR',
            level={'name': 'Test Level (Reader)'},
            study={'code': 'TSDR001', 'name': 'Test Study (Reader)'},
            group={'name': 'Test Group (Reader)', 'tutor_id': cls.tutor_employee.id},
        )

        academic_file = create_student_academic_file(cls, 'TSDR', cls.group_record)
        cls.student = academic_file['student']
        cls.course = academic_file['course']
        cls.order = academic_file['order']
        cls.authorization = academic_file['authorization']
        cls.benefit = academic_file['benefit']
        cls.year_record = academic_file['year_record']

        cls.subject = cls.env['ems.subject'].create({
            'code': 'TSDR-SUB-01', 'acronym': 'TSDRS', 'name': 'Test Subject (Reader)',
        })
        cls.grade_session = cls.env['ems.grade_session'].create({
            'group_id': cls.group_record.id, 'subject_id': cls.subject.id, 'round': '1',
            'teacher_id': cls.tutor_employee.id,
        })

        cls.strike = cls.env['ems.strike'].create({
            'student_id': cls.student.id,
            'reason_id': cls.env.ref('ems.strike_reason_other').id,
            'teacher_id': cls.tutor_employee.id,
        })

        cls.issue_tutor = cls.env['ems.attendance_issue_tutor'].create({
            'tutor_id': cls.tutor_employee.id, 'issue_date': date.today(),
        })
        cls.issue_student = cls.env['ems.attendance_issue_student'].create({
            'attendance_issue_tutor_id': cls.issue_tutor.id, 'student_id': cls.student.id,
        })

    # ---------------------------------------------------------------- group wiring

    def test_reader_group_is_technical(self):
        """No category: it must never show up as a pickable role selector on the user form."""
        self.assertFalse(self.group_reader.category_id)

    def test_orientation_implies_teacher_and_reader(self):
        self.assertIn(self.group_teacher, self.group_orientation.implied_ids)
        self.assertIn(self.group_reader, self.group_orientation.implied_ids)

    def test_orientation_admin_implies_orientation(self):
        self.assertIn(self.group_orientation, self.group_orientation_admin.implied_ids)

    def test_coexistence_implies_reader(self):
        """The coexistence coordinator gains the same access without a second set of rules."""
        self.assertIn(self.group_reader, self.group_coexistence.implied_ids)

    def test_orientation_is_its_own_category(self):
        """Transversal to the teacher -> tutor -> HoS chain, like Quality/Coexistence/TAC."""
        self.assertEqual(self.group_orientation.category_id, self.env.ref('ems.category_orientation'))
        self.assertNotEqual(self.group_orientation.category_id, self.env.ref('ems.category_roles'))

    # ---------------------------------------------------------------- role catalog

    def test_role_orientation_catalog_entry(self):
        self.assertEqual(self.role_orientation.employee_type, 'teacher')
        self.assertFalse(self.role_orientation.unipersonal, "The guidance post is held by a team.")
        self.assertEqual(self.role_orientation.group_id, self.group_orientation)

    def test_role_orientation_is_manually_assignable(self):
        """It has no department/company backing, so it is not hierarchy-managed."""
        self.assertFalse(self.role_orientation.is_hierarchy_managed)

    def test_assign_role_orientation_adds_group(self):
        employee = self.env['hr.employee'].create({
            'name': 'Test Guidance Hire (Reader)', 'employee_type': 'teacher',
            'user_id': self.env['res.users'].with_context(no_reset_password=True).create({
                'name': 'Test Guidance Hire', 'login': 'test_guidance_hire',
                'email': 'test_guidance_hire@example.com', 'lang': 'en_US',
                'groups_id': [(4, self.group_user.id)],
            }).id,
        })
        employee.write({'role_ids': [(4, self.role_orientation.id)]})
        self.assertIn(self.group_orientation, employee.user_id.groups_id)
        employee.write({'role_ids': [(3, self.role_orientation.id)]})
        self.assertNotIn(self.group_orientation, employee.user_id.groups_id)

    # ---------------------------------------------------------------- read surface

    def test_reader_can_read_every_student_data_model(self):
        for model in STUDENT_DATA_MODELS:
            with self.subTest(model=model):
                self.assertTrue(
                    self.env[model].with_user(self.reader_only_user).has_access('read'),
                    f"{model} is not readable by group_student_data_reader alone")

    def test_reader_sees_every_record_of_those_models(self):
        """'All students, not just my tutees' means the same row filter an academic admin gets.

        Comparing against `group_academic_admin` rather than asserting an empty domain: Odoo
        returns `[(1, '=', 1)]` for a rule that imposes no filter, and `res.partner` also carries
        Odoo's own global multi-company/portal rules, which apply to every internal user."""
        reader_rules = self.env['ir.rule'].with_user(self.reader_only_user)
        admin_rules = self.env['ir.rule'].with_user(self.academic_admin_user)

        def unfiltered(domain):
            # A model nobody row-filters yields []; one whose rule imposes no filter yields
            # [(1, '=', 1)]. Both mean the same thing here.
            return [leaf for leaf in (domain or []) if leaf != (1, '=', 1)]

        for model in STUDENT_DATA_MODELS:
            with self.subTest(model=model):
                self.assertEqual(
                    unfiltered(reader_rules._compute_domain(model, 'read')),
                    unfiltered(admin_rules._compute_domain(model, 'read')),
                    f"{model} is still row-filtered for group_student_data_reader")

    def test_reader_grants_read_only(self):
        for model in STUDENT_DATA_MODELS:
            for operation in ('write', 'create', 'unlink'):
                with self.subTest(model=model, operation=operation):
                    self.assertFalse(
                        self.env[model].with_user(self.reader_only_user).has_access(operation),
                        f"group_student_data_reader must not grant {operation} on {model}")

    def test_reader_does_not_reach_financial_data(self):
        for model in FINANCIAL_MODELS:
            with self.subTest(model=model):
                self.assertFalse(
                    self.env[model].with_user(self.reader_only_user).has_access('read'),
                    f"{model} is out of scope for issue #393")

    # ------------------------------------------------- real records, not just the wiring

    def test_orientation_reads_grades_of_a_group_it_does_not_tutor(self):
        session = self.grade_session.with_user(self.orientation_user)
        self.assertEqual(session.subject_id, self.subject)

    def test_plain_teacher_still_cannot_read_those_grades(self):
        """Control case: without this feature the record really is out of reach."""
        with self.assertRaises(AccessError):
            self.grade_session.with_user(self.plain_teacher_user).read(['subject_id'])

    def test_every_teacher_reads_any_students_academic_history(self):
        """Issue #393, widened scope: the centre considers a student's academic history necessary
        information for the whole teaching community, so it is no longer tutor-scoped. A plain
        teacher, tutor of nobody, must read it - and its subject/outcome children with it."""
        record = self.year_record.with_user(self.plain_teacher_user)
        self.assertEqual(record.student_id, self.student)
        for model in ('ems.student.year_record', 'ems.student.year_record.subject',
                      'ems.student.year_record.outcome'):
            with self.subTest(model=model):
                rules = self.env['ir.rule'].with_user(self.plain_teacher_user)
                self.assertEqual([leaf for leaf in (rules._compute_domain(model, 'read') or [])
                                  if leaf != (1, '=', 1)], [],
                                 f"{model} is still tutor-scoped for a plain teacher")

    def test_academic_history_stays_read_only_for_teachers(self):
        """Widening the read scope must not have handed anyone write access."""
        for operation in ('write', 'create', 'unlink'):
            with self.subTest(operation=operation):
                self.assertFalse(
                    self.env['ems.student.year_record']
                        .with_user(self.plain_teacher_user).has_access(operation))

    def test_academic_history_menu_is_reachable_by_any_teacher(self):
        visible = self.env['ir.ui.menu'].with_user(self.plain_teacher_user).search([]).ids
        self.assertIn(self.env.ref('ems.menu_year_record').id, visible)

    def test_orientation_reads_year_record_of_any_student(self):
        self.assertEqual(
            self.year_record.with_user(self.orientation_user).student_id, self.student)

    def test_coexistence_reads_year_record_of_any_student(self):
        self.assertEqual(
            self.year_record.with_user(self.coexistence_user).student_id, self.student)

    def test_orientation_reads_attendance_issues_of_any_student(self):
        self.assertEqual(
            self.issue_student.with_user(self.orientation_user).student_id, self.student)

    def test_coexistence_reads_attendance_issues_of_any_student(self):
        """The daily attendance issues behind an incident, previously tutor-only."""
        self.assertEqual(
            self.issue_student.with_user(self.coexistence_user).student_id, self.student)

    def test_orientation_reads_strikes_of_any_student(self):
        self.assertEqual(
            self.strike.with_user(self.orientation_user).student_id, self.student)

    def test_orientation_cannot_write_a_strike(self):
        with self.assertRaises(AccessError):
            self.strike.with_user(self.orientation_user).write({'notes': 'nope'})

    def test_orientation_cannot_write_a_year_record(self):
        with self.assertRaises(AccessError):
            self.year_record.with_user(self.orientation_user).write({'study_name': 'nope'})

    def test_students_screen_is_not_narrowed_to_own_tutees(self):
        """`action_student_group_enrollment` hard-codes a tutor filter in server-side code, so a
        row-level permission alone would still render an empty list - see its own comment."""
        action = self.env.ref('ems.action_student_group_enrollment')
        for user in (self.orientation_user, self.coexistence_user):
            with self.subTest(user=user.login):
                result = action.with_user(user).run()
                self.assertNotIn(('tutor_id.user_id', '=', user.id), result['domain'],
                                 f"{user.login} would only see their own tutees")

    def test_secretary_tab_data_is_visible(self):
        """The Secretary tab's authorizations resolve through `_ems_enrollment_in_force()`, which
        walks `sale_order_ids`. Without read access there the walk yields nothing silently: the
        tab renders empty and every auth_* badge reads "No" on a student who did sign."""
        for user in (self.orientation_user, self.coexistence_user):
            with self.subTest(user=user.login):
                student = self.student.with_user(user)
                self.assertEqual(student.ems_authorization_ids, self.authorization,
                                 "the Secretary tab would render empty")
                self.assertTrue(student.auth_image,
                                "the authorization badge would wrongly read 'No'")

    def test_benefits_are_visible(self):
        """The other half of the Secretary tab."""
        for user in (self.orientation_user, self.coexistence_user):
            with self.subTest(user=user.login):
                self.assertEqual(self.student.with_user(user).benefit_ids, self.benefit)

    # ---------------------------------------------------------------- menu visibility

    def test_student_data_menus_are_visible_to_both_posts(self):
        for user in (self.orientation_user, self.coexistence_user):
            visible = self.env['ir.ui.menu'].with_user(user).search([]).ids
            for xmlid in STUDENT_DATA_MENU_XMLIDS:
                with self.subTest(user=user.login, menu=xmlid):
                    self.assertIn(self.env.ref(xmlid).id, visible,
                                  f"{xmlid} is not reachable by {user.login}")
