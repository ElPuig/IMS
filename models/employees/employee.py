# -*- coding: utf-8 -*-

from odoo import models, fields, api
from odoo.exceptions import ValidationError

employee_types = [
    ('asp', 'Administrative and Services Personnel'), 
    ('teacher', 'Teacher')
]

class ims_employee(models.Model):
    _inherit = "hr.employee"
    
    notes = fields.Text(string="Notes")
        
    employee_type = fields.Selection(string='Employee Type', selection='_get_new_employee_type', compute='_compute_question_type', readonly=False, store=True)
    contract_type_id = fields.Many2one(comodel_name="hr.contract.type", string="Contract Type")
    job_id = fields.Many2one(comodel_name="hr.job", string="Job Position", domain="[('employee_type', '=', employee_type)]")
    teaching_ids = fields.One2many(string="Teaching", comodel_name="ims.teaching", inverse_name="teacher")	

    #The roles fields was a One2Many relation, but role's kanban view does not work within the form.		
    role_ids = fields.Many2many(string="Roles", comodel_name="ims.teacher_role")
    tutorship_ids = fields.One2many(string="Tutorships", comodel_name="ims.student_group", inverse_name="tutor")

    #This fields are computed in order to display string data within some views.
    roles = fields.Char(compute='_roles_str')	
    tutorships = fields.Char(compute='_tutorships_str')	

    @api.model
    def _get_new_employee_type(self):            
        return employee_types


    @api.constrains('roles')
    @api.onchange('roles')
    def check_limit(self):
        for rec in self:
            for role in rec.role_ids:
                if len(role.teachers) > 1:
                    raise ValidationError("This role is already assigned to another teacher.")
				
    @api.depends("roles")
    def _roles_str(self):			
        for rec in self:
            rec.roles = ""
            for role in rec.role_ids:
                rec.roles = '%s, %s' % (rec.roles, role.name) 			
                #rec.roles_str = role.name

            rec.roles = rec.roles.lstrip(", ")

    
    @api.depends("tutorships")
    def _tutorships_str(self):			
        for rec in self:
            rec.tutorships = ""
            for tutorship in rec.tutorship_ids:
                rec.tutorships = '%s, %s' % (rec.tutorships, tutorship.name) 			
                #rec.roles_str = role.name

            rec.tutorships = rec.tutorships.lstrip(", ")
