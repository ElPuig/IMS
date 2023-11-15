# -*- coding: utf-8 -*-

from odoo import models, fields, api

class ims_level(models.Model):
	_name = "ims.level"
	_description = "Level: Defines the studies level (University, VET, etc.)."
	
	acronym = fields.Char(string="Acronym", required="true")
	name = fields.Text(string="Name", required="true")
	study_ids = fields.One2many(string="Studies", comodel_name="ims.study", inverse_name="level_id")

	notes = fields.Text(string="Notes")
