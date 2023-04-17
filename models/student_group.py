# -*- coding: utf-8 -*-

from odoo import models, fields, api

class ims_student_group(models.Model):
	_name = 'ims.student_group'
	_description = 'Grup alumnes'

	code = fields.Char('Codi')
	name = fields.Char('Nom')
	email = fields.Char('Correu electrónic')	
	notes = fields.Text('Anotacions')

	students = fields.One2many(comodel_name="ims.student", inverse_name="student_group", string="Alumnes")