# -*- coding: utf-8 -*-

from odoo import models, fields, api

class ims_space(models.Model):
	_name = "ims.space"
	_description = "Space: where each student group are assigned to."
	
	code = fields.Char(string="Numeric Code", required="true")
	name = fields.Char(string="Name", required="true")
	space_type_id = fields.Many2one(string="Type", comodel_name="ims.space_type", required="true")

