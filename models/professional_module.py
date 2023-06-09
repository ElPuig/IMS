# -*- coding: utf-8 -*-

from odoo import models, fields, api

class ims_professional_module(models.Model):
	_name = 'ims.professional_module'
	_description = 'Profesional Module'

	code = fields.Char('Official Code')
	number = fields.Integer('Number')
	name = fields.Char('Name')
	#start_date = fields.Date('Start date')	#WARNING: this should be computed by FUs and can change between courses
	#end_date = fields.Date('End date')		#WARNING: this should be computed by FUs and can change between courses
	#started = fields.Boolean('Started')
	image = fields.Binary('Image')
	notes = fields.Text('Notes')

	teacher = fields.Many2one(comodel_name="ims.teacher", string="Teacher")
	study = fields.Many2one(comodel_name="ims.study", string="Study")
	formative_units = fields.One2many(comodel_name="ims.formative_unit", inverse_name="professional_module", string="Formative Units")
	followups = fields.One2many(comodel_name="ims.followup", inverse_name="professional_module", string="Follow-ups")