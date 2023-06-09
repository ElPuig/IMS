# -*- coding: utf-8 -*-

from odoo import models, fields, api

class ims_formative_unit(models.Model):
    _name = 'ims.formative_unit'
    _description = 'Formative Unit'

    code = fields.Integer('Code')
    name = fields.Char('Name')    
    # start_date = fields.Date('Start date') #TODO: can change during courses
    # end_date = fields.Date('End date')

    teacher = fields.Many2one(comodel_name="ims.teacher", string="Teacher")
    professional_module = fields.Many2one(comodel_name="ims.professional_module", string="Professional Module")
    
    followups = fields.One2many(comodel_name="ims.followup", inverse_name="formative_unit", string="Follow-up")