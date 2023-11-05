# -*- coding: utf-8 -*-

from odoo import models, fields, api

class ims_teaching(models.Model):
	_name = "ims.teaching"
	_description = "Teaching: ternary relation between teacher-group-uf."	

	teacher_id = fields.Many2one(string="Teacher", comodel_name="hr.employee", required="true", domain="[('employee_type', '=', 'teacher')]")	
	group_id = fields.Many2one(string="Group", comodel_name="ims.group", required="true")	
	formative_unit_id = fields.Many2one(string="Formative Unit", comodel_name="ims.formative_unit", required="true")	