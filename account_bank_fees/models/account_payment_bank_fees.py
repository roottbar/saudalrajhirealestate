# -*- coding: utf-8 -*-
# Odoo 18.0 Compatible - Updated by roottbar

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError


class AccountPaymentBankFees(models.Model):
    _name = "account.payment.bank.fees"
    _description = "Account Payment Bank Fees"

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
    account_payment_id = fields.Many2one("account.payment", string="Payment", required=True, ondelete="cascade")
    currency_id = fields.Many2one("res.currency", compute="_compute_currency", string="Currency")
    amount_untaxed = fields.Monetary(string="Subtotal", compute="_compute_total", store=True, readonly=True)
    amount_tax = fields.Monetary(string="Amount Tax", compute="_compute_total", store=True, readonly=True)
    amount_total = fields.Monetary(string="Amount Total", compute="_compute_total", store=True, readonly=True)

    @api.depends("amount", "type", "taxes_ids", "account_payment_id.amount", "account_payment_id.partner_id",
                 "account_payment_id.currency_id")
    def _compute_total(self):
        for payment_bank_fees in self:
            account_payment = payment_bank_fees.account_payment_id
            if payment_bank_fees.type == "percentage":
                amount_payment = account_payment.amount
                if payment_bank_fees.currency_id != account_payment.currency_id:
                    amount_payment = payment_bank_fees.currency_id._convert(amount_payment, account_payment.currency_id,
                                                                            account_payment.company_id,
                                                                            account_payment.date)
                amount_untaxed = amount_payment * payment_bank_fees.amount / 100
            else:
                amount_untaxed = payment_bank_fees.amount

            # compute fees amount
            taxes = payment_bank_fees.taxes_ids.compute_all(amount_untaxed, payment_bank_fees.currency_id,
                                                            partner=account_payment.partner_id)
            amount_tax = sum(t.get('amount', 0.0) for t in taxes.get('taxes', []))

            payment_bank_fees.amount_untaxed = amount_untaxed
            payment_bank_fees.amount_tax = amount_tax
            payment_bank_fees.amount_total = amount_untaxed + amount_tax

    def _compute_currency(self):
        for payment_bank_fees in self:
            company_currency_id = payment_bank_fees.account_payment_id.company_id.currency_id
            journal_id = payment_bank_fees.account_payment_id.journal_id
            payment_bank_fees.currency_id = journal_id.currency_id or company_currency_id

    @api.constrains("amount", "type")
    def _check_amount(self):
        for payment_bank_fees in self:
            if payment_bank_fees.amount <= 0:
                raise ValidationError(_("Amount must be positive"))

            if payment_bank_fees.type == "percentage" and payment_bank_fees.amount > 100:
                raise ValidationError(_("Amount percentage must be between 0 and 100"))

    def _prepare_journal_item(self):
        account_payment = self.account_payment_id
        balance = self.currency_id._convert(self.amount_untaxed, account_payment.company_id.currency_id,
                                            account_payment.company_id, account_payment.date)
        return {
            "name": self.name,
            "date_maturity": account_payment.date,
            "amount_currency": self.amount_untaxed,
            "currency_id": self.currency_id.id,
            "account_id": self.account_id.id,
            "partner_id": account_payment.partner_id.id,
            "debit": balance,
            "credit": 0,
            "tax_ids": [(6, 0, self.taxes_ids.ids)],
            "payment_bank_fees_id": self.id
        }

    @api.model
    def _prepare_journal_item_tax(self, tax, tax_vals, account, amount_tax, amount_currency_tax):
        account_payment = self.account_payment_id

        vals = {
            "name": tax.name,
            "account_id": account.id,
            "partner_id": account_payment.partner_id.id,
            "currency_id": self.currency_id.id,
            "amount_currency": amount_currency_tax,
            "debit": amount_tax,
            "credit": 0,
            "date_maturity": account_payment.date,
            "tax_ids": [(6, 0, tax_vals['tax_ids'])],
            "tax_tag_ids": [(6, 0, tax_vals['tag_ids'])],
            "tax_repartition_line_id": tax_vals['tax_repartition_line_id'],
            "payment_bank_fees_id": self.id
        }

        return vals


class AccountMoveLine(models.Model):
    _inherit = "account.move.line"

    payment_bank_fees_id = fields.Many2one("account.payment.bank.fees", "Payment Bank Fees", copy=False)


class AccountPayment(models.Model):
    _inherit = "account.payment"

    payment_bank_fees_ids = fields.One2many("account.payment.bank.fees", "account_payment_id", "Payment Bank Fees")
    journal_type = fields.Selection(related="journal_id.type", string="Journal Type", readonly=True, store=True)
    total_fees = fields.Monetary(string="Total Fees", compute="_compute_total_fees", store=True, readonly=True,
                                 currency_field="company_currency_id")

    @api.depends("payment_bank_fees_ids.amount_total", "currency_id", "company_id", "date")
    def _compute_total_fees(self):
        for payment in self:
            total_fees = 0
            for payment_bank_fees in payment.payment_bank_fees_ids:
                amount_fees = payment_bank_fees.amount_total
                if payment_bank_fees.currency_id != payment.company_currency_id:
                    amount_fees = payment_bank_fees.currency_id._convert(amount_fees, payment.company_currency_id,
                                                                         payment.company_id, payment.date)

                total_fees += amount_fees
            payment.total_fees = total_fees

    @api.onchange("journal_id")
    def onchange_journal(self):
        self.payment_bank_fees_ids = False

        if self.journal_id.type == "bank" and self.journal_id.account_bank_fees_ids:
            payment_bank_fees = []
            for account_bank_fees in self.journal_id.account_bank_fees_ids:
                vals = {
                    "account_id": account_bank_fees.account_id.id,
                    "name": account_bank_fees.name,
                    "type": account_bank_fees.type,
                    "amount": account_bank_fees.amount,
                    "taxes_ids": [(6, 0, account_bank_fees.taxes_ids.ids)]
                }
                payment_bank_fees.append((0, 0, vals))
            self.payment_bank_fees_ids = payment_bank_fees

    def _seek_for_lines(self):
        liquidity_lines, counterpart_lines, writeoff_lines = super(AccountPayment, self)._seek_for_lines()

        # remove bank fees line from writeoff lines
        writeoff_lines = writeoff_lines.filtered(lambda l: not l.payment_bank_fees_id)

        return liquidity_lines, counterpart_lines, writeoff_lines

    def _prepare_journal_item_bank_fees(self):
        lines = []

        for payment_bank_fees in self.payment_bank_fees_ids:
            lines.append((0, 0, payment_bank_fees._prepare_journal_item()))

            # add taxes
            if payment_bank_fees.taxes_ids:
                taxes = payment_bank_fees.taxes_ids._origin.compute_all(payment_bank_fees.amount_untaxed,
                                                                        self.currency_id, partner=self.partner_id)

                for tax_vals in taxes.get('taxes', []):
                    amount_tax = tax_vals.get('amount', 0.0)
                    amount_currency_tax = amount_tax
                    amount_tax = payment_bank_fees.currency_id._convert(amount_tax, self.company_id.currency_id,
                                                                        self.company_id, self.date)

                    tax_repartition_line = self.env['account.tax.repartition.line'].browse(
                        tax_vals['tax_repartition_line_id'])
                    tax = tax_repartition_line.invoice_tax_id or tax_repartition_line.refund_tax_id
                    if tax.tax_exigibility == 'on_payment':
                        account = tax.cash_basis_transition_account_id
                    else:
                        account = tax_repartition_line.account_id

                    lines.append((0, 0, payment_bank_fees._prepare_journal_item_tax(tax, tax_vals, account, amount_tax,
                                                                                    amount_currency_tax)))

        return lines

    def action_post(self):
        # add journal items bank fees before confirm payment
        lines = self._prepare_journal_item_bank_fees()

        if lines:
            # add total fees for journal item to other side

            move_line_id = self.mapped("move_id.line_ids").filtered(
                lambda l: l.account_id in [self.journal_id.payment_credit_account_id,
                                           self.journal_id.payment_debit_account_id])

            if self.payment_type == "inbound":
                total_fees = -self.total_fees
            elif self.payment_type == "outbound":
                total_fees = self.total_fees
            else:
                total_fees = 0.0

            amount_currency = self.company_currency_id._convert(total_fees, self.currency_id, self.company_id,
                                                                self.date)
            line_vals = {
                "amount_currency": move_line_id.amount_currency + amount_currency,
                "debit": total_fees < 0.0 and move_line_id.debit + total_fees or 0.0,
                "credit": total_fees > 0.0 and move_line_id.credit + total_fees or 0.0
            }

            lines.append((1, move_line_id.id, line_vals))
            self.move_id.with_context(skip_account_move_synchronization=True).write({"line_ids": lines})

        return super(AccountPayment, self).action_post()

    def action_draft(self):
        res = super(AccountPayment, self).action_draft()
        # remove journal items of fees
        lines = []
        move_lines = self.mapped("move_id.line_ids")
        for delete_aml in move_lines.filtered(lambda l: l.payment_bank_fees_id):
            lines.append((3, delete_aml.id))

        if lines:
            move_line_id = self.mapped("move_id.line_ids").filtered(
                lambda l: l.account_id in [self.journal_id.payment_credit_account_id,
                                           self.journal_id.payment_debit_account_id])

            if self.payment_type == "inbound":
                total_fees = self.total_fees
            elif self.payment_type == "outbound":
                total_fees = -self.total_fees
            else:
                total_fees = 0.0

            amount_currency = self.company_currency_id._convert(total_fees, self.currency_id, self.company_id,
                                                                self.date)
            line_vals = {
                "amount_currency": move_line_id.amount_currency + amount_currency,
                "debit": total_fees > 0.0 and move_line_id.debit + total_fees or 0.0,
                "credit": total_fees < 0.0 and move_line_id.credit + total_fees or 0.0
            }
            lines.append((1, move_line_id.id, line_vals))
            self.move_id.write({"line_ids": lines})

        return res
