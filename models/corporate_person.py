# -*- coding: utf-8 -*-

from odoo import models, fields, api

class ims_corporate_person(models.Model):
	_name = "ims.corporate_person"
	_description = "Corporate person: Collects personal and corporative data."
	_inherit = "ims.person"
	
	corporate_email = fields.Char(string="Email (professional)", required="true")
	corporate_phone = fields.Char(string="Phone (professional)")	