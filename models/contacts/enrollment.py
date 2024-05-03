# -*- coding: utf-8 -*-

from odoo import models, fields, api

class ims_enrollment(models.Model):
	_name = "ims.enrollment"
	_description = "Enrollment: ternary relation between student-group-uf."	

	student_id = fields.Many2one(string="Student", comodel_name="res.partner", required="true", domain="[('contact_type', '=', 'student')]")	
	group_id = fields.Many2one(string="Group", comodel_name="ims.group", required="true")	
	subject_id = fields.Many2one(string="Subject", comodel_name="ims.subject", required="true")	