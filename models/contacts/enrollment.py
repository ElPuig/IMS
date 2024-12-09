# -*- coding: utf-8 -*-

from odoo import models, fields, api

class ims_enrollment(models.Model):
	_name = "ims.enrollment"
	_description = "Enrollment: ternary relation between student-group-uf."	

	student_id = fields.Many2one(string="Student", comodel_name="res.partner", required=True, domain="[('contact_type', '=', 'student')]")	
	group_id = fields.Many2one(string="Group", comodel_name="ims.group", required=True)	
	subject_id = fields.Many2one(string="Subject", comodel_name="ims.subject", required=True)		

	def name_get(self):
        #Allows displaying a custom name: https://www.odoo.com/documentation/16.0/es/developer/reference/backend/orm.html#odoo.models.Model.name_get
		result = []	

		for rec in self:
			result.append((rec.id, "%s" % rec.subject_id.name_get()[0][1]))			
			
		return result