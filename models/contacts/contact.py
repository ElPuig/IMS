# -*- coding: utf-8 -*-

from odoo import models, fields, api
from odoo.exceptions import ValidationError

class ims_contact(models.Model):
    _inherit = ['res.partner']
        
    tutor = fields.Char(string='Tutor', compute="_compute_tutor", store=True)
    level_id = fields.Many2one(string='Level', comodel_name='ims.level')#, compute="_compute_level_id", store=True)
    study_id = fields.Many2one(string='Studies', comodel_name='ims.study')#, compute="_compute_study_id", store=True)
    main_group_id = fields.Many2one(string='Main Group', comodel_name='ims.group')        
    enrollment_ids = fields.One2many(string='Enrollment', comodel_name='ims.enrollment', inverse_name='student_id')
    contact_type = fields.Selection(string='Contact Type', selection=[('provider', 'Provider'), ('student', 'Student')])

    @api.depends('main_group_id')
    def _compute_tutor(self):	
        for rec in self:			
            rec.tutor = rec.main_group_id.tutor_id.name                        
            if rec.tutor == 'False':
                rec.tutor = 'None' 

    # Desired behaviour:
    #   1. Data import through demo data (XML) or CSV shall not need to specify level_id, study_id nor tutor, everything will be computed through main_group_id
    #      This is enough just on creation, but all the fields must be loaded and stored correctly on the BBDD.  
    #
    #   2. Data manipulation through the form must clear fields if some dependency is removed: level > studies > group
    #
    #   Option 1: @api.depends('main_group_id') to compute the firs time the model is created, with NO compute on any field. I guess this is fired just on creation. 
    #             @api.onchange for all the other changes (included the tutor within the form view).
    #  
    #   Option 2: Everything with @api.onchange and override the "write" method to calculate on creation. 
    
    # @api.depends('study_id')
    # def _compute_main_group_id(self):	
    #     for rec in self:			
    #         rec.study_id = rec.main_group_id.study_id            

    # @api.depends('main_group_id')
    # def _compute_study_id(self):	
    #     for rec in self:			
    #         rec.study_id = rec.main_group_id.study_id         

    # @api.depends('main_group_id')
    # def _compute_level_id(self):	
    #     for rec in self:			
    #         rec.level_id = rec.main_group_id.study_id.level_id    

    # # Data manipulation through the form must clear fields if some dependency is removed: level > studies > group
    # @api.onchange('level_id')
    # def _onchange_level_id(self):	
    #     for rec in self:			
    #         rec.study_id = False
        
    # @api.onchange('study_id')
    # def _onchange_study_id(self):	
    #     for rec in self:			
    #         rec.main_group_id = False
