# -*- coding: utf-8 -*-
from num2words import num2words
from odoo import models, fields, api, _
from odoo.exceptions import ValidationError


class PaymentVoucher(models.Model):
    _name = "payment.voucher"
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = "Payment Voucher"

    name = fields.Char(string='Name', readonly=True, copy=False)
    reference = fields.Char("Reference", copy=False)
    payment_date = fields.Date(string='Payment Date', default=fields.Date.today, required=True, copy=False)
    state = fields.Selection([
        ('draft', 'Draft'),
        ('posted', 'Posted')], readonly=True, default='draft', copy=False, string="State")
    payment_method_id = fields.Many2one('account.payment.method', string='Payment Method Type', required=True,
                                        domain=[('payment_type', '=', 'outbound')])
    payment_method_code = fields.Char(related='payment_method_id.code', readonly=True)
    partner_id = fields.Many2one('res.partner', string='Partner', required=True, domain=[('supplier_rank', '>', 0)])
    amount = fields.Monetary(string='Payment Amount', required=True)
    currency_id = fields.Many2one('res.currency', string='Currency', required=True, copy=False,
                                  default=lambda self: self.env.user.company_id.currency_id)
    communication = fields.Char(string='Memo')
    journal_id = fields.Many2one('account.journal', string='Payment Journal', required=True,
                                 domain=[('type', 'in', ('bank', 'cash'))])
    company_id = fields.Many2one('res.company', related='journal_id.company_id', string='Company', readonly=True,
                                 copy=False)
    bank_id = fields.Many2one('res.bank', related='journal_id.bank_id', string='Bank', store=True, readonly=True)
    check_manual_sequencing = fields.Boolean(related='journal_id.check_manual_sequencing', readonly=True)
    check_number = fields.Integer(string="Check Number", readonly=True, copy=False)
    check_number_in_words = fields.Char(string="Check Number", copy=False)
    hide_payment_method = fields.Boolean(compute="_compute_hide_payment_method")
    payment_transaction_id = fields.Many2one('payment.transaction', string="Payment Transaction")
    account_payment_id = fields.Many2one('account.payment', string='Account Payment', copy=False)

    @api.constrains('amount')
    def _check_amount(self):
        if self.amount <= 0:
            raise ValidationError(_("Amount must be greater than zero"))

    @api.constrains('check_number_in_words')
    def _check_number_in_words(self):
        if self.payment_method_code == 'check_printing' and self.check_manual_sequencing:
            payment_voucher_ids = self.search(
                [('id', '!=', self.id), ('check_number_in_words', '=', self.check_number_in_words)])
            if payment_voucher_ids:
                raise ValidationError(_("Number must be unique!"))

    @api.depends('journal_id')
    def _compute_hide_payment_method(self):
        for payment_voucher in self:
            if payment_voucher.journal_id:
                journal_payment_methods = payment_voucher.journal_id.outbound_payment_method_ids
                payment_voucher.hide_payment_method = len(journal_payment_methods) == 1 and journal_payment_methods[
                    0].code == 'manual'

                if payment_voucher.journal_id.check_manual_sequencing:
                    payment_voucher.check_number = payment_voucher.journal_id.check_sequence_id.number_next_actual
            else:
                payment_voucher.hide_payment_method = True

    @api.onchange('journal_id')
    def _onchange_journal(self):
        if self.journal_id:
            self.currency_id = self.journal_id.currency_id or self.company_id.currency_id

            # get first journal payment method and set as default to payment method
            journal_payment_methods = self.journal_id.outbound_payment_method_ids
            self.payment_method_id = journal_payment_methods and journal_payment_methods[0] or False

            if self.journal_id.check_manual_sequencing:
                self.check_number_in_words = self.journal_id.check_sequence_id.number_next_actual

    @api.model
    def create(self, vals):
        if vals['payment_method_id'] == self.sudo().env.ref('account_check_printing.account_payment_method_check').id:
            journal = self.env['account.journal'].browse(vals['journal_id'])
            if journal.check_manual_sequencing:
                vals.update({'check_number': journal.check_sequence_id.next_by_id()})

        petty_cash_request_id = False
        if 'active_model' in self._context.keys() and self._context['active_model'] == 'petty.cash.request':
            petty_cash_request_id = self.env['petty.cash.request'].browse(self._context['active_id'])

            if vals.get('amount') != petty_cash_request_id.actual_amount:
                raise ValidationError(
                    _("Payment Voucher must have the same amount of request %s" % petty_cash_request_id.actual_amount))

        res = super(PaymentVoucher, self).create(vals)

        if petty_cash_request_id and not petty_cash_request_id.payment_voucher_id:
            petty_cash_request_id.write({'payment_voucher_id': res.id})

        return res

    def post(self):
        account_payment = self.env['account.payment']

        for payment_voucher in self:
            if payment_voucher.state == 'posted':
                continue

            name = self.env['ir.sequence'].next_by_code('petty.payment.voucher')

            communication = ''
            if payment_voucher.communication:
                communication += payment_voucher.communication + '/'

            communication += name

            vals = {
                'payment_type': 'outbound',
                'partner_type': 'supplier',
                'partner_id': payment_voucher.partner_id.id,
                'date': payment_voucher.payment_date,
                'amount': payment_voucher.amount,
                'currency_id': payment_voucher.currency_id.id,
                'company_id': payment_voucher.company_id.id,
                'journal_id': payment_voucher.journal_id.id,
                'payment_method_id': payment_voucher.payment_method_id.id,
                'check_number': payment_voucher.check_number,
                'payment_transaction_id': payment_voucher.payment_transaction_id and payment_voucher.payment_transaction_id.id or False,
                'ref': communication,
            }

            payment = account_payment.create(vals)
            payment.action_post()

            payment_voucher.write({'name': name, 'state': 'posted', 'account_payment_id': payment.id})

        return True

    def open_payment(self):
        action = self.sudo().env.ref('account.action_account_payments_payable', False)
        result = action.read()[0]
        result['domain'] = [('id', '=', self.account_payment_id.id)]
        return result

    def print_payment_voucher_report(self):
        return self.sudo().env.ref('petty_cash.action_report_payment_voucher').report_action(self)

    def get_amount_in_text(self):
        # report payment voucher -> get amount in text

        return num2words(self.amount, lang='ar') + ' فقط لا غير'
