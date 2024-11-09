# -*- coding: utf-8 -*-

from odoo import models, fields, api
from odoo.exceptions import UserError

class ims_group(models.Model):
	_name = "ims.group"
	_description = "Groups: Where the students are assigned to."	
	
	course = fields.Integer(string="Course", required="true")
	acronym = fields.Char(string="Acronym", required="true")
	name = fields.Char(string="Name", compute="_compute_name", store=True) #should not be edited manually
	notes = fields.Text(string="Notes")

	study_id = fields.Many2one(string="Study", comodel_name="ims.study", required="true")
	tutor_id = fields.Many2one(string="Tutor", comodel_name="hr.employee", domain="[('employee_type', '=', 'teacher')]")
	
	delegate_id = fields.Many2one(string="Delegate", comodel_name="res.partner", domain="[('contact_type', '=', 'student'), ('main_group_id', '=', id)]")	
	space_id = fields.Many2one(string="Classroom", comodel_name="ims.space")
	
	main_student_ids = fields.One2many(string="Students", comodel_name="res.partner", inverse_name="main_group_id", domain="[('contact_type', '=', 'student')]")
	enrolled_student_ids = fields.Many2many(string="Enrolled", comodel_name="res.partner", compute="_compute_enrolled_student_ids") 	
	transient_enrollment_ids = fields.One2many(string="Enrollment", comodel_name="ims.transient_enrollment", inverse_name="group_id", compute="_compute_enrollment_ids") # Contains the same data as enrolled_student_ids but filtered for the current group (sadly, it cannot be filtered on view...)

	@api.depends("study_id.acronym", "course", "acronym")
	def _compute_name(self):
		for rec in self:
			#TODO: validate the uniqueness
			rec.name = "%s%s%s" % (rec.study_id.acronym, rec.course, rec.acronym)

	def _compute_enrolled_student_ids(self):			
		for rec in self:			
			rec.enrolled_student_ids = self.env["ims.enrollment"].search([("group_id", "=", rec.id)]).mapped("student_id") or False

	def _compute_enrollment_ids(self):					
		self.env['ims.transient_enrollment'].search([('group_id', '=', self.id)]).unlink()
		for rec in self:				
			#Sources: 
			# 	https://www.odoo.com/documentation/16.0/developer/reference/backend/orm.html?highlight=read_group#search-read
			#	https://www.cybrosys.com/odoo/odoo-books/odoo-15-development/ch15/grouped-data/	
			for student in self.env['ims.enrollment'].read_group(domain=[('group_id', '=', rec.id)], fields=['student_id'], groupby=['student_id']):	
				sid = student['student_id'][0]	
				subs = self.env["ims.enrollment"].search([("group_id", "=", rec.id), ('student_id', '=', sid)]).mapped("subject_id")
				
				# Source: https://www.odoo.com/fi_FI/forum/apua-1/how-to-insert-value-to-a-one2many-field-in-table-with-create-method-28714
				rec.transient_enrollment_ids.create({
					"group_id": rec.id,
					"student_id": sid,
					"subject_ids": subs,					
				})				

class ims_transient_enrollment(models.TransientModel):
	_name = "ims.transient_enrollment"
	_description = "Transitient model for displaying enrollment data within groups but filtered (allows ims.group.transient_enrollment_ids to work: contains the same data as enrolled_student_ids but filtered for the current group because it cannot be filtered on view...)."
	
	group_id = fields.Many2one(comodel_name="ims.group")
	student_id = fields.Many2one(comodel_name="res.partner")
	subject_ids = fields.Many2many(comodel_name="ims.subject")	
	image_1920 = fields.Binary(string="Image", related='student_id.image_1920')

