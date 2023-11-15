# -*- coding: utf-8 -*-

from odoo import models, fields, api

class ims_enrollment(models.Model):
	_name = "ims.enrollment"
	_description = "Enrollment: ternary relation between student-group-uf."	

	student_id = fields.Many2one(string="Student", comodel_name="res.partner", required="true", domain="[('contact_type', '=', 'student')]")	
	group_id = fields.Many2one(string="Group", comodel_name="ims.group", required="true")	
	formative_unit_id = fields.Many2one(string="Formative Unit", comodel_name="ims.formative_unit", required="true")	