# -*- coding: utf-8 -*-

from odoo import models, fields, api

class ims_administrative_position(models.Model):
	_name = "ims.administrative_position"
	_description = "Administrative position: The position held by the administration staff."	
    
	name = fields.Text(string="Name", required="true")
	notes = fields.Text("Notes")

	administrative = fields.One2many(string="Administrative", comodel_name="ims.administrative", inverse_name="position")