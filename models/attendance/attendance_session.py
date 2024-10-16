# -*- coding: utf-8 -*-

from odoo import models, fields, api

class ims_attendance_session(models.Model):
	_name = 'ims.attendance_session'
	_description = 'Every concrete class session'
	
	date = fields.Datetime(string="Date", default = fields.Datetime.now)
	duration = fields.Integer(string="Duration", default = 60)
	# end_time = fields.Float("End Time", default=lambda self: self.attendance_group.end_time)
	notes = fields.Text('Notes')

	attendance_group = fields.Many2one(comodel_name="ims.attendance_group", string="Attendance Group")

	group = fields.Many2one(comodel_name="ims.group", string="Grup")	
	attendance_statuses = fields.One2many(comodel_name="ims.attendance_status", inverse_name="attendance_session", string="Student status")

	hasStatuses = fields.Boolean(compute='_compute_has_statuses', store=False)
	date_start = fields.Datetime(string="date_start", compute='_compute_date')
	date_stop = fields.Datetime(string="date_stop", compute='_compute_date')
	name =fields.Char(string="name", compute='_compute_name')
	# event_color = fields.Integer("Color", compute='computeColor')

	# def computeColor(self):
	# 	for record in self:
	# 		record.name = record.attendance_group.color
	
	def _compute_name(self):
		for record in self:
			record.name = record.attendance_group.subject.acronym

	@api.depends('date')
	def _compute_date(self):
		for record in self:
			record.date_start = record.date
			record.date_stop = record.date

	@api.depends('attendance_statuses')
	def _compute_has_statuses(self):
		for record in self:
			record.hasStatuses = len(record.attendance_statuses) > 0

	def generate_statuses_by_templates (self):
		for contact in self.attendance_group.attendance_templates.student:
			status = self.env['ims.attendance_status'].create({
				'attendance_session': self.id,
				'student' : contact.id,
				'status' : '1'
			})

	def generate_statuses (self, session):
		for contact in self.attendance_group.attendance_templates.student:
			status = self.env['ims.attendance_status'].create({
				'attendance_session': self.id,
				'student' : contact.id,
				'status' : '1'
			})
			