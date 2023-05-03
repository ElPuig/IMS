# -*- coding: utf-8 -*-

from odoo import models, fields, api

class ims_classroom(models.Model):
	_name = 'ims.classroom'
	_description = 'Aula'
	
	code = fields.Text('Codi')
	name = fields.Text('Nom')

