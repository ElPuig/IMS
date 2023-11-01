# -*- coding: utf-8 -*-

from odoo import models, fields, api

class ims_newteacher(models.Model):
    _inherit = "hr.employee"
    
    # _name = "ims.newteacher"
    # _description = "Teacher: Collects the teacher\"s data."
    # _inherits = {"hr.employee": "employee"}
    
    # employee = fields.Many2one("hr.employee", "Employee", required=True, ondelete="cascade")
