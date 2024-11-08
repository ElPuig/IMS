# -*- coding: utf-8 -*-

from odoo import models, fields, api
from odoo.exceptions import ValidationError

class ims_group(models.Model):
	_name = "ims.group"
	_description = "Groups: Where the students are assigned to."	
	
	course = fields.Integer(string="Course", required="true")
	acronym = fields.Char(string="Acronym", required="true")
	name = fields.Char(string="Name", compute="_compute_name", store=True) #should not be edited manually
	notes = fields.Text(string="Notes")

	study_id = fields.Many2one(string="Study", comodel_name="ims.study", required="true")
	tutor_id = fields.Many2one(string="Tutor", comodel_name="hr.employee", domain="[('employee_type', '=', 'teacher')]")
	
	delegate_id = fields.Many2one(string="Delegate", comodel_name="res.partner", domain="[('contact_type', '=', 'student')]")	
	space_id = fields.Many2one(string="Classroom", comodel_name="ims.space")
	
	main_student_ids = fields.One2many(string="Students (main group)", comodel_name="res.partner", inverse_name="main_group_id", domain="[('contact_type', '=', 'student')]") #, readonly=True		
	enrolled_student_ids = fields.Many2many(string="Students (enrolled)", comodel_name="res.partner", compute="_compute_enrolled_student_ids") # TODO: should be store=True in order to allow search on view, but nothing displays... https://www.odoo.com/es_ES/forum/ayuda-1/filter-and-group-by-for-many2many-fields-how-to-do-that-151888

	@api.depends("study_id.acronym", "course", "acronym")
	def _compute_name(self):
		for rec in self:
			#TODO: validate the uniqueness
			rec.name = "%s%s%s" % (rec.study_id.acronym, rec.course, rec.acronym)

	def _compute_enrolled_student_ids(self):			
		for rec in self:			
			rec.enrolled_student_ids = self.env["ims.enrollment"].search([("group_id", "=", rec.id)]).mapped("student_id")