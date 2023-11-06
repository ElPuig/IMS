# -*- coding: utf-8 -*-

from odoo import models, fields, api

class ims_provider(models.Model):
	_name = "ims.provider"
	_description = "Provider: Collects corporative data."
	_inherit = "ims.person"
	
	role = fields.Char(string="Role")
	company = fields.Many2one(string="Company", comodel_name="ims.company")