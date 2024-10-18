# -*- coding: utf-8 -*-

# import math, pytz
# from datetime import datetime, time
from odoo import models, fields, api
#from attendance_session import ims_attendance_session

class ims_attendance_session(models.Model):
	_name = 'ims.attendance_session'
	_description = 'Attendance session: contains the data about every session done with the students.'
	
	attendance_schedule_id = fields.Many2one(string="Schedule", comodel_name="ims.attendance_schedule")
	
	# NOTE: This is an statistical data model, should be unaltered if master-data changes, so the parent data will be copied.		
	weekday = fields.Selection(string="Weekday", related='attendance_schedule_id.weekday', store=True)
	start_time = fields.Float("Start Time", related='attendance_schedule_id.start_time', store=True)
	end_time = fields.Float("End Time", related='attendance_schedule_id.end_time', store=True)		
	
	teacher_id = fields.Many2one(string="Teacher", related='attendance_schedule_id.attendance_template_id.teacher_id', store=True)
	level_id = fields.Many2one(string="Level", related='attendance_schedule_id.attendance_template_id.level_id', store=True)
	study_id = fields.Many2one(string="Study", related='attendance_schedule_id.attendance_template_id.study_id', store=True)
	group_id = fields.Many2one(string="Group", related='attendance_schedule_id.attendance_template_id.group_id', store=True)
	subject_id = fields.Many2one(string="Subject", related='attendance_schedule_id.attendance_template_id.subject_id', store=True)			
	space_id = fields.Many2one(string="Space", related='attendance_schedule_id.space_id', store=True)		

	date = fields.Date(string="Date", default=fields.Datetime.now)
	notes = fields.Text('Notes')
	
	#attendance_status_ids = fields.One2many(string="Statuses", comodel_name="ims.attendance_status", inverse_name="attendance_session_id")

	# TODO: In order to speedup the development, the status will be setup as a selection, so it's single-choice (radio button) 
	#		In a near future, this should be multi-choice (checkbox) but new statuses should be allowed for customization purposes
	#		so another kind of field should be used (one2many relation BUT be aware of the BBDD registries in order to generate 
	# 		only the selected ones.).
	# status = fields.Selection(string='Status', default='1', required=True, selection=
    #     [(1, 'Attended'), (2, 'Delay'), (3, 'Miss'), (4, 'Issue')]
    # )

	

	




	# #name =fields.Char(string="Name", compute='_compute_name')
	# # date = fields.Datetime(string="Date", default=fields.Datetime.now)
	# # weekday = fields.Selection(string="Weekday", related='attendance_group.weekday') #, store=True)
	# # start_time = fields.Float(string="Start Time", related='attendance_group.start_time') #, store=True)
	# # end_time = fields.Float(string="End Time", related='attendance_group.end_time') #, store=True)
	# # start_date = fields.Datetime(string="Start date", compute="_compute_start_date", readonly=False, store=True)
	# # TODO: enddate
	# duration = fields.Integer(string="Duration", compute="_compute_duration", readonly=False, store=True)

	# notes = fields.Text(string="Notes")
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
			