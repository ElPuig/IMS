# -*- coding: utf-8 -*-

from odoo import models, fields, api
from odoo.http import request
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
        #	Up:   if the subjecenrollment_idst has a parent, create it if missing.
        #	Down: if the subject has children, create them if missing.		
        #
        # Warning: the added or removed row is not retreived, and there's only access to the original field's data and the current's field, so
        # if more than one action is done, the entire list will be checked again... This is ugly but I could'nt find a better way to achieve it :(
        #
        # Behaviour:
        #   Get added IDs (comparing which current IDs are not within old IDs)
        #       Recursive:
        #           If an added ID has a parent:
        #               Add the parent if not present.
        #           If an added ID has childs:
        #               Must add all its childs but only if never added before (there's no 
        #               childs already added, otherwise could be deleted previously, and shall 
        #               not be added again)
        #
        #   Get removed IDs (comparing which old IDs are not within current IDs)
        #       Recursive:
        #           If a removed ID has children:
        #               Must remove all its children. 

        # TODO: develop. 
        for rec in self:	               
            #new_sub = list(map(lambda x: x.subject_id, rec.enrollment_ids))                          
            enrollments = {}
            for item in rec.enrollment_ids:
                enrollments[item.subject_id] = item

            new_sub = list(enrollments.keys())
            old_sub = list(map(lambda x: x.subject_id, rec._origin.enrollment_ids))

            added = []
            for sub in new_sub:
                if sub not in old_sub:
                    added.append(sub)
            
            removed = []
            for sub in old_sub:
                if sub not in new_sub:
                    removed.append(sub)

            ignore = []
            for sub in added:
                if sub.subject_id in added:
                    # The current one and also its parents should be ignored.                    
                    while sub:
                        if not sub in ignore: ignore.append(sub)
                        sub = sub.subject_id

            for sub in added:
                # For every added enrollment: 
                # If has parent, it must be added (recursive) if not present.
                # If has childs, they must be added (recursive) if no other childs are present.
                if sub not in ignore:
                    if sub.subject_id:
                        #TODO: recursion!
                        rec.write({
                            'enrollment_ids': [(0, 0, {
                                "student_id": rec.id, 
                                "group_id": enrollments[sub].group_id,
                                "subject_id": sub.subject_id.id,      
                            })]
                        })                                                                                 

                    for ch in sub.subject_ids:
                        #TODO: recursion!
                        rec.write({
                            'enrollment_ids': [(0, 0, {
                                "student_id": rec.id, 
                                "group_id": enrollments.get(sub).group_id,
                                "subject_id": ch.id,      
                            })]
                        })   
                        

            # if len(rec.enrollment_ids) < len(rec._origin.enrollment_ids):                
            #     # row removed
            #     old_enroll_ids = list(map(lambda x: x.id, rec._origin.enrollment_ids))
            #     new_enroll_ids = list(map(lambda x: x.id.origin, rec.enrollment_ids))  
            #     for eid in old_enroll_ids:
            #         if eid not in new_enroll_ids:
            #             # remove also the children
            #             # TODO: test
            #             removed = rec.enrollment_ids.search([("id", "=", eid)]) or False  
            #             self._enrollment_populate_descendant(rec, removed)                        
            #             break

            # elif len(rec.enrollment_ids) > len(rec._origin.enrollment_ids):
            #     # row added (updates will be ignored)
            #     # TODO: should be recursive BUT:
            #     #   Adding a child adds all its childs.
            #     #   Adding a parent adds all the ascendants. Adding an ascendant MUST NOT add a descendant.                
            #     new_enroll_ids = list(map(lambda x: x.subject_id.id, rec._origin.enrollment_ids)) 
            #     for en in rec.enrollment_ids:
            #         if not en.id.origin:
            #             # add parent or child                        
            #             if en.subject_id.subject_id:
            #                 #has parent                             
            #                 if en.subject_id.subject_id.id not in new_enroll_ids: 
            #                     rec.write({
            #                         'enrollment_ids': [(0, 0, {
            #                             "student_id": en.student_id.id, 
            #                             "group_id": en.group_id.id,
            #                             "subject_id": en.subject_id.subject_id.id,      
            #                         })]
            #                     })                                 
                        
            #             elif en.subject_id.subject_ids:
            #                 #has children
            #                 for sub in en.subject_id.subject_ids:
            #                     if sub.id not in new_enroll_ids:
            #                         # must be added
            #                         rec.write({
            #                             'enrollment_ids': [(0, 0, {
            #                                 "student_id": en.student_id.id, 
            #                                 "group_id": en.group_id.id,
            #                                 "subject_id": sub.id,      
            #                             })]
            #                         })
            #             break                    
    
    def _enrollment_populate_ascendants(self):
        return

    def _enrollment_populate_descendant(self, rec, removed):
        # TODO: test
        removed_sub_child_ids = list(map(lambda x: x.id, removed.subject_id.subject_ids))
        for en in rec.enrollment_ids:
            if en.subject_id.id in removed_sub_child_ids:
                self._enrollment_populate_descendant(rec, en)
                rec.write({
                    'enrollment_ids': [(2, en.id)]
                })  
        return

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
        