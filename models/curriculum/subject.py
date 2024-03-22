# -*- coding: utf-8 -*-

from odoo import models, fields, api

class ims_subject(models.Model):
    _name = "ims.subject"
    _description = "Subject: The main item for a student's subject."

    code = fields.Char(string="Code", required="true")
    acronym = fields.Char(string="Acronym", required="true")
    name = fields.Char(string="Name", required="true")
    notes = fields.Text("Notes")

    study_id = fields.Many2one(string="Study", comodel_name="ims.study", required="true")
    teacher_id = fields.Many2one(string="Teacher", comodel_name="hr.employee", domain="[('employee_type', '=', 'teacher')]")

    subject_ids = fields.One2many(string="Content", comodel_name="ims.subject", inverse_name="subject_id", domain="[('id', '!=', id)]")
    subject_id = fields.Many2one(string="Main subject", comodel_name="ims.subject")
    
    level = fields.Char(string="Level", compute="_level", store=True)	

    @api.depends("subject_id")
    def _level(self):			
        for rec in self:
            rec.roles = 1
            #TODO: ask each rec.subject_id for his level, the current level is that + 1
            # for role in rec.role_ids:
            #     rec.roles = "%s, %s" % (rec.roles, role.name) 			
            # rec.roles = rec.roles.lstrip(", ")

    def name_get(self):
		#Allows displaying a custom name: https://www.odoo.com/documentation/16.0/es/developer/reference/backend/orm.html#odoo.models.Model.name_get

        result = []	
        for rec in self:
            result.append((rec.id, "%s %s: %s" % (rec.study_id.acronym, rec.acronym, rec.name)))
            
        return result