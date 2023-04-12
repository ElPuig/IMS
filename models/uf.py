# -*- coding: utf-8 -*-

from odoo import models, fields, api

class ims_uf(models.Model):
    _name = 'ims.uf'
    _description = 'Model de dades per a una Unitat Formativa'

    name = fields.Char('Nom')
    code = fields.Char('Codi')
    #teacher = fields.Char('Professor')
    startDate = fields.Date('Data inici')
    endDate = fields.Date('Data final')

    teacher = fields.Many2one(comodel_name="ims.teacher", string="Professor")

    mp = fields.Many2one(comodel_name="ims.mp", string="Modul Professional")