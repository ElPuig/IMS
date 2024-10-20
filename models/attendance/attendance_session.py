# -*- coding: utf-8 -*-

import math, pytz
from datetime import datetime, time
from odoo import models, fields, api
from odoo.exceptions import UserError
#from attendance_session import ims_attendance_session

class ims_attendance_session(models.Model):
	_name = "ims.attendance_session"
	_description = "Attendance session: contains the data about every session done with the students."		
	#_display_warning = fields.Boolean(compute="_default_display_warning", store=False)	
	_display_warning = fields.Boolean(default=lambda self: self._default_display_warning(), store=False)	
	
	# NOTE: This is an statistical data model, should be unaltered if master-data changes, so the parent data will be copied.		
	weekday = fields.Selection(string="Weekday", related="attendance_schedule_id.weekday", store=True)
	start_time = fields.Float("Start Time", related="attendance_schedule_id.start_time", store=True)
	end_time = fields.Float("End Time", related="attendance_schedule_id.end_time", store=True)	

	#TODO: related IDs are changing when the template changes. Should not!
	teacher_id = fields.Many2one(string="Teacher", related="attendance_schedule_id.attendance_template_id.teacher_id", store=True)
	level_id = fields.Many2one(string="Level", related="attendance_schedule_id.attendance_template_id.level_id", store=True)
	study_id = fields.Many2one(string="Study", related="attendance_schedule_id.attendance_template_id.study_id", store=True)
	group_id = fields.Many2one(string="Group", related="attendance_schedule_id.attendance_template_id.group_id", store=True)
	subject_id = fields.Many2one(string="Subject", related="attendance_schedule_id.attendance_template_id.subject_id", store=True)
	space_id = fields.Many2one(string="Space", related="attendance_schedule_id.space_id", store=True)
	
	date = fields.Date(string="Date", default=fields.Datetime.now, required=True)
	guard_mode = fields.Boolean(string= "Guard mode", default=False, store=True)
	notes = fields.Text("Notes")
	
	# TODO: Maybe UTC dates are needed? If it's the case, do as in schedule (build the dates)
	# start_date = fields.Datetime(required=True)	
	# end_date = fields.Datetime(required=True)
	
	attendance_status_ids = fields.One2many(string="Statuses", comodel_name="ims.attendance_status", inverse_name="attendance_session_id")	
	attendance_schedule_id = fields.Many2one(string="Session", comodel_name="ims.attendance_schedule", default=lambda self: self._default_attendance_schedule(), required=True)
	


	def _default_attendance_schedule(self):			
		attendance_schedule_records = self._get_attendance_schedule_records()		
		return attendance_schedule_records[0] if len(attendance_schedule_records) == 1 else False				

	def _default_display_warning(self):						
		attendance_schedule_records = self._get_attendance_schedule_records()
		return (self.id == False and len(attendance_schedule_records) != 1)
	
	def _get_attendance_schedule_records(self):		
		today = datetime.now()		
		return self.env["ims.attendance_schedule"].search([("weekday", "=", today.weekday()), ("start_date", "<=", today), ("end_date", ">=", today)])

	# @api.depends("attendance_schedule_id")
	# def _default_display_warning(self):		
	# 	for rec in self:			
	# 		today = datetime.now()		
	# 		attendance_schedule_records = self.env["ims.attendance_schedule"].search([("weekday", "=", today.weekday()), ("start_date", "<=", today), ("end_date", ">=", today)])
	# 		rec._display_warning=("NewId" in str(rec.id) and len(attendance_schedule_records) != 1)

	@api.onchange("guard_mode")
	def _onchange_guard_mode(self):		
		return {'domain': {'attendance_schedule_id': "[]" if self.guard_mode else "[('attendance_template_id.teacher_id.user_id', '=', uid)]"}}

	@api.onchange("attendance_schedule_id")	
	def _onchange_attendance_schedule_id(self):		
		for rec in self:
			students = []
			
			for attendance_status in rec.attendance_status_ids:
				# Unlink previous students
				students.append([3, attendance_status.id])

			for student in rec.attendance_schedule_id.attendance_template_id.student_ids:
				# Sources: 
				# 	https://stackoverflow.com/a/70843263
				#	https://www.odoo.com/ro_RO/forum/suport-1/how-to-insert-value-to-a-one2many-field-in-table-with-create-method-28714
				
				# Linking new students
				students.append([0, 0, {
					"student_id": student
				}])	

			self.write({"attendance_status_ids": students})

	def name_get(self):
        #Allows displaying a custom name: https://www.odoo.com/documentation/16.0/es/developer/reference/backend/orm.html#odoo.models.Model.name_get
		result = []	
		for rec in self:
			result.append((rec.id, "%s | %s" % (rec.attendance_schedule_id.name_get()[0][1], rec.date)))			
			
		return result


	def convert_to_utc_date(self, local_date):
		user_time_zone = self.env.context["tz"] # can be fetched form logged in user if it is set 
		local = pytz.timezone(user_time_zone) 
		start_date = local.localize(local_date, is_dst=None) # start_date is a naive datetime 
		start_date = start_date.astimezone(pytz.utc) 
		
		return datetime(start_date.year, start_date.month, start_date.day, start_date.hour, start_date.minute, 0, tzinfo=None)








	# #name =fields.Char(string="Name", compute="_compute_name")
	# # date = fields.Datetime(string="Date", default=fields.Datetime.now)
	# # weekday = fields.Selection(string="Weekday", related="attendance_group.weekday") #, store=True)
	# # start_time = fields.Float(string="Start Time", related="attendance_group.start_time") #, store=True)
	# # end_time = fields.Float(string="End Time", related="attendance_group.end_time") #, store=True)
	# # start_date = fields.Datetime(string="Start date", compute="_compute_start_date", readonly=False, store=True)
	# # TODO: enddate
	# duration = fields.Integer(string="Duration", compute="_compute_duration", readonly=False, store=True)

	# notes = fields.Text(string="Notes")
	# attendance_group = fields.Many2one(string="Attendance Group", comodel_name="ims.attendance_group")

	# attendance_statuses = fields.One2many(string="Student status", comodel_name="ims.attendance_status", inverse_name="attendance_session")		
	# has_statuses = fields.Boolean(compute="_compute_has_statuses", store=False)	
	# # event_color = fields.Integer("Color", compute="computeColor")

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


	# # @api.depends("date")
	# # def _compute_date(self):
	# # 	for record in self:
	# # 		record.start_date = record.date
	# # 		record.end_date = record.date

	# def convert_to_utc_date(self, local_date):
	# 	user_time_zone = self.env.context["tz"] # can be fetched form logged in user if it is set 
	# 	local = pytz.timezone(user_time_zone) 
	# 	start_date = local.localize(local_date, is_dst=None) # start_date is a naive datetime 
	# 	start_date = start_date.astimezone(pytz.utc) 
		
	# 	return datetime(start_date.year, start_date.month, start_date.day, start_date.hour, start_date.minute, 0, tzinfo=None)

	# @api.depends("attendance_statuses")
	# def _compute_has_statuses(self):
	# 	for record in self:
	# 		record.has_statuses = len(record.attendance_statuses) > 0

	# def generate_statuses_by_templates (self):
	# 	for contact in self.attendance_group.attendance_templates.student:
	# 		status = self.env["ims.attendance_status"].create({
	# 			"attendance_session": self.id,
	# 			"student" : contact.id,
	# 			"status" : "1"
	# 		})

	# def generate_statuses (self, session):
	# 	for contact in self.attendance_group.attendance_templates.student:
	# 		status = self.env["ims.attendance_status"].create({
	# 			"attendance_session": self.id,
	# 			"student" : contact.id,
	# 			"status" : "1"
	# 		})
			