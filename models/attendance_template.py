# -*- coding: utf-8 -*-

from odoo import models, fields, api

class ims_attendance_template(models.Model):
	_name = 'ims.attendance_template'
	_description = 'Attendance template'

	start_time = fields.Datetime("Start Time")
	end_time = fields.Datetime("End Time")

	teacher = fields.Many2one(comodel_name="ims.teacher", string="Professor")
	student = fields.Many2one(comodel_name="ims.student", string="Student")
	study = fields.Many2one(comodel_name="ims.study", string="Study")
	mp = fields.Many2one(comodel_name="ims.professional_module", string="Professional Module")
	uf = fields.Many2one(comodel_name="ims.formative_unity", string="Formative Unitiy")
	level = fields.Many2one(comodel_name="ims.level", string="Level")
	classroom = fields.Many2one(comodel_name="ims.classroom", string="Classroom")
	weekday = fields.Selection([
		('1', 'Monday'),
        ('2', 'Tuesday'),
        ('3', 'Wednesday'),
        ('4', 'Thursday'),
        ('5', 'Friday'),
    ])
    #TODO millorar el selector de color amb un que realment seleccionis el color
	#Color will be used in the calendar view
	color = fields.Selection([
        ('1', 'Blau'),
        ('2', 'Verd'),
        ('3', 'Vermell'),
        ('4', 'Groc'),
        ('5', 'Taronja'),
    ], string='Color')
    

	attendance_group = fields.Many2one(comodel_name="ims.attendance_group", string="Attendance Template Group")

	
    
    