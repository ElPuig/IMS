# -*- coding: utf-8 -*-

from odoo import models, fields, api

class ims_group(models.Model):
	_name = "ims.group"
	_description = "Groups: Where the students are assigned to."	
	
	course = fields.Integer(string="Course", required="true")
	acronym = fields.Char(string="Acronym", required="true")
	name=fields.Char(string='Name',compute='_compute_name') #should not be edited manually
	notes = fields.Text(string="Notes")

	study_id = fields.Many2one(string="Study", comodel_name="ims.study", required="true")
	tutor_id = fields.Many2one(string="Tutor", comodel_name="hr.employee", domain="[('employee_type', '=', 'teacher')]")
	
	delegate_id = fields.Many2one(string="Delegate", comodel_name="res.partner", domain="[('contact_type', '=', 'student')]")	
	room_id = fields.Many2one(string="room", comodel_name="ims.room")

	student_ids = fields.One2many(string="Students", comodel_name="res.partner", inverse_name="main_group_id", domain="[('contact_type', '=', 'student')]")	
	
	@api.depends("study_id.acronym", "course", "acronym")
	def _compute_name(self):
		for rec in self:
			rec.name = '%s%s%s' % (rec.study_id.acronym, rec.course, rec.acronym)