# -*- coding: utf-8 -*-

from odoo import models, fields, api

class ims_student_group(models.Model):
	_name = 'ims.student_group'
	_description = 'Student groups'

	code = fields.Char('Code')
	name = fields.Char('Name')
	email = fields.Char('Email')	
	notes = fields.Text('Notes')

	students = fields.One2many(comodel_name="ims.student", inverse_name="student_group", string="Students")
	template_groups = fields.One2many(comodel_name="ims.template_group", inverse_name="student_group", string="Student groups")