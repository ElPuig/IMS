# -*- coding: utf-8 -*-

from odoo import models, fields, api

class ims_teaching(models.Model):
	_name = "ims.teaching"
	_description = "Teaching: ternary relation between teacher-group-uf."	

	teacher_id = fields.Many2one(string="Teacher", comodel_name="hr.employee", required=True, domain="[('employee_type', '=', 'teacher')]")	
	group_id = fields.Many2one(string="Group", comodel_name="ims.group", required=True)	
	subject_id = fields.Many2one(string="Subject", comodel_name="ims.subject", required=True)	
	level = fields.Integer(string="Level", related="subject_id.level")				