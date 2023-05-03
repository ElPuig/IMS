# -*- coding: utf-8 -*-

from odoo import models, fields, api

class ims_template_group(models.Model):
	_name = 'ims.template_group'
	_description = 'Grup de plantilles'
	_inherit = 'ims.template'

	student_group = fields.Many2one(comodel_name="ims.student_group", string="Grup")
	
	templates = fields.One2many(comodel_name="ims.template", inverse_name="template_group", string="Plantilles grup")

	weekday = fields.Selection([
        ('1', 'Lunes'),
        ('2', 'Martes'),
        ('3', 'Miércoles'),
        ('4', 'Jueves'),
        ('5', 'Viernes'),
    ], string='Dia de la setmana')
    
    #color #TODO millorar el selector de color amb un que realment seleccionis el color
	color = fields.Selection([
        ('1', 'Blau'),
        ('2', 'Verd'),
        ('3', 'Vermell'),
        ('4', 'Groc'),
        ('5', 'Taronja'),
    ], string='Color')

