# -*- coding: utf-8 -*-

from odoo import models, fields, api

class ims_study(models.Model):
    _name = 'ims.study'
    _description = 'Study'
    
    code = fields.Char('Code')
    acronym = fields.Char('Acronym')
    name = fields.Char('Name')
    date = fields.Date('Release Date')
    deprecated = fields.Boolean('Deprecated')
    notes = fields.Text('Notes')

    professional_modules = fields.One2many(comodel_name="ims.professional_module", inverse_name="study", string="Professional Modules")
    follows = fields.One2many(comodel_name="ims.followup", inverse_name="study", string="Follow-up")

