# -*- coding: utf-8 -*-

from odoo import models, fields, api

class ims_followupup(models.Model):
	_name = 'ims.followup'
	_description = 'Follow-up'
	
	notes = fields.Text('Notes')

	teacher = fields.Many2one(comodel_name="ims.teacher", string="Teacher")
	student = fields.Many2one(comodel_name="ims.student", string="Student")
	study = fields.Many2one(comodel_name="ims.study", string="Study")
	professional_module = fields.Many2one(comodel_name="ims.professional_module", string="Professional Module")
	formative_unit = fields.Many2one(comodel_name="ims.formative_unit", string="Formative Unit")

