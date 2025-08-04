from odoo import models, fields, api


class AccountMove(models.Model):
    _inherit = 'account.move'

    analytic_account_id = fields.Many2one(
        'account.analytic.account',
        string='الحساب التحليلي الافتراضي',
        readonly=True,
        states={'draft': [('readonly', False)]},
        help='الحساب التحليلي الذي سيتم تطبيقه على بنود الفاتورة عند الترحيل'
    )

    analytic_tag_ids = fields.Many2many(
        'account.analytic.tag',
        string='الوسوم التحليلية الافتراضية',
        readonly=True,
        states={'draft': [('readonly', False)]},
        help='الوسوم التحليلية التي سيتم تطبيقها على بنود الفاتورة عند الترحيل'
    )

    @api.model
    def create(self, vals):
        """تطبيق الحساب التحليلي عند إنشاء الفاتورة"""
        move = super(AccountMove, self).create(vals)
        if move.analytic_account_id or move.analytic_tag_ids:
            for line in move.invoice_line_ids:
                if not line.analytic_account_id:
                    line.analytic_account_id = move.analytic_account_id
                if not line.analytic_tag_ids and move.analytic_tag_ids:
                    line.analytic_tag_ids = [(6, 0, move.analytic_tag_ids.ids)]
        return move

    def _post(self, soft=True):
        """تطبيق الحساب التحليلي عند ترحيل الفاتورة"""
        res = super(AccountMove, self)._post(soft)
        for move in self:
            if move.analytic_account_id or move.analytic_tag_ids:
                for line in move.line_ids:
                    if not line.analytic_account_id:
                        line.analytic_account_id = move.analytic_account_id
                    if not line.analytic_tag_ids and move.analytic_tag_ids:
                        line.analytic_tag_ids = [(6, 0, move.analytic_tag_ids.ids)]
        return res