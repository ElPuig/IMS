# -*- coding: utf-8 -*-

from odoo import models, fields, api

class ims_professional_module(models.Model):
	_name = "ims.professional_module"
	_description = "Professional Module: Is how a subject is called in VET studies and it\"s composed by Formative Units so every FU must be passed in order to pass also the PM."

	code = fields.Char(string="Code", required="true")
	acronym = fields.Char(string="Acronym", required="true")
	name = fields.Char(string="Name", required="true")	
	notes = fields.Text("Notes")
	
	study_id = fields.Many2one(string="Study", comodel_name="ims.study", required="true")
	formative_unit_ids = fields.One2many(string="Formative Units", comodel_name="ims.formative_unit", inverse_name="professional_module_id")
	
	teacher_id = fields.Many2one(string="Teacher", comodel_name="hr.employee", domain="[('employee_type', '=', 'teacher')]")
	tracking_ids = fields.One2many(string="Follow-ups", comodel_name="ims.tracking", inverse_name="professional_module_id")

	def name_get(self):
		#Allows displaying a custom name: https://www.odoo.com/documentation/16.0/es/developer/reference/backend/orm.html#odoo.models.Model.name_get

		result = []	
		for rec in self:
			result.append((rec.id, '%s %s: %s' % (rec.study_id.acronym, rec.acronym, rec.name)))
			
		return result