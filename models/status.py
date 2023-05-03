# -*- coding: utf-8 -*-

from odoo import models, fields, api

class ims_status(models.Model):
    _name = 'ims.status'
    _description = 'Estat'
    
    code = fields.Char('Codi')
    value = fields.Char('Valor')
    notes = fields.Text('Anotacions')

