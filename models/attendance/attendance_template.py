# -*- coding: utf-8 -*-

from odoo import models, fields, api

class ims_attendance_template(models.Model):
	_name = "ims.attendance_template"
	_description = "Attendance template: contains the basic attendance data (who teaches what, where and for whom)"

	# TODO: add a start_date and an end_date. It will be used to select the current data when creating a new session.
	start_date = fields.Date(string="Start date", required=True)
	end_date = fields.Date(string="End date", required=True)
	color = fields.Integer(string="Color", help="Field to store the color that will be used for calendar view")   

	teacher_id = fields.Many2one(string="Teacher", comodel_name="hr.employee", domain="[('employee_type', '=', 'teacher')]", required=True)
	level_id = fields.Many2one(string="Level", comodel_name="ims.level", required=True)
	study_id = fields.Many2one(string="Study", comodel_name="ims.study", domain="[('level_id', '=', level_id)]", required=True)
	group_id = fields.Many2one(string="Group", comodel_name="ims.group", domain="[('study_id', '=', study_id)]", required=True)
	subject_id = fields.Many2one(string="Subject", comodel_name="ims.subject", domain="[('study_id', '=', study_id)]", required=True)
	space_id = fields.Many2one(string="Space", comodel_name="ims.space", required=True)
	
	attendance_schedule_ids = fields.One2many(string="Sessions", comodel_name="ims.attendance_schedule", inverse_name="attendance_template_id")		
	
	student_ids = fields.Many2many(string="Students", comodel_name="res.partner", domain="[('contact_type', '=', 'student')]") # TODO: autofill by group + subject | allow changes

	def name_get(self):
        #Allows displaying a custom name: https://www.odoo.com/documentation/16.0/es/developer/reference/backend/orm.html#odoo.models.Model.name_get
		result = []	
		for rec in self:
			result.append((rec.id, "%s (%s)" % (rec.subject_id.name_get()[0][1], rec.group_id.name)))			
			
		return result

	@api.onchange("group_id")	
	def _onchange_group_id(self):		
		for rec in self:
			rec.space_id = rec.group_id.space_id