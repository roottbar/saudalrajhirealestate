# -*- coding: utf-8 -*-
# Odoo 18.0 Compatible - Updated by roottbar
from odoo import models, fields, api


class ResPartner(models.Model):
    _inherit = "res.partner"

    def _get_domain_accounting_category(self):
        domain = []
        if "default_customer_rank" in self._context.keys():
            domain += [('apply_to_customer', '=', True)]
        if "default_supplier_rank" in self._context.keys():
            domain += [('apply_to_vendor', '=', True)]

        return domain

    partner_account_category_id = fields.Many2one('res.partner.account.category', 'Accounting Category', copy=False,
                                                  domain=_get_domain_accounting_category)

    @api.model
    def default_get(self, fields):
        res = super(ResPartner, self).default_get(fields)

        partner_account_category_parameter = "accounting_category_partner.vendor_account_category_id"
        if "default_customer_rank" in self._context.keys():
            partner_account_category_parameter = "accounting_category_partner.customer_account_category_id"

        partner_account_category_id = self.env["ir.config_parameter"].sudo().get_param(
            partner_account_category_parameter, False)
        res.update(
            {'partner_account_category_id': partner_account_category_id and eval(partner_account_category_id) or False})

        return res

    @api.onchange('partner_account_category_id')
    def _onchange_account_category(self):
        self.property_account_receivable_id = self.partner_account_category_id.account_receivable_id
        self.property_account_payable_id = self.partner_account_category_id.account_payable_id
