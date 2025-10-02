# -*- coding: utf-8 -*-

from odoo import fields, models, api, _
from odoo.exceptions import ValidationError


class AnalyticAccountsPettyCashLineConfigWizard(models.TransientModel):
    _name = 'analytic.accounts.petty.cash.line.config'
    _description = 'Analytic Accounts of Petty Cash Line Config'

    analytic_account_ids = fields.Many2many('account.analytic.account', 'analytic_accounts_pc_line_config_rel',
                                            string='Analytic accounts')

    @api.model
    def default_get(self, fields):
        res = super(AnalyticAccountsPettyCashLineConfigWizard, self).default_get(fields)

        analytic_account_ids = self.env["ir.config_parameter"].sudo().get_param('analytic_account_ids', '[]')

        # check analytic accounts exists or not
        analytic_account_ids = self.env['account.analytic.account'].search([('id', 'in', eval(analytic_account_ids))])

        res.update({'analytic_account_ids': [(6, 0, analytic_account_ids.ids)]})

        return res

    def execute(self):
        config_parameters = self.env["ir.config_parameter"].sudo()

        # check if remove analytic accounts from settings that is already used in petty cash
        analytic_account_ids = eval(config_parameters.get_param('analytic_account_ids', '[]'))

        if analytic_account_ids:
            diff_analytic_accounts = list(set(analytic_account_ids) - set(self.analytic_account_ids.ids))

            if diff_analytic_accounts:
                petty_cash_lines = self.env['petty.cash.line'].search(
                    [('analytic_account_id', 'in', diff_analytic_accounts)])

                if petty_cash_lines:
                    raise ValidationError(
                        _(
                            "You cannot delete this analytic accounts from settings,there are already used in petty cash"))

        # update analytic accounts of petty cash line in settings
        config_parameters.set_param("analytic_account_ids", str(self.analytic_account_ids.ids))
        return True
