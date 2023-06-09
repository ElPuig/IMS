# -*- coding: utf-8 -*-

from odoo import models, fields, api

class ims_classroom(models.Model):
	_name = 'ims.classroom'
	_description = 'Classroom'
	
	code = fields.Text('Numeric Code')
	name = fields.Text('Name')

