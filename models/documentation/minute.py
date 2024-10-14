# -*- coding: utf-8 -*-

from odoo import models, fields, api
from datetime import datetime

class minute(models.Model):
	_name = "ims.minute"
	_description = "Minute: Defines a meeting minute (department meeting, workgroup meeting, evaluation meeting...)."
	
	date = fields.Datetime(string="Date", default=datetime.today(), required="true")
	type = fields.Selection(string="Type", default="department", selection=[("department", "Department meeting"), ("workgroup", "Workgroup meeting"), ("evaluation", "Evaluation meeting")], required="true") #TODO: more types?	
	nature = fields.Selection(string="Nature", default="ordinary", selection=[("ordinary", "Ordinary"), ("extraordinary", "Extraordinary")], required="true")
	modality = fields.Selection(string="Modality", default="in-person", selection=[("in-person", "In-person"), ("online", "Online"), ("hybrid", "Hybrid")], required="true")	

	space_id = fields.Many2one(string="Space", comodel_name="ims.space", required="true")
	department_id = fields.Many2one(string="Department", comodel_name="hr.department")
	workgroup_id = fields.Many2one(string="Workgroup", comodel_name="ims.workgroup")	

	#Note: foreign to the same table should be declared manually
	assistant_ids = fields.Many2many(string="Assistants", comodel_name="res.partner", relation="ims_minute_assistant_rel", column1="ims_minute_id", column2="res_partner_id", domain="[('type','=','contact')]", required="true") 
	abstent_ids = fields.Many2many(string="Abstents", comodel_name="res.partner", relation="ims_minute_absetnt_rel", column1="ims_minute_id", column2="res_partner_id", domain="[('type','=','contact')]") 
	
	members = fields.Char(string="Memebers", compute='_compute_members')
	abstract = fields.Char(string="Abstract or main topic", size=255, required="true")
	
	def name_get(self):
		#Allows displaying a custom name: https://www.odoo.com/documentation/16.0/es/developer/reference/backend/orm.html#odoo.models.Model.name_get
        
		result = []	    
		for rec in self:           
			result.append((rec.id, "%s: %s (%s)" % (dict(rec._fields['type'].selection).get(rec.type), rec.workgroup_id.name if type == "workgroup" else rec.department_id.name, dict(rec._fields['nature'].selection).get(rec.nature))))
            
		return result

	@api.depends("type")
	def _compute_members(self):
		for rec in self:
			rec.members = "Workgroup: %s" % rec.workgroup_id.name if rec.type == "workgroup" else "Department: %s" % rec.department_id.name

	#TODO: Should also set the permissions for the record (department and also workgroup <-- NEW)
	#	   https://www.cybrosys.com/blog/how-to-create-record-rule-in-odoo-16

	#index -> should be computed using the record section but some content is fixed
	#	1. Last record approval (if exists).
	#	2. Last agreements review.
	#	3. Regular meeting content. where each record section should have.
	#		3.1. Title.
	#		3.2. The content or another section.
	#		NOTE: pending topics of the last meeting could be added.
	#	4. Agreements
	#	5. Pending topics.
	#	6. Signature
	#		6.1. By the user who created the record (will be signed by clicking on a button).
	#		6.2. By another user who aproves it, should be loaded as manager of the previous one, but this could limit some scenearios so it"s better to let it free.
	#			 The redactor adds the aprover, and a notification will be sent. The aprover can aprove the record or not.
	#			 The record can be edited, but then it becomes desaproved. 
	#
	#	7. Attachments (this will allow to attach any custom document).
	#
	#	PENDING: changes registry?



