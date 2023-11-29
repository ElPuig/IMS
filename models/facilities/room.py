# -*- coding: utf-8 -*-

from odoo import models, fields, api

class ims_room(models.Model):
	_name = "ims.room"
	_description = "Room: where each student group are assigned to."
	
	code = fields.Char(string="Numeric Code", required="true")
	name = fields.Char(string="Name", required="true")
	type = fields.Selection(string="Type", selection=[("Classroom", "classroom"), ("Equipment", "equipment"), ("Office", "office")], required="true")

