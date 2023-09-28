# -*- coding: utf-8 -*-

from odoo import models, fields, api

class ims_teacher(models.Model):
	_name = "ims.teacher"
	_description = "Teacher: Collects the teacher\"s data."

	name = fields.Char(string="Name", required="true")
	surname = fields.Char(string="Surname", required="true")
	professional_email = fields.Char(string="Email (professional)", required="true")
	personal_email = fields.Char(string="Email (personal)")
	professional_phone = fields.Char(string="Phone (professional)")
	personal_phone = fields.Char(string="Phone (personal)")
	image = fields.Binary(string=" ") #empty label for image filed (widget image will be used, and nocaption="1" produces side effects with the image size...)
	notes = fields.Text(string="Notes")

	formative_units = fields.One2many(string="Formative Units", comodel_name="ims.formative_unit", inverse_name="teacher")
	professional_modules = fields.One2many(string="Professional Modules", comodel_name="ims.professional_module", inverse_name="teacher")
	trackings = fields.One2many(string="Follow-ups", comodel_name="ims.tracking", inverse_name="teacher")