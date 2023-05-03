# -*- coding: utf-8 -*-

from odoo import models, fields, api

class ims_level(models.Model):
	_name = 'ims.level'
	_description = 'Nivell'
	
	code = fields.Text('Codi')
	name = fields.Text('Nom')

