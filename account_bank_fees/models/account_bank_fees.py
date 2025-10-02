# -*- coding: utf-8 -*-
# Odoo 18.0 Compatible - Updated by roottbar

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError


class AccountBankFees(models.Model):
    _name = "account.bank.fees"
    _description = "Account Bank Fees"

    name = fields.Char("Label", copy=False)
    account_id = fields.Many2one("account.account", string="Account", required=True,
                                 domain=[("internal_group", "=", "expense")], copy=False)
    type = fields.Selection([
        ("fixed", "Fixed"),
        ("percentage", "Percentage")], string="Type", default="fixed", required=True, copy=False)
    amount = fields.Float(string="Amount", digits="Account", required=True, copy=False)
    taxes_ids = fields.Many2many("account.tax", string="Taxes", copy=False,
                                 domain=[('type_tax_use', '=', 'purchase'), '|', ('active', '=', False),
                                         ('active', '=', True)])
    journal_id = fields.Many2one("account.journal", string="Journal", required=True, ondelete="cascade")

    @api.constrains("amount", "type")
    def _check_amount(self):
        for account_bank_fees in self:
            if account_bank_fees.amount <= 0:
                raise ValidationError(_("Amount must be positive"))

            if account_bank_fees.type == "percentage" and account_bank_fees.amount > 100:
                raise ValidationError(_("Amount percentage must be between 0 and 100"))


class AccountJournal(models.Model):
    _inherit = "account.journal"

    account_bank_fees_ids = fields.One2many("account.bank.fees", "journal_id", "Account Bank Fees")
