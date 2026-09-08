from odoo.exceptions import AccessError
from odoo.tests.common import TransactionCase


class TestTeachingReductionType(TransactionCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.head_of_department_user = cls.env['res.users'].with_context(no_reset_password=True).create({
            'name': 'Test Head of Department (Teaching Reduction Type)',
            'login': 'test_hod_for_teaching_reduction_type',
            'groups_id': [(4, cls.env.ref('ems.group_department_chief').id)],
        })
        cls.teacher_user = cls.env['res.users'].with_context(no_reset_password=True).create({
            'name': 'Test Teacher (Teaching Reduction Type)',
            'login': 'test_teacher_for_teaching_reduction_type',
            'groups_id': [(4, cls.env.ref('ems.group_teacher').id)],
        })
        cls.test_type = cls.env['ems.teaching_reduction_type'].create({
            'code': 'TST',
            'name': 'Test Type',
            'reduction_hours': 2,
        })

    def test_create_valid(self):
        reduction_type = self.env['ems.teaching_reduction_type'].create({'code': 'T01', 'name': 'Test 01', 'reduction_hours': 3})
        self.assertTrue(reduction_type.id)
        self.assertEqual(reduction_type.code, 'T01')
        self.assertEqual(reduction_type.name, 'Test 01')
        self.assertEqual(reduction_type.reduction_hours, 3)
        self.assertTrue(reduction_type.active)

    def test_create_missing_code(self):
        with self.assertRaises(Exception):
            self.env['ems.teaching_reduction_type'].create({'name': 'No Code', 'reduction_hours': 1})

    def test_create_missing_name(self):
        with self.assertRaises(Exception):
            self.env['ems.teaching_reduction_type'].create({'code': 'T02', 'reduction_hours': 1})

    def test_create_missing_reduction_hours(self):
        with self.assertRaises(Exception):
            self.env['ems.teaching_reduction_type'].create({'code': 'T03', 'name': 'No Hours'})

    def test_code_must_be_unique(self):
        self.env['ems.teaching_reduction_type'].create({'code': 'UNIQ', 'name': 'First', 'reduction_hours': 1})
        with self.assertRaises(Exception):
            self.env['ems.teaching_reduction_type'].create({'code': 'UNIQ', 'name': 'Second', 'reduction_hours': 1})

    def test_display_name(self):
        reduction_type = self.env['ems.teaching_reduction_type'].create({'code': 'T04', 'name': 'Age reduction', 'reduction_hours': 2})
        self.assertEqual(reduction_type.display_name, 'Age reduction')

    def test_admin_can_create(self):
        reduction_type = self.env['ems.teaching_reduction_type'].with_user(self.head_of_department_user).create({
            'code': 'T05', 'name': 'Admin Test', 'reduction_hours': 1,
        })
        self.assertTrue(reduction_type.id)

    def test_admin_can_write(self):
        reduction_type = self.env['ems.teaching_reduction_type'].create({'code': 'T06', 'name': 'Before Write', 'reduction_hours': 1})
        reduction_type.with_user(self.head_of_department_user).write({'name': 'After Write'})
        self.assertEqual(reduction_type.name, 'After Write')

    def test_admin_can_unlink(self):
        reduction_type = self.env['ems.teaching_reduction_type'].create({'code': 'T07', 'name': 'To Delete', 'reduction_hours': 1})
        type_id = reduction_type.id
        reduction_type.with_user(self.head_of_department_user).unlink()
        self.assertFalse(self.env['ems.teaching_reduction_type'].search([('id', '=', type_id)]))

    def test_teacher_cannot_create(self):
        with self.assertRaises(AccessError):
            self.env['ems.teaching_reduction_type'].with_user(self.teacher_user).create({
                'code': 'T08', 'name': 'Teacher Attempt', 'reduction_hours': 1,
            })

    def test_teacher_cannot_write(self):
        with self.assertRaises(AccessError):
            self.test_type.with_user(self.teacher_user).write({'name': 'Teacher Write'})

    def test_teacher_cannot_unlink(self):
        with self.assertRaises(AccessError):
            self.test_type.with_user(self.teacher_user).unlink()

    def test_teacher_can_read(self):
        reduction_type = self.test_type.with_user(self.teacher_user)
        self.assertEqual(reduction_type.name, 'Test Type')

    def test_employee_can_have_several_reduction_types(self):
        other_type = self.env['ems.teaching_reduction_type'].create({'code': 'T09', 'name': 'Other Type', 'reduction_hours': 1})
        employee = self.env['hr.employee'].create({
            'name': 'Test Teacher With Reductions',
            'employee_type': 'teacher',
            'teaching_reduction_ids': [(6, 0, [self.test_type.id, other_type.id])],
        })
        self.assertEqual(employee.teaching_reduction_ids, self.test_type | other_type)

    def test_reduction_hours_added_to_teaching_summary(self):
        employee = self.env['hr.employee'].create({
            'name': 'Test Teacher Reduction Summary',
            'employee_type': 'teacher',
            'teaching_reduction_ids': [(6, 0, [self.test_type.id])],
        })
        summary = employee.resource_calendar_id.get_schedule_hours_summary()
        reduction_row = next(row for row in summary['teaching']['rows'] if row['label'] == 'Test Type')
        self.assertEqual(reduction_row['hours'], 2)
        self.assertEqual(summary['teaching']['total'], 2)
        self.assertEqual(summary['total'], 2)
