# -*- coding: utf-8 -*-

from odoo import models, fields, api

class ims_teaching(models.Model):
	_name = "ims.teaching"
	_description = "Teaching: ternary relation between teacher-group-uf."	

	teacher_id = fields.Many2one(string="Teacher", comodel_name="hr.employee", required="true", domain="[('employee_type', '=', 'teacher')]")	
	group_id = fields.Many2one(string="Group", comodel_name="ims.group", required="true")	
	subject_id = fields.Many2one(string="Subject", comodel_name="ims.subject", required="true")	