# -*- coding: utf-8 -*-

from odoo import models, fields, api

class ims_template(models.Model):
	_name = 'ims.template'
	_description = 'Plantilla'

	start_time = fields.Datetime("Hora inici")
	end_time = fields.Datetime("Hora fi")

	teacher = fields.Many2one(comodel_name="ims.teacher", string="Professor")
	student = fields.Many2one(comodel_name="ims.student", string="Alumne")
	study = fields.Many2one(comodel_name="ims.study", string="Estudi")
	mp = fields.Many2one(comodel_name="ims.mp", string="MP")
	uf = fields.Many2one(comodel_name="ims.uf", string="UF")
	level = fields.Many2one(comodel_name="ims.level", string="Nivell")
	classroom = fields.Many2one(comodel_name="ims.classroom", string="Aula")
	

	template_group = fields.Many2one(comodel_name="ims.template_group", string="Grup de plantilles")
    

	#dades per provar la vista calendari
    
    #dia setmana
    #color


