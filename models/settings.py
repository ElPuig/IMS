# -*- coding: utf-8 -*-

from odoo import models, fields, api

class ResConfigSettings(models.TransientModel):
   _inherit = 'res.config.settings'

   contract_type = fields.Selection(
       [('monthly', 'Monthly'), ('half_yearly', '6 Months'),
        ('yearly', 'Yearly')],
       string="Contract Type",
       config_parameter='ims.contract_type',
       help="Select contract types from the selection field")