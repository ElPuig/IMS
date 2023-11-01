# -*- coding: utf-8 -*-

from odoo import models, fields, api

class ims_newteacher(models.Model):
    _inherit = "hr.employee"
    
    # _name = "ims.newteacher"
    # _description = "Teacher: Collects the teacher\"s data."
    # _inherits = {"hr.employee": "employee"}
    
    # employee = fields.Many2one("hr.employee", "Employee", required=True, ondelete="cascade")
    #The roles fields was a One2Many relation, but role's kanban view does not work within the form.		
    roles = fields.Many2many(string="Roles", comodel_name="ims.teacher_role")

    #This fields are computed in order to display string data within some views.
    roles_str = fields.Char(compute='_roles_str')	

    @api.depends("roles")
    def _roles_str(self):			
        for rec in self:
            rec.roles_str = ""
            for role in rec.roles:
                rec.roles_str = '%s, %s' % (rec.roles_str, role.name) 			
                #rec.roles_str = role.name

            rec.roles_str = rec.roles_str.lstrip(", ")
