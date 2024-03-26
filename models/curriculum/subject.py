# -*- coding: utf-8 -*-

from odoo import models, fields, api
from odoo.exceptions import ValidationError

class ims_subject(models.Model):
    _name = "ims.subject"
    _description = "Subject: The main item for a student's subject."

    code = fields.Char(string="Code", required="true")
    acronym = fields.Char(string="Acronym", required="true")
    name = fields.Char(string="Name", required="true")
    level = fields.Integer(string="Level")  # Note: this field is computed, but marking as compute needs Store=true for filtering and then is not beeing updated :(
    notes = fields.Text("Notes")

    study_id = fields.Many2one(string="Study", comodel_name="ims.study", required="true")
    teacher_id = fields.Many2one(string="Teacher", comodel_name="hr.employee", domain="[('employee_type', '=', 'teacher')]")

    # TODO: some way to directly open the new form instead of searching (no search is needed, no orphan should be allowed)
    subject_ids = fields.One2many(string="Content", comodel_name="ims.subject", inverse_name="subject_id", domain="[('id', '!=', id), ('level', '>', level), ('subject_id', '=', False)]")
    subject_id = fields.Many2one(string="Main subject", comodel_name="ims.subject")    
    
    @api.onchange("subject_id")
    def _onchange_subject_id(self):
        for rec in self:
            rec.study_id = rec.subject_id.study_id
            rec.level = rec.subject_id.level + 1              

    def name_get(self):
		#Allows displaying a custom name: https://www.odoo.com/documentation/16.0/es/developer/reference/backend/orm.html#odoo.models.Model.name_get

        result = []	
        for rec in self:
            result.append((rec.id, "%s %s: %s" % (rec.study_id.acronym, rec.acronym, rec.name)))
            
        return result