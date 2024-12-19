# -*- coding: utf-8 -*-

from odoo import models, fields, api
from odoo.exceptions import ValidationError

class ims_content(models.Model):
	_name = "ims.content"
	_description = "Content: Defines a subject's content."
	_order = "code asc"
	_sql_constraints = [
		('unique_content_code', 'unique (subject_id, code)', 'duplicated code!')
    ]
	
	code = fields.Char(string="Code", required=True)
	acronym = fields.Char(string="Acronym", required=True)
	name = fields.Char(string="Name", required=True)	
	content_ids = fields.One2many(string="Composite", comodel_name="ims.content", inverse_name="content_id")
	content_id = fields.Many2one(string="Parent", comodel_name="ims.content")
	subject_id = fields.Many2one(string="Subject", comodel_name="ims.subject", compute="_compute_subject", store=True)
	notes = fields.Text(string="Notes")	
	
	# The following fields are computed and used to display the data correctly within the treeview
	level = fields.Integer(string="Level", default=1, compute="_compute_level", store=True)			
	
	@api.depends("content_id")
	def _compute_level(self):
		for rec in self:
			if rec.content_id.id != False: rec.level = rec.content_id.level + 1 

	@api.depends("content_id")
	def _compute_subject(self):	  		      
		for rec in self:
			if rec.content_id.id != False: rec.subject_id = rec.content_id.subject_id
			if rec.content_id.id != False: rec.level = rec.content_id.level + 1 

	@api.constrains('code')
	def check_code(self):
		for rec in self:
			if rec.content_id.id != False: 
				if not rec.code.startswith(rec.content_id.code):
					raise ValidationError("The code must start as the parent's code.")
	
	@api.depends('acronym', 'name')
	def _compute_display_name(self):              
		for rec in self:
			rec.display_name = "%s: %s" % (rec.acronym, rec.name)

	def open_form_content(self):
		return {
            'name': 'Content Edit',     
			'type': 'ir.actions.act_window',
            'res_model': 'ims.content',
            'res_id': self.id,						
            'view_id': self.env.ref('ims.view_content_form').id,
            'view_mode': 'form',
			'target': 'new'
        }	