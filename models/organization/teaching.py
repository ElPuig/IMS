# -*- coding: utf-8 -*-

from odoo import models, fields, api

class ims_teaching(models.Model):
	_name = "ims.teaching"
	_description = "Teaching: ternary relation between teacher-group-uf."	

	teacher = fields.Many2one(string="Teacher", comodel_name="ims.teacher", required="true")	
	group = fields.Many2one(string="Group", comodel_name="ims.student_group", required="true")	
	formative_unit = fields.Many2one(string="Formative Unit", comodel_name="ims.formative_unit", required="true")	