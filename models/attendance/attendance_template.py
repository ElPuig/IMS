# -*- coding: utf-8 -*-

from odoo import models, fields, api

class ims_attendance_template(models.Model):
	_name = 'ims.attendance_template'
	_description = 'Attendance template'

	start_time = fields.Float("Start Time")
	end_time = fields.Float("End Time")

	teacher = fields.Many2one(comodel_name="hr.employee", string="Professor")
	student = fields.Many2one(comodel_name="res.partner", string="Student")
	study = fields.Many2one(comodel_name="ims.study", string="Study")
	subject = fields.Many2one(comodel_name="ims.subject", string="Subject")
	level = fields.Many2one(comodel_name="ims.level", string="Level") #TODO: this should be loaded from subject
	space = fields.Many2one(comodel_name="ims.space", string="space")
	weekday = fields.Selection([
		('1', 'Monday'),
        ('2', 'Tuesday'),
        ('3', 'Wednesday'),
        ('4', 'Thursday'),
        ('5', 'Friday'),
    ])

	color = fields.Integer(string='Color', help='Field to store the color that will be used for calendar view')
    
	attendance_group = fields.Many2one(comodel_name="ims.attendance_group", string="Attendance Template Group")

	
    
    