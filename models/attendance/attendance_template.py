# -*- coding: utf-8 -*-

from odoo import models, fields, api

class ims_attendance_template(models.Model):
	_name = 'ims.attendance_template'
	_description = 'Attendance template'

	# start_date = fields.Datetime(string="Start date", default = fields.Datetime.now)	
	# end_date = fields.Datetime(string="End date", default = fields.Datetime.now)	
	# duration = fields.Integer(string="Duration", default = 60)
	start_time = fields.Float("Start Time")
	end_time = fields.Float("End Time")

	teacher = fields.Many2one(string="Teacher", comodel_name="hr.employee")
	student = fields.Many2one(string="Student", comodel_name="res.partner", domain="[('contact_type', '=', 'student')]")
	study = fields.Many2one(string="Study", comodel_name="ims.study")
	subject = fields.Many2one(string="Subject",comodel_name="ims.subject")
	level = fields.Many2one(string="Level", comodel_name="ims.level") #TODO: this should be loaded from subject
	space = fields.Many2one(string="Space", comodel_name="ims.space")
	weekday = fields.Selection(string="Weekday", selection=[
		('1', 'Monday'),
        ('2', 'Tuesday'),
        ('3', 'Wednesday'),
        ('4', 'Thursday'),
        ('5', 'Friday'),
    ])

	color = fields.Integer(string='Color', help='Field to store the color that will be used for calendar view')    
	attendance_group = fields.Many2one(string="Attendance Template Group", comodel_name="ims.attendance_group")		

	# TODO: Revisar porqué el onchange no funciona
	@api.onchange("attendance_group")
	def _onchange_attendance_group(self):
		if self.attendance_group:
			self.study = self.attendance_group.study
			self.subject = self.attendance_group.subject
			self.teacher = self.attendance_group.teacher
			self.space = self.attendance_group.space
			self.weekday = self.attendance_group.weekday
			self.color = self.attendance_group.color

	

	


   # TODO:
   # Template: teacher -> group -> subject -> loads the students data and also the space (allows to edit)
   # Sessions: which day and our to use the template
   # Instance: use a session to fill assistance data (attendance_status)
   # Status: attencade status per student in an instance
    