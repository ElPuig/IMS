# -*- coding: utf-8 -*-

from odoo import models, fields, api

class ims_study(models.Model):
    _name = 'ims.study'
    _description = 'Estudi'
    
    code = fields.Char('Codi')
    name = fields.Char('Nom')
    active = fields.Boolean('Actiu')
    notes = fields.Text('Anotacions')

    follows = fields.One2many(comodel_name="ims.follow", inverse_name="study", string="Seguiments")
