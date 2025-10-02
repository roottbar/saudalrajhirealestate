# -*- coding: utf-8 -*-

from odoo import fields, models, api, _
from odoo.exceptions import ValidationError


class AccountsPettyCashLineConfigWizard(models.TransientModel):
    _name = 'accounts.petty.cash.line.config'
    _description = 'Accounts of Petty Cash Line Config'

    accounts = fields.Many2many('account.account', string='Accounts')

    @api.model
    def default_get(self, fields):
        res = super(AccountsPettyCashLineConfigWizard, self).default_get(fields)

        accounts = self.env["ir.config_parameter"].sudo().get_param('accounts', '[]')

        # check accounts exists or not
        accounts = self.env['account.account'].search([('id', 'in', eval(accounts))])

        res.update({'accounts': [(6, 0, accounts.ids)]})

        return res

    def execute(self):
        config_parameters = self.env["ir.config_parameter"].sudo()

        # check if remove account from settings that is already used in petty cash
        accounts = eval(config_parameters.get_param('accounts', '[]'))

        if accounts:
            diff_accounts = list(set(accounts) - set(self.accounts.ids))

            if diff_accounts:
                petty_cash_lines = self.env['petty.cash.line'].search([('account_id', 'in', diff_accounts)])

                if petty_cash_lines:
                    raise ValidationError(
                        _("You cannot delete this accounts from settings,there are already used in petty cash"))

        # update accounts of petty cash Line in settings
        config_parameters.set_param("accounts", str(self.accounts.ids))
        return True
