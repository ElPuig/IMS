# -*- coding: utf-8 -*-

from odoo import models, fields, api

class ims_group(models.Model):
	_name = 'ims.group'
	_description = 'Groups: Where the students are assigned to.'

	acronym = fields.Char('Acronym')
	name = fields.Char('Name')
	email = fields.Char('Email')	
	notes = fields.Text('Notes')

	students = fields.One2many(comodel_name="ims.student", inverse_name="group", string="Students")
	template_groups = fields.One2many(comodel_name="ims.template_group", inverse_name="group", string="Groups")