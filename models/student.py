# -*- coding: utf-8 -*-

from odoo import models, fields, api

class ims_student(models.Model):
	_name = 'ims.student'
	_description = 'Alumne'

	code = fields.Char('Codi')
	name = fields.Char('Nom')
	surname = fields.Char('Cognoms')
	email = fields.Char('Correu electrónic')	
	image = fields.Binary('Foto')
	notes = fields.Text('Anotacions')

	student_group = fields.Many2one(comodel_name="ims.student_group", string="Grup")

	follows = fields.One2many(comodel_name="ims.follow", inverse_name="student", string="Seguiments")