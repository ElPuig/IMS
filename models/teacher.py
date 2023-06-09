# -*- coding: utf-8 -*-

from odoo import models, fields, api

class ims_teacher(models.Model):
	_name = 'ims.teacher'
	_description = 'Teacher'

	name = fields.Char('Name')
	surname = fields.Char('Surnames')
	email = fields.Char('Email')	
	image = fields.Binary('image')
	notes = fields.Text('Notes')

	formative_units = fields.One2many(comodel_name="ims.formative_unit", inverse_name="teacher", string="Formative Units")
	professional_modules = fields.One2many(comodel_name="ims.professional_module", inverse_name="teacher", string="Professional Modules")
	followups = fields.One2many(comodel_name="ims.followup", inverse_name="teacher", string="Follow-ups")