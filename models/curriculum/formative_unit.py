# -*- coding: utf-8 -*-

from odoo import models, fields, api

class ims_formative_unit(models.Model):
    _name = "ims.formative_unit"
    _description = "Formative Unit: Is how a set of topics is called in VET studies, a set of FUs composes a Professional Module but each FU must be evaluated separately."

    code = fields.Char(string="Code", required="true")
    acronym = fields.Char(string="Acronym", required="true")
    name = fields.Char(string="Name", required="true")
    notes = fields.Text("Notes")

    professional_module_id = fields.Many2one(string="Professional Module", comodel_name="ims.professional_module")

    teacher_id = fields.Many2one(string="Teacher", comodel_name="hr.employee", domain="[('employee_type', '=', 'teacher')]")
    tracking_ids = fields.One2many(string="Follow-up", comodel_name="ims.tracking", inverse_name="formative_unit_id")

    def name_get(self):
		#Allows displaying a custom name: https://www.odoo.com/documentation/16.0/es/developer/reference/backend/orm.html#odoo.models.Model.name_get

        result = []	
        for rec in self:
            result.append((rec.id, '%s %s %s: %s' % (rec.professional_module_id.study_id.acronym, rec.professional_module_id.acronym, rec.acronym, rec.name)))
            
        return result