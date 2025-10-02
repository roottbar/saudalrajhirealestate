# -*- coding: utf-8 -*-

from odoo import models, fields


class Planning(models.Model):
    _inherit = "planning.slot"

    tender_project_id = fields.Many2one("tender.project", string="Project",
                                        domain="[('company_id', '=', company_id), ('allow_planning', '=', True)]",
                                        check_company=True, copy=False)
