from odoo import models, fields, api


class AccountPayment(models.Model):
    _inherit = 'account.payment'

    analytic_account_id = fields.Many2one(
        'account.analytic.account',
        string='الحساب التحليلي',
        readonly=True,
        readonly="state != 'draft'"
    )
    analytic_tag_ids = fields.Many2many(
        'account.analytic.tag',
        string='الوسوم التحليلية',
        readonly=True,
        readonly="state != 'draft'"
    )

    def _prepare_move_line_default_vals(self, write_off_line_vals=None):
        """Override to include analytic account and tags in move lines"""
        res = super(AccountPayment, self)._prepare_move_line_default_vals(write_off_line_vals)

        for line in res:
            if self.analytic_account_id:
                line['analytic_account_id'] = self.analytic_account_id.id
            if self.analytic_tag_ids:
                line['analytic_tag_ids'] = [(6, 0, self.analytic_tag_ids.ids)]

        return res
