# -*- coding: utf-8 -*-

from odoo import models, fields, api

class ims_mp(models.Model):
	_name = 'ims.mp'
	_description = 'Model de dades per a un Mòdul Professional'

	code = fields.Char('Codi')
	name = fields.Char('Nom')
	#teacher = fields.Char('Professor')
	startDate = fields.Date('Data inici')
	started = fields.Boolean('Començat')
	students = fields.Integer('Estudiants')
	image = fields.Binary('Image')
	notes = fields.Text('Anotacions')

	teacher = fields.Many2one(comodel_name="ims.teacher", string="Professor")

	ufs = fields.One2many(comodel_name="ims.uf", inverse_name="mp", string="Unitats Formatives")
	follows = fields.One2many(comodel_name="ims.follow", inverse_name="mp", string="Seguiments")