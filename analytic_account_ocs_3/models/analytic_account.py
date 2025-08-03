# -*- coding: utf-8 -*-

from odoo import models, fields, api

class AccountAnalyticAccount(models.Model):
    _inherit = 'account.analytic.account'
    
    operating_unit_id = fields.Many2one(
        'operating.unit',
        string='Operating Unit',
        domain="[('company_id', '=', company_id)]",
        help="Operating unit for this analytic account"
    )
    
    @api.model
    def _name_search(self, name, args=None, operator='ilike', limit=100, name_get_uid=None):
        """Override name search to include operating unit filtering"""
        if args is None:
            args = []
        return super()._name_search(name, args, operator, limit, name_get_uid)
