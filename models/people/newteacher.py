# -*- coding: utf-8 -*-

from odoo import models, fields, api
from odoo.exceptions import ValidationError

class ims_newteacher(models.Model):
    _inherit = "hr.employee"
    
    # employee_type = fields.Selection([('teacher', 'Teacher'), ('asp', 'ASP'), ('student', 'Student'), ('contractor', 'Contractor'), ('freelance', 'Freelance')])
    employee_type = fields.Selection(selection_add=[('teacher', 'Teacher'), ('asp', 'ASP')], ondelete={'teacher': 'set default', 'asp':'set default'})
    contract_type = fields.Many2one(comodel_name="hr.contract.type", string="Contract Type")

    # employee = fields.Many2one("hr.employee", "Employee", required=True, ondelete="cascade")
    #The roles fields was a One2Many relation, but role's kanban view does not work within the form.		
    roles = fields.Many2many(string="Roles", comodel_name="ims.teacher_role")

    #This fields are computed in order to display string data within some views.
    roles_str = fields.Char(compute='_roles_str')	

    @api.constrains('roles')
    @api.onchange('roles')
    def check_limit(self):
        for rec in self:
            for role in rec.roles:
                if len(role.teachers) > 1:
                    raise ValidationError("This role is already assigned to another teacher.")
				
    @api.depends("roles")
    def _roles_str(self):			
        for rec in self:
            rec.roles_str = ""
            for role in rec.roles:
                rec.roles_str = '%s, %s' % (rec.roles_str, role.name) 			
                #rec.roles_str = role.name

            rec.roles_str = rec.roles_str.lstrip(", ")
