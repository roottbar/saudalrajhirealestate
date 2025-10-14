# -*- coding: utf-8 -*-

from odoo import models, fields


class ResCompany(models.Model):
    _inherit = 'res.company'

    # Add missing field to prevent QWeb KeyError in document layout preview
    company_registry = fields.Char(string='Company Registry')