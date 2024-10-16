# -*- coding: utf-8 -*-

import datetime, pytz
from odoo import models, fields, api
import datetime

class ims_attendance_group(models.Model):
	_name = 'ims.attendance_group'
	_description = 'Attendance templates linked to a student group that allows template batch generation'
	_inherit = 'ims.attendance_template'
	
	name = fields.Char(compute='compute_name', string="Name")

	group = fields.Many2one(comodel_name="ims.group", string="Grup")	
	attendance_templates = fields.One2many(comodel_name="ims.attendance_template", inverse_name="attendance_group", string="Templates")
	attendance_sessions = fields.One2many(comodel_name="ims.attendance_session", inverse_name="attendance_group", string="Sessions")

	hasTemplates = fields.Boolean(compute='compute_hasTemplates', store=False)

	@api.depends('attendance_templates')
	def compute_hasTemplates(self):
		for record in self:
			record.hasTemplates = len(record.attendance_templates) > 0

	@api.depends('group')
	def compute_name(self):
		for record in self:
			# TODO: Pulir la generación del nombre
			record.name = "-".join([record.group.name, record.subject.name, record.weekday, str(record.start_date.time())])

	# TODO: Rename to GenerateTemplatesByGroup
	# TODO: Create GenerateTemplatesByEnrollment method or GenerateAllTemplates (group+enrollment)
	def GenerateTemplatesByStudent (self):
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
	
	def GenerateNextSession (self): #Generate next session with related attendances
		weekday = int(self.weekday)
		lastSessionDate = self.getLatestSessionDateTime()
		newSession = self.env['ims.attendance_session'].create({
			'date': self.nextDateByWeekday(weekday, lastSessionDate),
			'duration': self.duration,
			'attendance_group': self.id,
			'group': self.group.id
		})

		newSession.GenerateStatuses(newSession)
		


	def nextDateByWeekday (self, weekday, lastSessionDate):
		currentWeekday = lastSessionDate.weekday() + 1  #Counting monday as 1
		daysUntil = (weekday - currentWeekday + 7) % 7
		if daysUntil <= 0:
			daysUntil += 7
		nextDate = (lastSessionDate + datetime.timedelta(days=daysUntil))
		nextDate = self.addHourToDate(nextDate)

		return nextDate
	
	def addHourToDate(self, date):				
		hora = self.start_date.hour
		minuto = self.start_date.minute
		segundo = self.start_date.second

		date = datetime.datetime(date.year, date.month, date.day, hora, minuto, segundo, tzinfo=None)

		return date
	
	
	def getLatestSessionDateTime (self):
		lastSessionDateTime = datetime.datetime.today() - datetime.timedelta(days=1)
		lastSession = self.env['ims.attendance_session'].search(
			[('attendance_group', '=', self.id)], order='date desc', limit=1)
		if lastSession:
			lastSessionDateTime = lastSession.date
				
		return lastSessionDateTime
