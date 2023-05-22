# -*- coding: utf-8 -*-

from odoo import models, fields, api

class ims_status(models.Model):
    _name = 'ims.status'
    _description = 'Status'
    
    code = fields.Char('Code')
    value = fields.Char('Value')
    notes = fields.Text('Notes')

