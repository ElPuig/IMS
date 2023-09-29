# -*- coding: utf-8 -*-

from odoo import models, fields, api

class ims_group(models.Model):
	_name = "ims.group"
	_description = "Groups: Where the students are assigned to."	
	
	course = fields.Integer(string="Course", required="true")
	acronym = fields.Char(string="Acronym", required="true")
	# name = fields.Char(string="Name")
	name=fields.Char(string='Name',compute='_compute_name')
	notes = fields.Text(string="Notes")

	study = fields.Many2one(string="Study", comodel_name="ims.study", required="true")	
	students = fields.One2many(string="Students", comodel_name="ims.student", inverse_name="group")
	
	@api.depends("study.acronym", "course", "acronym")
	def _compute_name(self):
		for rec in self:
			rec.name = '%s%s%s' % (rec.study.acronym, rec.course, rec.acronym)