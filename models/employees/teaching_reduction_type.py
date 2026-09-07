# -*- coding: utf-8 -*-

from odoo import fields, models


class EmsTeachingReductionType(models.Model):
    _name = "ems.teaching_reduction_type"
    _description = "Teaching-hour reduction type: an entitlement (e.g. an age-based reduction) that adds extra weekly teaching hours to a teacher's schedule summary."
    _order = "name"
    _sql_constraints = [
        ('unique_code', 'unique(code)', 'The code must be unique.'),
    ]

    code = fields.Char(string="Code", required=True)
    name = fields.Char(string="Name", translate=True, required=True)
    reduction_hours = fields.Integer(string="Reduction hours", required=True)
    active = fields.Boolean(string="Active", default=True)
