# -*- coding: utf-8 -*-

from odoo import models, fields


class AccountPayment(models.Model):
    _inherit = "account.payment"

    counterpart_partner_id = fields.Many2one("res.partner", string="Counterpart Partner", copy=False,
                                             check_company=True, tracking=True,
                                             domain="['|', ('company_id', '=', False), ('company_id', '=', company_id)]")

    def _prepare_move_line_default_vals(self, write_off_line_vals=None):
        line_vals = super(AccountPayment, self)._prepare_move_line_default_vals(write_off_line_vals)
        if self.counterpart_partner_id:
            if self.payment_type == 'inbound':
                # Receive money.
                counterpart_amount = -self.amount

            elif self.payment_type == 'outbound':
                # Send money.
                counterpart_amount = self.amount
            else:
                counterpart_amount = 0.0

            balance = self.currency_id._convert(counterpart_amount, self.company_id.currency_id, self.company_id,
                                                self.date)

            account_id = self.journal_id.payment_debit_account_id.id if balance < 0.0 else self.journal_id.payment_credit_account_id.id
            for line in line_vals:
                if line["account_id"] == account_id:
                    line["partner_id"] = self.counterpart_partner_id.commercial_partner_id.id
                    break
        return line_vals

    def write(self, vals):
        res = super().write(vals)

        if "counterpart_partner_id" in vals.keys():
            changed_fields = set(vals.keys())
            if not any(field_name in changed_fields for field_name in (
                    'date', 'amount', 'payment_type', 'partner_type', 'payment_reference', 'is_internal_transfer',
                    'currency_id', 'partner_id', 'destination_account_id', 'partner_bank_id',
            )):
                changed_fields.add("partner_id")
                self._synchronize_to_moves(changed_fields)
        return res
