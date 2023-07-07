# -*- coding: utf-8 -*-

#TODO: remove or rename to 'attendance_template'
from odoo import models, fields, api

class ims_template_group(models.Model):
	_name = 'ims.template_group'
	_description = 'Template groups'
	_inherit = 'ims.template'

	group = fields.Many2one(comodel_name="ims.group", string="Group")
	
	templates = fields.One2many(comodel_name="ims.template", inverse_name="template_group", string="Group templates")

	weekday = fields.Selection([
        ('1', 'Monday'),
        ('2', 'Tuesday'),
        ('3', 'Wednesday'),
        ('4', 'Thursday'),
        ('5', 'Friuday'),
    ], string='Week day')
    
    #color #TODO millorar el selector de color amb un que realment seleccionis el color
	color = fields.Selection([
        ('1', 'Blue'),
        ('2', 'Green'),
        ('3', 'Red'),
        ('4', 'Yellow'),
        ('5', 'Orange'),
    ], string='Color')

