# -*- coding: utf-8 -*-

from odoo import models, fields, api

class ims_teacher_role(models.Model):
	_name = "ims.teacher_role"
	_description = "Teacher's position: The coordination position held by the teachers staff."

	name = fields.Char(string="Name", required="true")	
	teacher = fields.Many2one(string="Teacher", comodel_name="ims.teacher")
	notes = fields.Text(string="Notes")