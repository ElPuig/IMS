# -*- coding: utf-8 -*-

from odoo import models, fields, api

class ims_administrative(models.Model):
	_name = "ims.administrative"
	_description = "Administrative person: Collects personal and corporative data."
	_inherit = "ims.corporate_person"
    
	role = fields.Many2one(string="Position", comodel_name="ims.administrative_role")