# -*- coding: utf-8 -*-

from odoo import models, fields, api
from odoo.exceptions import ValidationError

class ims_outcome(models.Model):
	_name = 'ims.outcome'
	_description = 'Learning outcome: what the student should learn.'
	_order = 'code asc'
	_sql_constraints = [
		('unique_code', 'unique (subject_id, code)', 'duplicated code!')
    ]
	
	code = fields.Char(string='Code', required=True)
	acronym = fields.Char(string='Acronym', required=True)
	name = fields.Char(string='Name', required=True)			
	outcome_ids = fields.One2many(string="Composite", comodel_name="ims.outcome", inverse_name="outcome_id")
	outcome_id = fields.Many2one(string="Parent", comodel_name="ims.outcome")
	subject_id = fields.Many2one(string='Subject', comodel_name='ims.subject', compute='_compute_subject', store=True)
	notes = fields.Text(string='Notes')		

	# The following fields are computed and used to display the data correctly within the treeview
	#level = fields.Integer(string="Level", default=1, compute="_compute_level", store=True)						
	level = fields.Integer(string="Level", default=1, store=True)						
	
	# @api.depends("outcome_id")
	# def _compute_level(self):
	# 	for rec in self:
	# 		if rec.outcome_id.id != False: rec.level = rec.outcome_id.level + 1 

	@api.depends("outcome_id")
	def _compute_subject(self):	  		      
		for rec in self:
			if rec.outcome_id.id != False: rec.subject_id = rec.outcome_id.subject_id
			if rec.outcome_id.id != False: rec.level = rec.outcome_id.level + 1 

	@api.constrains('code')
	def _check_code(self):
		for rec in self:
			if rec.outcome_id.id != False: 
				if not rec.code.startswith(rec.outcome_id.code):
					raise ValidationError("The code must start as the parent's code.")
	
	@api.depends('acronym', 'name')
	def _compute_display_name(self):              
		for rec in self:
			rec.display_name = "%s: %s" % (rec.acronym, rec.name)

	def open_form(self):
		return {
            'name': '%s Edit' % self._description.split(':')[0],
			'type': 'ir.actions.act_window',
            'res_model': self._name,
            'res_id': self.id,						
            'view_id': self.env.ref('ims.view_%s_form' % (self._name.split('.')[1])).id,
            'view_mode': 'form',
			'target': 'new'
        }	