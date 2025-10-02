from odoo import models, fields, api


class AccountMoveLine(models.Model):
    _inherit = 'account.move.line'

    def _prepare_payment_counterpart_moves(self):
        """Override to include analytic account and tags from payment to move lines"""
        res = super(AccountMoveLine, self)._prepare_payment_counterpart_moves()

        payment = self.env['account.payment'].search([('move_id', '=', self.move_id.id)], limit=1)
        if payment:
            if payment.analytic_account_id:
                res['analytic_account_id'] = payment.analytic_account_id.id
            if payment.analytic_tag_ids:
                res['analytic_tag_ids'] = [(6, 0, payment.analytic_tag_ids.ids)]

        return res