# -*- coding: utf-8 -*-

from odoo import models, fields, api

class ims_teaching(models.Model):
	_name = "ims.teaching"
	_description = "Teaching: ternary relation between teacher-group-uf."	
	_sql_constraints = [
		('ims_teaching_unique', 
		'unique(teacher_id, group_id, subject_id)',
		'The ternary "teacher / group / subject" must be unique!')
	]

	teacher_id = fields.Many2one(string="Teacher", comodel_name="hr.employee", required=True, domain="[('employee_type', '=', 'teacher')]")	
	group_id = fields.Many2one(string="Group", comodel_name="ims.group", required=True)	
	subject_id = fields.Many2one(string="Subject", comodel_name="ims.subject", required=True)	
	
	# this field is used to change the style of the row in the view
	level = fields.Integer(string="Level", related="subject_id.level", store=False)		