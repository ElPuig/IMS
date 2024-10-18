# -*- coding: utf-8 -*-

from odoo import models, fields, api

class ims_attendance_status(models.Model):
	_name = 'ims.attendance_status'
	_description = 'Attendance status: information about session per student.'

	status = fields.Selection(string='Status', default='1', required=True, selection=
        [(1, 'Attended'), (2, 'Delay'), (3, 'Miss'), (4, 'Issue')]
    )

	#student_id = fields.Many2one(string="Student", comodel_name="res.partner", domain="[('contact_type', '=', 'student')]")
	attendance_session_id = fields.Many2one(string="Session", comodel_name="ims.attendance_session")
	
	
	
	# notes = fields.Text('Notes')
	# #TODO revisar si en lugar de un Selection debe ser un modelo status 
	# # many2many para permitir varias entradas en una misma sesión (por ejemplo incidencias)

	# #Status constants
	# CONS_ATTENDED='1'
	# CONS_MISS='2'
	# CONS_DELAY='3'

	# status = fields.Selection(
    #     [(CONS_ATTENDED, 'Attended'), (CONS_MISS, 'Miss'), (CONS_DELAY, 'Delay')],
    #     string='Status',
    #     default='1',
    #     required=True,
    # )

	# attendance_session = fields.Many2one(string="Session", comodel_name="ims.attendance_session")
	# student = fields.Many2one(comodel_name="res.partner", string="Student", domain = "[('contact_type','=','student')]")

	# def action_miss(self):
	# 	self.ensure_one()
	# 	self.status = self.CONS_MISS

	# def action_attend(self):
	# 	self.ensure_one()
	# 	self.status = self.CONS_ATTENDED

	# def action_delay(self):
	# 	self.ensure_one()
	# 	self.status = self.CONS_DELAY

	