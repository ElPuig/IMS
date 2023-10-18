# -*- coding: utf-8 -*-

from odoo import models, fields, api

class ims_company(models.Model):
	_name = "ims.company"
	_description = "Company: Collects company data."	
	
	name = fields.Char(string="Name", required="true")
	vat = fields.Char(string="VAT")
	image = fields.Binary(string="Image")
	notes = fields.Text(string="Notes")

	contacts = fields.One2many(string="Contacts", comodel_name="ims.provider", inverse_name="company")