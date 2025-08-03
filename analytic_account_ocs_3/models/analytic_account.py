# -*- coding: utf-8 -*-

from odoo import models, fields

class AccountAnalyticAccount(models.Model):
    _inherit = 'account.analytic.account'
    
    operating_unit_id = fields.Many2one(
        'operating.unit',
        string='Operating Unit',
        domain="[('company_id', '=', company_id)]"
    )
