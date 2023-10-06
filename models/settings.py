# -*- coding: utf-8 -*-

from odoo import models, fields, api

class _ims_settings(models.TransientModel):
    _inherit = 'res.config.settings'   
    
    test = fields.Boolean(string="Test")