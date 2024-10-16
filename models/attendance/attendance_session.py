# -*- coding: utf-8 -*-

from odoo import models, fields, api

class ims_attendance_session(models.Model):
	_name = 'ims.attendance_session'
	_description = 'Every concrete class session'
	
	name =fields.Char(string="Name", compute='_compute_name')
	date = fields.Datetime(string="Date", default=fields.Datetime.now)
	start_date = fields.Datetime(string="Start date", compute='_compute_date')
	end_date = fields.Datetime(string="End date", compute='_compute_date')

	duration = fields.Integer(string="Duration", default = 60)
	# end_time = fields.Float("End Time", default=lambda self: self.attendance_group.end_time)
	notes = fields.Text(string="Notes")

	attendance_group = fields.Many2one(string="Attendance Group", comodel_name="ims.attendance_group")

	group = fields.Many2one(string="Grup", comodel_name="ims.group")	
	attendance_statuses = fields.One2many(string="Student status", comodel_name="ims.attendance_status", inverse_name="attendance_session")
		
	has_statuses = fields.Boolean(compute='_compute_has_statuses', store=False)	
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
			record.start_date = record.date
			record.end_date = record.date

	@api.depends('attendance_statuses')
	def _compute_has_statuses(self):
		for record in self:
			record.has_statuses = len(record.attendance_statuses) > 0

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
			