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
    ects = fields.Integer(string="ECTS Credits") 
    internal_hours = fields.Integer(string="Internal hours") 
    external_hours = fields.Integer(string="External hours")   

    total_internal_hours = fields.Integer(string="Total internal hours", compute='_compute_total_internal_hours', recursive=True) # Computed sum(hours / total_hours)
    total_external_hours = fields.Integer(string="Total external hours", compute='_compute_total_external_hours', recursive=True) # Computed sum(hours / total_hours)
    total_hours = fields.Integer(string="Total hours", compute='_compute_total_hours', recursive=True) # Computed sum(hours / total_hours)

    last = fields.Boolean(string="Last", compute='_compute_last') # To know if it's the last sub-subject (needed for views)
    
    notes = fields.Text("Notes")

    study_id = fields.Many2one(string="Study", comodel_name="ims.study", required="true")
    study_ids = fields.Many2many(string="Studies", comodel_name="ims.study")
    teacher_id = fields.Many2one(string="Teacher", comodel_name="hr.employee", domain="[('employee_type', '=', 'teacher')]")

    subject_ids = fields.One2many(string="Composite", comodel_name="ims.subject", inverse_name="subject_id", domain="[('id', '!=', id), ('level', '>', level), ('subject_id', '=', False)]")
    subject_id = fields.Many2one(string="Main subject", comodel_name="ims.subject")
    
    content_ids = fields.One2many(string="Content", comodel_name="ims.content", inverse_name="subject_id")
    criteria_ids = fields.One2many(string="Criteria", comodel_name="ims.criteria", inverse_name="subject_id")

    #The subject_view_ids is used as a view for the subject list
    #TODO: _compute_subject_views should run on every save (even when creating the model from demo data, not just saving the form...)
    subject_view_ids = fields.One2many(comodel_name="ims.subject_view", inverse_name="subject_id", compute="_compute_subject_views", store=True)

    @api.depends("study_ids")
    def _compute_subject_views(self):	        
        for rec in self:
            self.env['ims.subject_view'].search([('subject_id', '=', rec.id)]).unlink()
            for study in rec.study_ids:                
                rec.subject_view_ids.create({
                    "level": rec.level,
                    "code": rec.code,
                    "acronym": rec.acronym,
                    "name": rec.name,
                    "study_id": study.id,
                    "subject_id": rec.id,
                })	                               

    @api.onchange("subject_id")
    def _onchange_subject_id(self):
        for rec in self:
            rec.study_id = rec.subject_id.study_id
            rec.level = rec.subject_id.level + 1    
   
    @api.depends("subject_ids.internal_hours")
    def _compute_total_internal_hours(self):
        for rec in self:
            rec.total_internal_hours = sum((line.internal_hours if line.last else line.total_internal_hours) for line in rec.subject_ids)

    @api.depends("subject_ids.external_hours")
    def _compute_total_external_hours(self):
        for rec in self:
            rec.total_external_hours = sum((line.external_hours if line.last else line.total_external_hours) for line in rec.subject_ids)

    @api.depends("subject_ids.total_hours")
    @api.onchange("internal_hours", "external_hours")
    def _compute_total_hours(self):
        for rec in self:
            th = rec.total_internal_hours + rec.total_external_hours            
            rec.total_hours = rec.internal_hours + rec.external_hours if rec.last or th == 0 else th


    @api.depends("subject_ids")
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
    
class ims_subject_view(models.Model):
    _name = "ims.subject_view"
    _description = "View model for displaying subject data within studies (because a subject can be shared along different studies)."
    
    level = fields.Integer(string="Level")    
    code = fields.Char(string="Code", required="true")
    acronym = fields.Char(string="Acronym", required="true")
    name = fields.Char(string="Name", required="true")
    study_id = fields.Many2one(string="Study", comodel_name="ims.study", required="true")
    subject_id = fields.Many2one(string="Subject", comodel_name="ims.subject", required="true")