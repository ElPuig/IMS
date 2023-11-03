# -*- coding: utf-8 -*-

from odoo import models, fields, api

class ims_job(models.Model):
    _inherit = "hr.job"
    
    #employee_type = fields.Selection(selection_add=[('teacher', 'Teacher'), ('asp', 'ASP')], ondelete={'teacher': 'set default', 'asp':'set default'})
    #employee_type = fields.Selection(selection=[('asp', 'ASP'), ('teacher', 'Teacher'), ('student', 'Student')], ondelete={'asp':'set default', 'teacher': 'set default', 'student': 'set default'})    

    # user_type_id = fields.Many2one('account.account.type', ...)
    # internal_type = fields.Selection(related='user_type_id.type', ...)

    employee_type = fields.Selection(string='Employee Type', selection=ims_employee.employee_types)
    		