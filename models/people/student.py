# -*- coding: utf-8 -*-
import base64
from odoo import models, fields, api

class ims_student(models.Model):
	_name = "ims.student"
	_description = "Student: Collects the student\"s data."
	_inherit = "ims.corporate_person"

	group = fields.Many2one(comodel_name="ims.student_group", string="Group")
	tutor=fields.Char(string='Tutor', compute='_compute_tutor')
	follows = fields.One2many(comodel_name="ims.tracking", inverse_name="student", string="Follow-up")

	@api.depends("group")
	def _compute_tutor(self):	
		for rec in self:
			rec.tutor = '%s %s' % (rec.group.tutor.name, rec.group.tutor.surname)