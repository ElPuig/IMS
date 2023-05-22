# -*- coding: utf-8 -*-

from odoo import models, fields, api

class ims_study(models.Model):
    _name = 'ims.study'
    _description = 'Study'
    
    code = fields.Char('Code')
    name = fields.Char('Name')
    active = fields.Boolean('Active')
    notes = fields.Text('Notes')

    follows = fields.One2many(comodel_name="ims.followup", inverse_name="study", string="Follow-up")
