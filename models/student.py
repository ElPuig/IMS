# -*- coding: utf-8 -*-
import base64
from odoo import models, fields, api

class ims_student(models.Model):
	_name = "ims.student"
	_description = "Student: Collects the student\"s data."
	_inherit = "ims.person"

	group = fields.Many2one(comodel_name="ims.group", string="Group")
	follows = fields.One2many(comodel_name="ims.tracking", inverse_name="student", string="Follow-up")

	# @api.model
	# def create(self, vals):
	# 	if vals.get("image"):
	# 		vals["image"] = base64.b64encode(vals["image"]).decode("utf-8")
	# 	return super(ims_student, self).create(vals)
	
	# def write(self, vals):
	# 	if vals.get("image"):
	# 		vals["image"] = base64.b64encode(vals["image"]).decode("utf-8")
	# 	return super(ims_student, self).write(vals)