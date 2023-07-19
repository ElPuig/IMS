# -*- coding: utf-8 -*-

from odoo import models, fields, api

class ims_attendance_group(models.Model):
	_name = 'ims.attendance_group'
	_description = 'Attendance templates linked to a student group that allows template batch generation'
	_inherit = 'ims.attendance_template'

	student_group = fields.Many2one(comodel_name="ims.group", string="Grup")
	
	attendance_templates = fields.One2many(comodel_name="ims.attendance_template", inverse_name="attendance_group", string="Template group")

	weekday = fields.Selection([
        ('1', 'Monday'),
        ('2', 'Tuesday'),
        ('3', 'Wednesday'),
        ('4', 'Thursday'),
        ('5', 'Friday'),
    ], string='Weekday')