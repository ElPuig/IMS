# -*- coding: utf-8 -*-

from odoo import models, fields, api

class ims_attendance_group(models.Model):
	_name = 'ims.attendance_group'
	_description = 'Attendance templates linked to a student group that allows template batch generation'
	_inherit = 'ims.attendance_template'
	
	name = fields.Char("Name")

	group = fields.Many2one(comodel_name="ims.group", string="Grup")	
	attendance_templates = fields.One2many(comodel_name="ims.attendance_template", inverse_name="attendance_group", string="Templates")
	attendance_sessions = fields.One2many(comodel_name="ims.attendance_session", inverse_name="attendance_group", string="Sessions")

	hasTemplates = fields.Boolean(compute='compute_hasTemplates', store=False)

	@api.depends('attendance_templates')
	def compute_hasTemplates(self):
		for record in self:
			record.hasTemplates = len(record.attendance_templates) > 0

	def GenerateTemplatesByStudent (self):
		for student in self.group.students:			
			template = self.env['ims.attendance_template'].create({
				'start_time': self.start_time,
				'end_time': self.end_time,
				'teacher': self.teacher.id,
				'study': self.study.id,
				'student': student.id,
				'mp': self.mp.id,
				'uf': self.uf.id,
				'level': self.level.id,
				'space': self.space.id,
				'weekday': self.weekday,
				'color': self.color,
				'attendance_group': self.id
			})