# -*- coding: utf-8 -*-

from odoo import fields, models, api, _
from odoo.exceptions import ValidationError
from odoo.addons import decimal_precision as dp


class ApprovedCancelPettyCashRequestWizard(models.TransientModel):
    _name = 'approved.cancel.petty.cash.request'
    _description = 'Approved Or Cancel Petty Cash Request'

    amount = fields.Float("Amount", digits=dp.get_precision('Product Price'))
    reason = fields.Char('Reason')
    approved_petty_cash_request = fields.Boolean('Approved Petty Cash Request')

    @api.constrains('amount')
    def _check_amount(self):
        if self.amount <= 0:
            raise ValidationError(_("Amount must be greater than zero"))

    @api.model
    def default_get(self, fields):
        res = super(ApprovedCancelPettyCashRequestWizard, self).default_get(fields)

        petty_cash_request = self.env['petty.cash.request'].browse(self._context['active_id'])
        res.update({'amount': petty_cash_request.amount})

        return res

    def action_cancel(self):
        petty_cash_request = self.env['petty.cash.request'].browse(self._context['active_id'])

        if petty_cash_request.state == "f_m_approved":
            raise ValidationError(_("Petty Cash Request already financial manager approved"))
        if petty_cash_request.state == "cancel":
            raise ValidationError(_("Petty Cash Request already cancel"))

        values = {'state': 'cancel'}
        if self.reason:
            if petty_cash_request.recommends:
                recommends = petty_cash_request.recommends + '\n' + self.reason
            else:
                recommends = self.reason
            values.update({
                'recommends': recommends
            })

        petty_cash_request.write(values)
        return True

    def action_fm_approved(self):

        petty_cash_request = self.env['petty.cash.request'].browse(self._context['active_id'])

        if petty_cash_request.state == "f_m_approved":
            raise ValidationError(_("Petty Cash Request already already financial manager approved"))
        if petty_cash_request.state == "cancel":
            raise ValidationError(_("Petty Cash Request already cancel"))

        if self.amount > petty_cash_request.amount:
            raise ValidationError(_("Invalid amount.\n You can Amount maximum %s" % petty_cash_request.amount))

        values = {'state': 'f_m_approved', 'actual_amount': self.amount}
        if self.reason:
            if petty_cash_request.recommends:
                recommends = petty_cash_request.recommends + '\n' + self.reason
            else:
                recommends = self.reason
            values.update({
                'recommends': recommends
            })

        petty_cash_request.write(values)
        return True
