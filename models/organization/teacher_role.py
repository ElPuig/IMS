# -*- coding: utf-8 -*-

from odoo import models, fields, api
from odoo.exceptions import ValidationError

class ims_teacher_role(models.Model):
	_name = "ims.teacher_role"
	_description = "Teacher's position: The coordination position held by the teachers staff."

	name = fields.Char(string="Name", required="true")	
	color = fields.Integer(string="Color")
	notes = fields.Text(string="Notes")
	
	#The teachers (old teacher) field was a Many2one relation, but kanban view does not work within the form. It will be validated on the fly.
	#teachers = fields.Many2many(string="Teacher", comodel_name="hr.employee.public")		
	#teachers = fields.Many2many(string="Teacher", comodel_name="hr.employee.public", domain="[('employee_type', '=', 'teacher')]")		
	#Note: manual relation is needed, otherwise Odoo creates two tables within the BBDD, one for 'hr.employee.public' and one for 'hr.employee.base' 
	teachers = fields.Many2many(string="Teacher", comodel_name='hr.employee.public', relation='hr_employee_public_ims_teacher_role_rel', column1='ims_teacher_role_id', column2='hr_employee_public_id', domain="[('employee_type', '=', 'teacher')]") 

	@api.constrains('teachers')
	def check_limit(self):
		for rec in self:
			if len(rec.teachers) > 1:
				raise ValidationError("This role is already assigned to another teacher.")