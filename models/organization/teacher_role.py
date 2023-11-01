# -*- coding: utf-8 -*-

from odoo import models, fields, api
from odoo.exceptions import ValidationError

class ims_teacher_role(models.Model):
	_name = "ims.teacher_role"
	_description = "Teacher's position: The coordination position held by the teachers staff."

	name = fields.Char(string="Name", required="true")	
	notes = fields.Text(string="Notes")
	
	#The teachers (old teacher) field was a Many2one relation, but kanban view does not work within the form. It will be validated on the fly.
	#teachers = fields.Many2many(string="Teacher", comodel_name="ims.teacher")		
	teachers = fields.Many2many(string="Teacher", comodel_name="hr.employee", domain="[('job_id', '=', 'teacher')]")		

	@api.constrains('teachers')
	@api.onchange('teachers')
	def _check_limit(self):
		if len(self.teachers)>1:
			raise ValidationError("Only one teacher per role is allowed.")