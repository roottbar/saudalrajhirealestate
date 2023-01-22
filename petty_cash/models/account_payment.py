# -*- coding: utf-8 -*-
from odoo import models, api


class account_payment(models.Model):
    _inherit = "account.payment"

    @api.model
    def default_get(self, fields):
        rec = super(account_payment, self).default_get(fields)

        if 'feeding_petty_cash' in self._context.keys() and self._context['feeding_petty_cash']:
            user_rule = self.env['petty.cash.user.rule'].search([('user', '=', self.env.user.id)], limit=1)
            rec['destination_account_id'] = user_rule.account_id.id

        return rec
