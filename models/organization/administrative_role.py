# -*- coding: utf-8 -*-

from odoo import models, fields, api

class ims_administrative_role(models.Model):
	_name = "ims.administrative_role"
	_description = "Administrative position: The position held by the administration staff."	
    
	name = fields.Text(string="Name", required="true")
	notes = fields.Text("Notes")

	administratives = fields.One2many(string="Administrative", comodel_name="ims.administrative", inverse_name="role")