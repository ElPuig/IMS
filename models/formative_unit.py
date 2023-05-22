# -*- coding: utf-8 -*-

from odoo import models, fields, api

class ims_formative_unit(models.Model):
    _name = 'ims.formative_unit'
    _description = 'Formative Unit'

    name = fields.Char('Name')
    code = fields.Char('Code')
    #teacher = fields.Char('Professor')
    start_date = fields.Date('Start date')
    end_date = fields.Date('End date')

    teacher = fields.Many2one(comodel_name="ims.teacher", string="Teacher")
    professional_module = fields.Many2one(comodel_name="ims.professional_module", string="Professional Module")
    
    followups = fields.One2many(comodel_name="ims.followup", inverse_name="formative_unit", string="Follow-up")