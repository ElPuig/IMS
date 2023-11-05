# -*- coding: utf-8 -*-

from odoo import models, fields, api
from odoo.exceptions import ValidationError

class ims_contact(models.Model):
    _inherit = ["res.partner"]
    
    contact_type = fields.Selection(string='Contact Type', selection=[('provider', 'Provider'), ('student', 'Student')])
    main_group_id = fields.Many2one(string="Main Group", comodel_name="ims.group")    