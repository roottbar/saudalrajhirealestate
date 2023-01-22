# -*- coding: utf-8 -*-

from odoo import fields, models, api, _
from odoo.addons import decimal_precision as dp
from odoo.exceptions import ValidationError


class ApprovedRejectedRequestFeedingWizard(models.TransientModel):
    _name = 'approved.rejected.request.feeding'
    _description = 'Approved Or Rejected Request Feeding'

    amount = fields.Float("Amount", digits=dp.get_precision('Product Price'))
    reason = fields.Char('Reason', required=True)
    approved_request_feeding = fields.Boolean('Approved Request Feeding')
    journal_id = fields.Many2one('account.journal', string='Payment Journal', domain=[('type', 'in', ('bank', 'cash'))])

    @api.constrains('amount')
    def _check_amount(self):
        if self.amount <= 0:
            raise ValidationError(_("Amount must be greater than zero"))

    @api.model
    def default_get(self, fields):
        res = super(ApprovedRejectedRequestFeedingWizard, self).default_get(fields)

        request_feeding_id = self.env['petty.cash.request.feeding'].browse(self._context['active_id'])
        res.update({'amount': request_feeding_id.amount})

        return res

    def action_rejected(self):
        request_feeding_id = self.env['petty.cash.request.feeding'].browse(self._context['active_id'])

        if request_feeding_id.state == "f_m_approved":
            raise ValidationError(_("Request Feeding already financial manager approved"))
        if request_feeding_id.state == "rejected":
            raise ValidationError(_("Request Feeding already rejected"))

        request_feeding_id.write({'rejected_reason': self.reason,
                                  'state': 'rejected',
                                  'final_current_balance': request_feeding_id.current_balance})
        return True

    @api.model
    def _prepare_journal_entry(self, request_feeding, journal_id, move_lines):
        vals = {
            'date': request_feeding.date,
            'ref': request_feeding.name,
            'journal_id': journal_id,
            'currency_id': request_feeding.currency_id.id,
            'narration': request_feeding.reason,
            'line_ids': move_lines,
            'request_feeding_id': request_feeding.id,
        }
        return vals

    @api.model
    def _prepare_journal_item(self, request_feeding, account_id, debit=0, credit=0):
        vals = {
            'account_id': account_id,
            'currency_id': request_feeding.currency_id.id,
            'debit': debit,
            'credit': credit,
            'date_maturity': request_feeding.date
        }
        return vals

    def action_fm_approved(self):
        request_feeding_id = self.env['petty.cash.request.feeding'].browse(self._context['active_id'])

        if request_feeding_id.state == "f_m_approved":
            raise ValidationError(_("Request Feeding already financial manager approved"))
        if request_feeding_id.state == "rejected":
            raise ValidationError(_("Request Feeding already rejected"))

        if self.amount > request_feeding_id.amount:
            raise ValidationError(_("Invalid amount.\n You can Amount maximum %s" % (request_feeding_id.amount)))

        # final current balance
        request_feeding_id.final_current_balance = request_feeding_id.current_balance

        # create two journal entries for feeding
        account_move_obj = self.env['account.move']
        transfer_account_id = request_feeding_id.company_id.transfer_account_id.id

        # journal entry for payment journal
        move_lines = [(0, 0, self._prepare_journal_item(request_feeding_id, self.journal_id.default_account_id.id,
                                                        credit=self.amount)),
                      (0, 0, self._prepare_journal_item(request_feeding_id, transfer_account_id, self.amount))]
        move = account_move_obj.create(self._prepare_journal_entry(request_feeding_id, self.journal_id.id, move_lines))
        move.action_post()

        # journal entry for feeding journal
        move_lines = [
            (0, 0, self._prepare_journal_item(request_feeding_id, request_feeding_id.account_id.id, self.amount)),
            (0, 0, self._prepare_journal_item(request_feeding_id, transfer_account_id, credit=self.amount))]
        move = account_move_obj.create(
            self._prepare_journal_entry(request_feeding_id, request_feeding_id.journal_id.id, move_lines))
        move.action_post()

        request_feeding_id.write({'approved_reason': self.reason,
                                  'payment_journal_id': self.journal_id.id,
                                  'actual_amount': self.amount,
                                  'state': 'f_m_approved'})
        return True
