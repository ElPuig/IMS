# -*- coding: utf-8 -*-

from odoo import models, fields, api

class ims_person(models.Model):
	_name = "ims.person"
	_description = "Person: Collects just personal data."

	name = fields.Char(string="Name", required="true")
	surname = fields.Char(string="Surname", required="true")	
	email = fields.Char(string="Email")	
	phone = fields.Char(string="Phone")
	image = fields.Binary(string="Image")
	notes = fields.Text(string="Notes")

	def name_get(self):
		#Allows displaying a custom name: https://www.odoo.com/documentation/16.0/es/developer/reference/backend/orm.html#odoo.models.Model.name_get

		result = []	
		for rec in self:
			result.append((rec.id, '%s %s' % (rec.name, rec.surname)))
			
		return result