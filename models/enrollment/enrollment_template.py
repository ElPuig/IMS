# -*- coding: utf-8 -*-
from odoo import models, fields, api


class SaleOrderTemplate(models.Model):
    _inherit = "sale.order.template"

    # Links the enrollment template (Pack) to a specific study.
    ems_study_id = fields.Many2one(
        'ems.study',
        string="Academic Study",
        help="Define which study this enrollment belongs to."
    )
    # Auxiliary field to see the level (CFGS, Grado, etc.) automatically.
    ems_level_id = fields.Many2one(
        related='ems_study_id.level_id',
        store=True,
        string="Level"
    )

    ems_existing_product_ids = fields.Many2many(
        'product.product',
        compute='_compute_existing_products',
        string="Enrolled Products (Technical)"
    )

    study_year = fields.Integer(string="Study Year")

    @api.depends('sale_order_template_line_ids.product_id')
    def _compute_existing_products(self):
        for template in self:
            valid_lines = template.sale_order_template_line_ids.filtered(lambda l: l.product_id)
            template.ems_existing_product_ids = valid_lines.mapped('product_id')

    @api.model
    def _ems_find_for(self, study, course):
        """The enrollment template for an exact (study, course) pair, or an empty
        recordset if none exists. Used by res.partner._ems_refresh_enrollments_from_template()
        to resolve the template for an already-known course (a student's main group),
        unlike enrollment_proposal_wizard._ems_templates_for() which lists candidates
        across several students/a course floor for a human to pick from in a dropdown.
        Nothing enforces a single template per study+course (see CLAUDE.md's data folder
        conventions); if more than one matches, the first one found is used - there is no
        extra signal here to disambiguate further, same as the wizard falling back to a
        single candidate once nothing else narrows it down."""
        if not (study and course):
            return self.browse()
        return self.search([('ems_study_id', '=', study.id), ('study_year', '=', course)], limit=1)
