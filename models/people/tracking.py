# -*- coding: utf-8 -*-

#TODO: rename to 'tracking'
from odoo import models, fields, api

class ims_tracking(models.Model):
	_name = 'ims.tracking'
	_description = 'Tracking: Tutors and teachers can add information about the student evolution, follow-up, etc.'
	
	notes = fields.Text('Notes')

	teacher = fields.Many2one(comodel_name="ims.teacher", string="Teacher")
	student = fields.Many2one(comodel_name="ims.student", string="Student")
	study = fields.Many2one(comodel_name="ims.study", string="Study")
	professional_module = fields.Many2one(comodel_name="ims.professional_module", string="Professional Module")
	formative_unit = fields.Many2one(comodel_name="ims.formative_unit", string="Formative Unit")
