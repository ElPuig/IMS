# -*- coding: utf-8 -*-

from odoo import models, fields, api

class ims_administrative(models.Model):
	_name = "ims.administrative"
	_description = "Administrative person: Collects personal and corporative data."
	_inherit = "ims.corporate_person"
    
	type = fields.Selection(string='Type', selection=[('canteen', 'Canteen'), ('concierje', 'Concierje'), ('cleaning', 'Cleaning'), ('it', 'IT'), ('maintainment', 'Maintainment'), ('secretary', 'Secretary')], required="true")