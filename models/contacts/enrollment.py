# -*- coding: utf-8 -*-

from odoo import models, fields, api

class ims_enrollment(models.Model):
	_name = "ims.enrollment"
	_description = "Enrollment: ternary relation between student-group-uf."	

	student_id = fields.Many2one(string="Student", comodel_name="res.partner", required=True, domain="[('contact_type', '=', 'student')]")	
	group_id = fields.Many2one(string="Group", comodel_name="ims.group", required=True)	
	subject_id = fields.Many2one(string="Subject", comodel_name="ims.subject", required=True)	
	
	# this field is used to filter the availabe subjects within the view (avoiding the selection of repeated subject on enrolling form).
	inuse_subject_ids = fields.Many2many('ims.subject', compute='_compute_inuse_subject_ids', store=False) 
	# this field is used to change the style of the row in the view
	level = fields.Integer(string="Level", related="subject_id.level", store=False) 
		
	@api.depends('student_id')
	def _compute_inuse_subject_ids(self):
		for rec in self:
			rec.inuse_subject_ids = False
			if rec.student_id:
				rec.inuse_subject_ids = rec.mapped('student_id.enrollment_ids.subject_id')
                	
	@api.depends('subject_id')
	def _compute_display_name(self):              
		for rec in self:
			rec.display_name = "%s" % rec.subject_id.display_name
	