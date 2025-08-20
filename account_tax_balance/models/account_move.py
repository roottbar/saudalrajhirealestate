# Copyright 2016 Antonio Espinosa <antonio.espinosa@tecnativa.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import _, api, fields, models


class AccountMove(models.Model):
    _inherit = "account.move"

    @api.model
    def _selection_financial_type(self):
        return [
            ("other", _("Other")),
            ("liquidity", _("Liquidity")),
            ("receivable", _("Receivable")),
            ("receivable_refund", _("Receivable refund")),
            ("payable", _("Payable")),
            ("payable_refund", _("Payable refund")),
        ]

    financial_type = fields.Selection(
        selection="_selection_financial_type",
        compute="_compute_financial_type",
        store=True,
        readonly=True,
    )

    @api.depends(
        "line_ids.account_id.account_type",
        "line_ids.balance",
        "line_ids.account_id.user_type_id.type",
    )
    def _compute_financial_type(self):
        def _balance_get(line_ids, account_type_filter):
            return sum(
                line_ids.filtered(
                    lambda x: x.account_id.account_type in account_type_filter
                ).mapped("balance")
            )

        for move in self:
            account_types = move.line_ids.mapped("account_id.account_type")
            
            # تحديد أنواع الحسابات للسيولة (الحسابات النقدية والمصرفية)
            liquidity_types = ['asset_cash', 'asset_bank']
            # تحديد أنواع الحسابات للذمم المدينة
            receivable_types = ['asset_receivable']
            # تحديد أنواع الحسابات للذمم الدائنة
            payable_types = ['liability_payable']
            
            # التحقق من وجود حسابات سيولة
            if any(acc_type in liquidity_types for acc_type in account_types):
                move.financial_type = "liquidity"
            # التحقق من وجود حسابات ذمم دائنة
            elif any(acc_type in payable_types for acc_type in account_types):
                balance = _balance_get(move.line_ids, payable_types)
                move.financial_type = "payable" if balance < 0 else "payable_refund"
            # التحقق من وجود حسابات ذمم مدينة
            elif any(acc_type in receivable_types for acc_type in account_types):
                balance = _balance_get(move.line_ids, receivable_types)
                move.financial_type = "receivable" if balance > 0 else "receivable_refund"
            else:
                move.financial_type = "other"
