# -*- coding: utf-8 -*-

import datetime, pytz
from odoo import models, fields, api
import datetime

class ims_attendance_group(models.Model):
	_name = 'ims.attendance_group'
	_description = 'Attendance templates linked to a student group that allows template batch generation'
	_inherit = 'ims.attendance_template'
	
	name = fields.Char(string="Name", compute='_compute_name')

	group = fields.Many2one(comodel_name="ims.group", string="Grup")	
	attendance_templates = fields.One2many(string="Templates", comodel_name="ims.attendance_template", inverse_name="attendance_group")
	attendance_sessions = fields.One2many(string="Sessions", comodel_name="ims.attendance_session", inverse_name="attendance_group")
	has_templates = fields.Boolean(compute='_compute_has_templates', store=False)

	@api.depends('attendance_templates')
	def _compute_has_templates(self):
		for record in self:
			record.has_templates = len(record.attendance_templates) > 0

	@api.depends('group')
	def _compute_name(self):
		for record in self:
			# TODO: Pulir la generación del nombre
			record.name = "-".join([record.group.name, record.subject.name, record.weekday, str(record.end_date.time())])

	# TODO: Rename to GenerateTemplatesByGroup
	# TODO: Create GenerateTemplatesByEnrollment method or GenerateAllTemplates (group+enrollment)
	def generate_templates_by_student (self):
		for student in self.group.enrolled_student_ids:			
			template = self.env['ims.attendance_template'].create({
				'teacher': self.teacher.id,
				'study': self.study.id,
				'student': student.id,
				'subject': self.subject.id,
				'level': self.level.id,
				'classroom': self.classroom.id,
				'weekday': self.weekday,
				'color': self.color,
				'attendance_group': self.id
			})
	
	def generate_next_session (self): #Generate next session with related attendances
		weekday = int(self.weekday)
		lastSessionDate = self.get_latest_session_date_time()
		newSession = self.env['ims.attendance_session'].create({
			'date': self.next_date_by_weekday(weekday, lastSessionDate),
			'duration': self.duration,
			'attendance_group': self.id,
			'group': self.group.id
		})
		newSession.generate_statuses(newSession)

	def next_date_by_weekday (self, weekday, lastSessionDate):
		currentWeekday = lastSessionDate.weekday() + 1  #Counting monday as 1
		daysUntil = (weekday - currentWeekday + 7) % 7
		if daysUntil <= 0:
			daysUntil += 7
		nextDate = (lastSessionDate + datetime.timedelta(days=daysUntil))
		nextDate = self.add_hour_to_date(nextDate)
		return nextDate
	
	def add_hour_to_date(self, date):				
		hora = self.end_date.hour
		minuto = self.end_date.minute
		segundo = self.end_date.second
		date = datetime.datetime(date.year, date.month, date.day, hora, minuto, segundo, tzinfo=None)
		return date
	
	def get_latest_session_date_time (self):
		lastSessionDateTime = datetime.datetime.today() - datetime.timedelta(days=1)
		lastSession = self.env['ims.attendance_session'].search(
			[('attendance_group', '=', self.id)], order='date desc', limit=1)
		if lastSession:
			lastSessionDateTime = lastSession.date
		return lastSessionDateTime
