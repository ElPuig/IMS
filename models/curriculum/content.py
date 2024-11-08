# -*- coding: utf-8 -*-

from odoo import models, fields, api

class ims_content(models.Model):
	_name = "ims.content"
	_description = "Content: Defines a subject's content."
	
	acronym = fields.Char(string="Acronym", required="true")
	name = fields.Char(string="Name", required="true")
	content_ids = fields.One2many(string="Composite", comodel_name="ims.content", inverse_name="content_id")
	content_id = fields.Many2one(string="Parent", comodel_name="ims.content")
	subject_id = fields.Many2one(string="Subject", comodel_name="ims.subject")

	notes = fields.Text(string="Notes")

	def open_form_view_content(self):
		return {
            'name': 'Content Edit',
            'domain': [],
            'res_model': 'ims.content',
            'type': 'ir.actions.act_window',
            'view_mode': 'form',
            'view_type': 'form',
            'res_id': self.id,
            'target': 'new',
        }