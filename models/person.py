# -*- coding: utf-8 -*-

from odoo import models, fields, api

class ims_person(models.Model):
	_name = "ims.person"
	_description = "Person: Collects person\"s data."

	name = fields.Char(string="Name", required="true")
	surname = fields.Char(string="Surname", required="true")
	corporate_email = fields.Char(string="Email (professional)", required="true")
	personal_email = fields.Char(string="Email (personal)")
	corporate_phone = fields.Char(string="Phone (professional)")
	personal_phone = fields.Char(string="Phone (personal)")
	image = fields.Binary(string=" ") #TODO: Improve this --> empty label for image filed becasue the image widget will be used, and nocaption="1" produces side effects with the image size... Also, image export will be no avaliable with no caption...
	notes = fields.Text(string="Notes")