# -*- coding: utf-8 -*-

from odoo import models, fields, api
from odoo.exceptions import ValidationError

class ims_contact(models.Model):
    _inherit = ['res.partner']
            
    # view-oriented fields:
    # level_id and study_id are used for form view purposes (linked dropdowns: level > study > group) and will be computed on save.
    level_id = fields.Many2one(string='Level', comodel_name='ims.level')    
    study_id = fields.Many2one(string='Studies', comodel_name='ims.study') 
    tutor_id = fields.Many2one(string='Tutor', related="main_group_id.tutor_id") # Related field: auto-computed and auto-refreshed within the form.
    
    # model-data fields:
    main_group_id = fields.Many2one(string='Main Group', comodel_name='ims.group')            
    enrollment_ids = fields.One2many(string='Enrollment', comodel_name='ims.enrollment', inverse_name='student_id')
    contact_type = fields.Selection(string='Contact Type', selection=[('provider', 'Provider'), ('student', 'Student')])   
    
    @api.onchange('enrollment_ids')
    def _onchange_enrollment_ids(self):	
        # The idea is to populate the enrollment data in both directions:
        #	Up:   if the subject has a parent, create it if missing.
        #	Down: if the subject has children, create them if missing.		

        # TODO: must know if added, removed or updated!
        for rec in self:	
            current_enrollment = rec.enrollment_ids[-1]                   
            parent_subject = current_enrollment.subject_id .subject_id
            children_subject = current_enrollment.subject_id .subject_ids
            if parent_subject:
                # Has a parent                
                enrollment = self.enrollment_ids.search([("student_id", "=", rec.id), ("subject_id", "=", parent_subject.id)]) or False                
                # if not enrollment:
                #     # Create the parent entry
                #     rec.enrollment_ids.create({
                #         "student_id": rec.id,
                #         "group_id": current_enrollment.group_id,
                #         "subject_id": parent_subject.id,                        
                #     })
            
            if children_subject:
                # Has children
                for children in children_subject:
                    enrollment = self.enrollment_ids.search([("subject_id", "=", children.subject_id.id)]) or False
                    raise UserWarning(len(enrollment))
                    if len(enrollment) == 0:
                        raise UserWarning("CHILDREN")

    @api.onchange('level_id')
    def _onchange_level_id(self):	
        for rec in self:			
            rec.study_id = False
        
    @api.onchange('study_id')
    def _onchange_study_id(self):	
        for rec in self:			
            rec.main_group_id = False
    
    @api.model_create_multi
    def create(self, values):
        # Fired when the model is created (Source: https://www.cybrosys.com/blog/how-to-override-create-write-and-unlink-methods-in-odoo-17)
        self._compute_group_data(values)
        contact = super(ims_contact, self).create(values)

        #self._compute_enrollment_data(contact)
        return contact
    
    def write(self, values):
        # Fired when the model is updated (Source: https://www.cybrosys.com/blog/how-to-override-create-write-and-unlink-methods-in-odoo-17)
        self._compute_group_data(values)
        contact =  super(ims_contact, self).write(values)

        #self._compute_enrollment_data(contact)
        return contact

    def _compute_group_data(self, values):
        # Avoids incongruences between the main_group, level and studies.     
        if 'main_group_id' in values and values.get('main_group_id'):   
            group = self.env["ims.group"].search([("id", "=", values.get('main_group_id'))]) or False                 
            values["level_id"] = group.level_id.id
            values["study_id"] = group.study_id.id

        elif 'study_id' in values and values.get('study_id'):
            study = self.env["ims.study"].search([("id", "=", values.get('study_id'))]) or False            
            values["level_id"] = study.level_id.id

    #def _compute_enrollment_data(self, contact):
		# The idea is to populate the enrollment data in both directions:
		#	Up:   if the subject has a parent, create it if missing.
		#	Down: if the subject has children, create them if missing.		
        
        # subject = self.env["ims.subject"].search([("id", "=", values.get('subject_id'))]) or False 
        # if subject.subject_id:
        #     # Has a parent
        #     enrollment = self.env["ims.enrollment"].search([("subject_id", "=", subject.subject_id.id)]) or False
        #     if len(enrollment) == 0:
        #         # Create the parent entry
        #         current.subject_view_ids.create({
        #             "level": rec.level,
        #             "code": rec.code,
        #             "acronym": rec.acronym,
        #             "name": rec.name,                        
        #             "subject_id": rec.id,
        #             "study_id": study.id,
        #         })

        # if subject.subject_id:
        