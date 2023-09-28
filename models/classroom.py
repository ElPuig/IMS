# -*- coding: utf-8 -*-

from odoo import models, fields, api

class ims_classroom(models.Model):
	_name = "ims.classroom"
	_description = "Classroom: where each student group are assigned to."
	
	code = fields.Text(string="Numeric Code", required="true")
	name = fields.Text(string="Name", required="true")

