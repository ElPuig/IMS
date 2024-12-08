# -*- coding: utf-8 -*-

from odoo import models, fields, api
from odoo.exceptions import ValidationError

employee_types = [
    ("asp", "Administrative and Services Personnel"), 
    ("teacher", "Teacher")
]

class ims_employee_base(models.AbstractModel):
    _inherit = ["hr.employee.base"]
    
    notes = fields.Text(string="Notes")
    
    #TODO: selection_add fails, like if employee_type wasn't a selection field... WHY?
    employee_type = fields.Selection(string="Employee Type", selection="_get_new_employee_type")
    #employee_type = fields.Selection(string="Employee Type", selection = employee_types)

    contract_type_id = fields.Many2one(string="Contract Type", comodel_name="hr.contract.type")
    job_id = fields.Many2one(string="Job Position", comodel_name="hr.job", domain="[('employee_type', '=', employee_type)]")
    teaching_ids = fields.One2many(string="Teaching", comodel_name="ims.teaching", inverse_name="teacher_id")	
   
    #Note: manual relation is needed, otherwise Odoo creates two tables within the BBDD, one for 'hr.employee.public' and one for 'hr.employee.base' 
    role_ids = fields.Many2many(string="Roles", comodel_name="ims.role", relation="hr_employee_public_ims_role_rel", column1="hr_employee_public_id", column2="ims_role_id", domain="[('employee_type', '=', employee_type)]") 
    tutorship_ids = fields.One2many(string="Tutorships", comodel_name="ims.group", inverse_name="tutor_id")

    #This fields are computed in order to display string data within some views.
    roles = fields.Char(string="Role names", compute="_compute_roles_str", store=True)	
    tutorships = fields.Char(string="Tutorship names", compute="_compute_tutorships_str", store=True)	

    # @api.model
    # def _get_new_employee_type(self):            
    #     return employee_types
    
    @api.constrains("role_ids")
    def check_limit(self):
        for rec in self:
            for role in rec.role_ids:                
                role.check_limit()                
				
    @api.depends("role_ids")
    def _compute_roles_str(self):			
        for rec in self:
            rec.roles = ""
            for role in rec.role_ids:
                rec.roles = "%s, %s" % (rec.roles, role.name) 			
            rec.roles = rec.roles.lstrip(", ")

    
    @api.depends("tutorship_ids")
    def _compute_tutorships_str(self):			
        for rec in self:
            rec.tutorships = ""
            for tutorship in rec.tutorship_ids:
                rec.tutorships = "%s, %s" % (rec.tutorships, tutorship.name) 			
            rec.tutorships = rec.tutorships.lstrip(", ")

class ims_employee(models.AbstractModel):
    _inherit = ["hr.employee"]

    employee_type = fields.Selection(string="Employee Type", selection_add = employee_types, ondelete={
        'asp': 'set default',
        'teacher': 'set default'
    })