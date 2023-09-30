# -*- coding: utf-8 -*-
import base64
from odoo import models, fields, api

class ims_student(models.Model):
	_name = "ims.student"
	_description = "Student: Collects the student\"s data."

	code = fields.Integer(string="Code")
	name = fields.Char(string="Name")
	surname = fields.Char(string="Surnames")
	corporate_email = fields.Char(string="Email (professional)", required="true")
	personal_email = fields.Char(string="Email (personal)")
	corporate_phone = fields.Char(string="Phone (professional)")
	personal_phone = fields.Char(string="Phone (personal)")
	image = fields.Binary(string=" ") #TODO: Improve this --> empty label for image filed becasue the image widget will be used, and nocaption="1" produces side effects with the image size... Also, image export will be no avaliable with no caption...
	notes = fields.Text("Notes")

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