# -*- coding: utf-8 -*-

from odoo import models, fields, api

class ims_student_group(models.Model):
	_name = "ims.student_group"
	_description = "Student Groups: Where the students are assigned to."	
	
	course = fields.Integer(string="Course", required="true")
	acronym = fields.Char(string="Acronym", required="true")
	name=fields.Char(string='Name',compute='_compute_name') #should not be edited manually
	notes = fields.Text(string="Notes")

	study = fields.Many2one(string="Study", comodel_name="ims.study", required="true")
	tutor = fields.Many2one(string="Tutor", comodel_name="ims.teacher")	
	
	# newtutor = fields.Many2one(string="New Tutor", comodel_name="hr.employee", domain="[('job_position_id', '=', 'teacher')]")
	
	delegate = fields.Many2one(string="Delegate", comodel_name="ims.student")	
	classroom = fields.Many2one(string="Classroom", comodel_name="ims.classroom")

	students = fields.One2many(string="Students", comodel_name="ims.student", inverse_name="group")
	
	@api.depends("study.acronym", "course", "acronym")
	def _compute_name(self):
		for rec in self:
			rec.name = '%s%s%s' % (rec.study.acronym, rec.course, rec.acronym)