# -*- coding: utf-8 -*-

from odoo import models, fields, api

class ims_space(models.Model):
	_name = "ims.space"
	_description = "Space: where each student group are assigned to."
	
	code = fields.Char(string="Numeric Code", required="true")
	name = fields.Char(string="Name", required="true")
	type = fields.Selection(string="Type", selection=[("classroom", "Classroom"), ("equipment", "Equipment"), ("laboratory", "Laboratory"), ("office", "Office"), ("workshop", "Workshop")], required="true")

