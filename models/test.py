# -*- coding: utf-8 -*-

from odoo import models, fields, api

class ims_level(models.Model):
	_name = 'ims.test'
	_description = 'Clase para pruebas'
	
	acronym = fields.Char('Acronym')
	name = fields.Text('Name')
	color = fields.Char(string='Color', help='Field to store the color that will be used for calendar view', default='#FFFFFF')

