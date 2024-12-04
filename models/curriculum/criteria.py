# -*- coding: utf-8 -*-

from odoo import models, fields, api

class ims_criteria(models.Model):
	_name = "ims.criteria"		
	_description = "Criteria: Defines a subject's criteria."

	acronym = fields.Char(string="Acronym", required="true")
	name = fields.Char(string="Name", required="true")	
	criteria_ids = fields.One2many(string="Composite", comodel_name="ims.criteria", inverse_name="criteria_id")
	criteria_id = fields.Many2one(string="Parent", comodel_name="ims.criteria")
	subject_id = fields.Many2one(string="Subject", comodel_name="ims.subject")	

	notes = fields.Text(string="Notes")
		

	def open_form_criteria(self):
		return {
            'name': 'Criteria Edit',
            'domain': [],
            'res_model': 'ims.criteria',
            'type': 'ir.actions.act_window',
            'view_mode': 'form',
            'view_type': 'form',
            'res_id': self.id,
            'target': 'new',
        }