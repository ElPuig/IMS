# -*- coding: utf-8 -*-

from odoo import models, fields, api

class ims_professional_module(models.Model):
	_name = "ims.professional_module"
	_description = "Professional Module: Is how a subject is called in VET studies and it\"s composed by Formative Units so every FU must be passed in order to pass also the PM."

	code = fields.Char(string="Code", required="true")
	acronym = fields.Char(string="Acronym", required="true")
	name = fields.Char(string="Name", required="true")
	#start_date = fields.Date("Start date")	#WARNING: this should be computed by FUs and can change between courses
	#end_date = fields.Date("End date")		#WARNING: this should be computed by FUs and can change between courses
	#started = fields.Boolean("Started")
	notes = fields.Text("Notes")

	teacher = fields.Many2one(string="Teacher", comodel_name="ims.teacher")
	study = fields.Many2one(string="Study", comodel_name="ims.study")
	formative_units = fields.One2many(string="Formative Units", comodel_name="ims.formative_unit", inverse_name="professional_module")
	trackings = fields.One2many(string="Follow-ups", comodel_name="ims.tracking", inverse_name="professional_module")