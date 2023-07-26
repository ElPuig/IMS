# -*- coding: utf-8 -*-

from odoo import models, fields, api
from . import attendance_template

class ims_attendance_group(models.Model):
	_name = 'ims.attendance_group'
	_description = 'Attendance templates linked to a student group that allows template batch generation'
	_inherit = 'ims.attendance_template'
	
	name = fields.Char("Name")

	student_group = fields.Many2one(comodel_name="ims.group", string="Grup")	
	attendance_templates = fields.One2many(comodel_name="ims.attendance_template", inverse_name="attendance_group", string="Template group")

	def GenerateTemplatesByStudent (self):
		for student in self.student_group.students:			
			template = self.env['ims.attendance_template'].create({
				'start_time': self.start_time,
				'end_time': self.end_time,
				'teacher': self.teacher.id,
				'study': self.study.id,
				'student': student.id,
				'mp': self.mp.id,
				'uf': self.uf.id,
				'level': self.level.id,
				'classroom': self.classroom.id,
				'weekday': self.weekday,
				'color': self.color,
			})