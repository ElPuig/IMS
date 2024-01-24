# -*- coding: utf-8 -*-

from odoo import models, fields, api

class ims_attendance_template(models.Model):
	_name = 'ims.attendance_template'
	_description = 'Attendance template'

	start_date = fields.Datetime(string="Date", default = fields.Datetime.now)
	duration = fields.Integer(string="Duration", default = 60)
	# start_time = fields.Float("Start Time")
	# end_time = fields.Float("End Time")

	teacher = fields.Many2one(comodel_name="ims.teacher", string="Professor")
	student = fields.Many2one(comodel_name="ims.student", string="Student")
	study = fields.Many2one(comodel_name="ims.study", string="Study")
	mp = fields.Many2one(comodel_name="ims.professional_module", string="Professional Module")
	uf = fields.Many2one(comodel_name="ims.formative_unit", string="Formative Unit")
	level = fields.Many2one(comodel_name="ims.level", string="Level")
	classroom = fields.Many2one(comodel_name="ims.classroom", string="Classroom")
	weekday = fields.Selection([
		('1', 'Monday'),
        ('2', 'Tuesday'),
        ('3', 'Wednesday'),
        ('4', 'Thursday'),
        ('5', 'Friday'),
    ])

	color = fields.Integer(string='Color', help='Field to store the color that will be used for calendar view')
    
	attendance_group = fields.Many2one(comodel_name="ims.attendance_group", string="Attendance Template Group")

	
    
    