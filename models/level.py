# -*- coding: utf-8 -*-

from odoo import models, fields, api

class ims_level(models.Model):
	_name = 'ims.level'
	_description = 'Level: Defines the studies level (University, VET, etc.).'
	
	acronym = fields.Char('Acronym')
	name = fields.Text('Name')

