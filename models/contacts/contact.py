# -*- coding: utf-8 -*-

from odoo import models, fields, api
from odoo.exceptions import ValidationError

class ims_contact(models.Model):
    _inherit = ["res.partner"]
    
    contact_type = fields.Selection(string="Contact Type", selection=[("provider", "Provider"), ("student", "Student")])
    main_group_id = fields.Many2one(string="Main Group", comodel_name="ims.group")
    tutor = fields.Char(string="Tutor", compute="_compute_tutor", store=True)
    enrollment_ids = fields.One2many(string="Enrollment", comodel_name="ims.enrollment", inverse_name="student_id")

    @api.depends("main_group_id")
    def _compute_tutor(self):	
        for rec in self:			
            rec.tutor = rec.main_group_id.tutor_id.name
            
            if rec.tutor == "False":
                rec.tutor = "None"    

    def open_form_view_contact_by_id(self, id):
         return {
            'name': 'Student',
            'domain': [],
            'res_model': 'res.partner',
            'type': 'ir.actions.act_window',
            'view_mode': 'form',
            'view_type': 'form',
            'res_id': id,
            'target': 'new',
        }

    def open_form_view_contact(self):
        return self.open_form_view_contact_by_id(self.id)