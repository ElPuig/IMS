# -*- coding: utf-8 -*-

#TODO: rename to 'tracking'
from odoo import models, fields, api

class ims_tracking(models.Model):
	_name = 'ims.tracking'
	_description = 'Tracking: Tutors and teachers can add information about the student evolution, follow-up, etc.'
	
	notes = fields.Text('Notes')

	teacher_id = fields.Many2one(string="Teacher", comodel_name="hr.employee", domain="[('employee_type', '=', 'teacher')]")
	student_id = fields.Many2one(string="Student", comodel_name="res.partner")
	study_id = fields.Many2one(string="Study", comodel_name="ims.study")
	professional_module_id = fields.Many2one(string="Professional Module", comodel_name="ims.professional_module")
	formative_unit_id = fields.Many2one(string="Formative Unit", comodel_name="ims.formative_unit")

