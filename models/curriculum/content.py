# -*- coding: utf-8 -*-

from odoo import models, fields, api

class ims_content(models.Model):
	_name = "ims.content"
	_description = "Content: Defines a subject's content."
	_order = "code asc"

	#TODO: Maybe, if content_id is not null (descendant), check that the code starts by parent code. Otherwise, nested items wont be displayed properly in treeeview.
	code = fields.Char(string="Code", required="true")
	acronym = fields.Char(string="Acronym", required="true")
	name = fields.Char(string="Name", required="true")	
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

	def open_form_content(self):
		return {
            'name': 'Content Edit',
            'domain': [],
            'res_model': 'ims.content',
            'type': 'ir.actions.act_window',
            'view_mode': 'form',
            'view_type': 'form',
            'res_id': self.id,
            'target': 'new'
        }