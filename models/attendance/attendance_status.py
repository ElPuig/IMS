# -*- coding: utf-8 -*-

from odoo import models, fields, api

class ims_attendance_status(models.Model):
	_name = "ims.attendance_status"
	_description = "Attendance status: information about session per student."

	status = fields.Selection(string="Status", default="1", required=True, selection=
        [("1", "Attended"), ("2", "Delay"), ("3", "Miss"), ("4", "Justified Miss"), ("5", "Issue")]
    )

	student_id = fields.Many2one(string="Student", comodel_name="res.partner", domain="[('contact_type', '=', 'student')]")
	student_image = fields.Binary(string="Image", related='student_id.image_1920')
	attendance_session_id = fields.Many2one(string="Session", comodel_name="ims.attendance_session")
	notes = fields.Text("Notes")
	