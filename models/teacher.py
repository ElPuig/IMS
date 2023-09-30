# -*- coding: utf-8 -*-

from odoo import models, fields, api

class ims_teacher(models.Model):
	_name = "ims.teacher"
	_description = "Teacher: Collects the teacher\"s data."
	_inherit = "ims.person"

	tutor = fields.One2many(string="Tutor", comodel_name="ims.group", inverse_name="tutor")
	teaching = fields.One2many(string="Teaching", comodel_name="ims.teaching", inverse_name="teacher")

	# formative_units = fields.One2many(string="Formative Units", comodel_name="ims.formative_unit", inverse_name="teacher")
	# professional_modules = fields.One2many(string="Professional Modules", comodel_name="ims.professional_module", inverse_name="teacher")
	trackings = fields.One2many(string="Follow-ups", comodel_name="ims.tracking", inverse_name="teacher")