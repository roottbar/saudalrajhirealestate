# -*- coding: utf-8 -*-
from odoo import models, api


class ResPartner(models.Model):
    _inherit = "res.partner"

    @api.model
    def default_get(self, fields):
        res = super(ResPartner, self).default_get(fields)

        if self._context.get('vendor_petty_cash'):
            petty_cash_vendor_account_category_id = self.env["ir.config_parameter"].sudo().get_param(
                'petty_cash.petty_cash_vendor_account_category_id', False)
            res.update({'partner_account_category_id': petty_cash_vendor_account_category_id and eval(
                petty_cash_vendor_account_category_id) or False})

        return res
