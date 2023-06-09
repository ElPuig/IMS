# -*- coding: utf-8 -*-

from odoo import models, fields, api

class ims_template(models.Model):
	_name = 'ims.template'
	_description = 'Template'

	start_time = fields.Datetime("Start time")
	end_time = fields.Datetime("End time")

	teacher = fields.Many2one(comodel_name="ims.teacher", string="Teacher")
	student = fields.Many2one(comodel_name="ims.student", string="Student")
	level = fields.Many2one(comodel_name="ims.level", string="Level")
	studies = fields.Many2one(comodel_name="ims.study", string="Studies")
	professional_module = fields.Many2one(comodel_name="ims.professional_module", string="Professional Module")
	formative_unit = fields.Many2one(comodel_name="ims.formative_unit", string="Formative Unit")	
	classroom = fields.Many2one(comodel_name="ims.classroom", string="Classroom")	
	
	template_group = fields.Many2one(comodel_name="ims.template_group", string="Template group")
    

	#dades per provar la vista calendari
    
    #dia setmana
    #color


