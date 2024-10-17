# -*- coding: utf-8 -*-

import math, pytz
from datetime import datetime, time
from odoo import models, fields, api

class ims_attendance_schedule(models.Model):
	_name = 'ims.attendance_schedule'
	_description = 'Attendance schedule: concretes the weekdays data.'
	
	weekday = fields.Selection(string="Weekday", selection=[
		('1', 'Monday'),
        ('2', 'Tuesday'),
        ('3', 'Wednesday'),
        ('4', 'Thursday'),
        ('5', 'Friday'),
    ])

	start_time = fields.Float("Start Time")
	end_time = fields.Float("End Time")
	space_id = fields.Many2one(string="Space", comodel_name="ims.space")	# TODO: autofill by template (allow changes)
	attendance_template_id = fields.Many2one(string="Template", comodel_name="ims.attendance_template")
	#attendance_instance_ids = fields.One2many(string="Instances", comodel_name="ims.attendance_instance", inverse_name="attendance_session_id")		
	notes = fields.Text(string="Notes")




	# #name =fields.Char(string="Name", compute='_compute_name')
	# # date = fields.Datetime(string="Date", default=fields.Datetime.now)
	# # weekday = fields.Selection(string="Weekday", related='attendance_group.weekday') #, store=True)
	# # start_time = fields.Float(string="Start Time", related='attendance_group.start_time') #, store=True)
	# # end_time = fields.Float(string="End Time", related='attendance_group.end_time') #, store=True)
	# # start_date = fields.Datetime(string="Start date", compute="_compute_start_date", readonly=False, store=True)
	# # TODO: enddate
	# duration = fields.Integer(string="Duration", compute="_compute_duration", readonly=False, store=True)

	
	# attendance_group = fields.Many2one(string="Attendance Group", comodel_name="ims.attendance_group")

	# attendance_statuses = fields.One2many(string="Student status", comodel_name="ims.attendance_status", inverse_name="attendance_session")		
	# has_statuses = fields.Boolean(compute='_compute_has_statuses', store=False)	
	# # event_color = fields.Integer("Color", compute='computeColor')

	# # def computeColor(self):
	# # 	for record in self:
	# # 		record.name = record.attendance_group.color
	
	# def _compute_name(self):
	# 	for record in self:
	# 		record.name = record.attendance_group.subject.acronym

	# @api.depends("date", "start_time")
	# def _compute_start_date(self):			
	# 	for rec in self:
	# 		#Computing the start date
	# 		start_time = math.modf(rec.start_time)				
	# 		local_time = datetime(rec.date.year, rec.date.month, rec.date.day, int(start_time[1]), int(start_time[0]*10), 0)
	# 		rec.start_date = self.convert_to_utc_date(local_time)


	# # @api.depends('date')
	# # def _compute_date(self):
	# # 	for record in self:
	# # 		record.start_date = record.date
	# # 		record.end_date = record.date

	# def convert_to_utc_date(self, local_date):
	# 	user_time_zone = self.env.context['tz'] # can be fetched form logged in user if it is set 
	# 	local = pytz.timezone(user_time_zone) 
	# 	start_date = local.localize(local_date, is_dst=None) # start_date is a naive datetime 
	# 	start_date = start_date.astimezone(pytz.utc) 
		
	# 	return datetime(start_date.year, start_date.month, start_date.day, start_date.hour, start_date.minute, 0, tzinfo=None)

	# @api.depends('attendance_statuses')
	# def _compute_has_statuses(self):
	# 	for record in self:
	# 		record.has_statuses = len(record.attendance_statuses) > 0

	# def generate_statuses_by_templates (self):
	# 	for contact in self.attendance_group.attendance_templates.student:
	# 		status = self.env['ims.attendance_status'].create({
	# 			'attendance_session': self.id,
	# 			'student' : contact.id,
	# 			'status' : '1'
	# 		})

	# def generate_statuses (self, session):
	# 	for contact in self.attendance_group.attendance_templates.student:
	# 		status = self.env['ims.attendance_status'].create({
	# 			'attendance_session': self.id,
	# 			'student' : contact.id,
	# 			'status' : '1'
	# 		})
			