# -*- coding: utf-8 -*-

from odoo import models, fields, api

class ims_attachment(models.Model):
	_name = "ims.attachment"
	_description = "Attachment file."
	
	name = fields.Char(string="Name", required="true")
	file = fields.Binary(string="File", required="true")
	domain = fields.Char(string="Domain") # Used to filter the atachment by model, empty means "for all"

	def open_form_attachment(self):
		return {
			'name': 'Attachment Edit',
			'domain': [],
			'res_model': 'ims.attachment',
			'type': 'ir.actions.act_window',
			'view_mode': 'form',
			'view_type': 'form',
			'res_id': self.id,
			'context': self._context,
			'target': 'new',
		}

	def download(self):        
		return {
			'name': self.name,
			'type': 'ir.actions.act_url',
			'url': "web/content/?model=" + self._name +"&id=" + str(self.id) + "&filename_field=name&field=file&download=true&filename=" + self.name,
			'target': 'self',
		}