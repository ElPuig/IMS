# -*- coding: utf-8 -*-

from odoo import models, fields, api

class ims_attendance_status(models.Model):
	_name = 'ims.attendance_status'
	_description = 'Attendance status per student/session'
	
	notes = fields.Text('Notes')
	#TODO revisar si en lugar de un Selection debe ser un modelo status 
	# many2many para permitir varias entradas en una misma sesión (por ejemplo incidencias)
	status = fields.Selection(
        [('1', 'Attended'), ('2', 'Miss'), ('3', 'Delay')],
        string='Status',
        default='1',
        required=True,
    )

	attendance_session = fields.Many2one(comodel_name="ims.attendance_session", string="Session")
	student = fields.Many2one(comodel_name="ims.student", string="Student")

	