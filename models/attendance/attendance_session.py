# -*- coding: utf-8 -*-

from odoo import models, fields, api

class ims_attendance_session(models.Model):
	_name = 'ims.attendance_session'
	_description = 'Every concrete class session'
	
	date = fields.Datetime(string="Date", default = fields.Datetime.now)
	start_time = fields.Float("Start Time", default=lambda self: self.attendance_group.start_time)
	end_time = fields.Float("End Time", default=lambda self: self.attendance_group.end_time)
	notes = fields.Text('Notes')

	attendance_group = fields.Many2one(comodel_name="ims.attendance_group", string="Attendance Group")

	student_group = fields.Many2one(comodel_name="ims.student_group", string="Grup")	
	attendance_statuses = fields.One2many(comodel_name="ims.attendance_status", inverse_name="attendance_session", string="Student status")

	hasStatuses = fields.Boolean(compute='compute_hasStatuses', store=False)

	@api.depends('attendance_statuses')
	def compute_hasStatuses(self):
		for record in self:
			record.hasStatuses = len(record.attendance_statuses) > 0

	def GenerateStatusesByTemplates (self):
		for student in self.attendance_group.attendance_templates.student:
			status = self.env['ims.attendance_status'].create({
				'attendance_session': self.id,
				'student' : student.id,
				'status' : '1'
			})

			