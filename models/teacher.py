# -*- coding: utf-8 -*-

from odoo import models, fields, api

class ims_teacher(models.Model):
	_name = 'ims.teacher'
	_description = 'Professor que imparteix MP/UF'

	code = fields.Char('Codi')
	name = fields.Char('Nom')
	surname = fields.Char('Cognoms')
	email = fields.Char('Correu electrónic')	
	image = fields.Binary('Foto')
	notes = fields.Text('Anotacions')

	ufs = fields.One2many(comodel_name="ims.uf", inverse_name="teacher", string="Unitats Formatives")
	mps = fields.One2many(comodel_name="ims.mp", inverse_name="teacher", string="Moduls professionals")
	follows = fields.One2many(comodel_name="ims.follow", inverse_name="teacher", string="Seguiments")