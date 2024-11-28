# -*- coding: utf-8 -*-

from odoo import models, fields, api

class ims_study(models.Model):
    _name = "ims.study"
    _description = "Study: The concrete type of stidy (kind of bachelor, concrete univeristy grade, etc.)"
    
    code = fields.Char(string="Code", required="true")
    acronym = fields.Char(string="Acronym", required="true")
    name = fields.Char(string="Name", required="true")
    date = fields.Date(string="Release Date", required="true")
    deprecated = fields.Boolean(string="Deprecated", required="true")
    main_decree = fields.Binary(string="Main decree")
    regional_decree = fields.Binary(string="Regional decree")
    notes = fields.Text(string="Notes")
    
    follow_ids = fields.One2many(string="Follow-up", comodel_name="ims.tracking", inverse_name="study_id")
    subject_ids = fields.Many2many(string="Subjects", comodel_name="ims.subject")
    level_id = fields.Many2one(string="Level", comodel_name="ims.level")

    def name_get(self):
        #Allows displaying a custom name: https://www.odoo.com/documentation/16.0/es/developer/reference/backend/orm.html#odoo.models.Model.name_get
        result = []	

        for rec in self:
            result.append((rec.id, "%s: %s" % (rec.acronym, rec.name)))			
            
        return result
    
    def open_form_view_study(self):
        return {
            'name': 'Study Edit',
            'domain': [],
            'res_model': 'ims.study',
            'type': 'ir.actions.act_window',
            'view_mode': 'form',
            'view_type': 'form',
            'res_id': self.id,
            'target': 'new',
        }