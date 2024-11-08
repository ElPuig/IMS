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
    hours = fields.Integer(string="Hours")  # For the last sub-subject
    last = fields.Boolean(string="Last", compute='_compute_last') # To know if it's the last sub-subject (needed for views)
    total_hours = fields.Integer(string="Total hours", compute='_compute_total_hours', recursive=True) # Computed sum(hours / total_hours)
    notes = fields.Text("Notes")

    study_id = fields.Many2one(string="Study", comodel_name="ims.study", required="true")
    teacher_id = fields.Many2one(string="Teacher", comodel_name="hr.employee", domain="[('employee_type', '=', 'teacher')]")

    subject_ids = fields.One2many(string="Composite", comodel_name="ims.subject", inverse_name="subject_id", domain="[('id', '!=', id), ('level', '>', level), ('subject_id', '=', False)]")
    subject_id = fields.Many2one(string="Main subject", comodel_name="ims.subject")
    
    content_ids = fields.One2many(string="Content", comodel_name="ims.content", inverse_name="subject_id")
    criteria_ids = fields.One2many(string="Criteria", comodel_name="ims.criteria", inverse_name="subject_id")

    # TODO: add "internal_hours" and "external_hours", including the computation of "hours" due this and its children.
    # TODO: add AR only for VET, every AR has "ACs" and "Cs". "ACs" and "Cs" are recursive.

    @api.onchange("subject_id")
    def _onchange_subject_id(self):
        for rec in self:
            rec.study_id = rec.subject_id.study_id
            rec.level = rec.subject_id.level + 1    

    @api.depends('subject_ids.total_hours')
    def _compute_total_hours(self):
        for rec in self:
            rec.total_hours = sum((line.hours if line.last else line.total_hours) for line in rec.subject_ids)

    @api.depends('subject_ids')
    def _compute_last(self):
        for rec in self:
            rec.last = (len(rec.subject_ids) == 0)
            
    def name_get(self):
		#Allows displaying a custom name: https://www.odoo.com/documentation/16.0/es/developer/reference/backend/orm.html#odoo.models.Model.name_get

        result = []	    
        acronyms = []    
        for rec in self:
            acronyms.clear()
            acronyms.append(rec.acronym)

            parent = rec.subject_id
            while(parent):
                acronyms.append(parent.acronym)
                parent = parent.subject_id     

            result.append((rec.id, "%s %s: %s" % (rec.study_id.acronym, " ".join(list(reversed(acronyms))), rec.name)))
            
        return result
    
    def open_form_view_subject(self):
        return {
            'name': 'Subject Edit',
            'domain': [],
            'res_model': 'ims.subject',
            'type': 'ir.actions.act_window',
            'view_mode': 'form',
            'view_type': 'form',
            'res_id': self.id,
            'target': 'new',
        }