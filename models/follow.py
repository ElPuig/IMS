# -*- coding: utf-8 -*-

from odoo import models, fields, api

class ims_follow(models.Model):
	_name = 'ims.follow'
	_description = 'Seguiment'
	
	notes = fields.Text('Anotacions')

	teacher = fields.Many2one(comodel_name="ims.teacher", string="Professor")
	student = fields.Many2one(comodel_name="ims.student", string="Alumne")
	study = fields.Many2one(comodel_name="ims.study", string="Estudi")
	mp = fields.Many2one(comodel_name="ims.mp", string="MP")
	uf = fields.Many2one(comodel_name="ims.uf", string="UF")

