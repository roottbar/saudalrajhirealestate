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

    @api.depends("line_ids.balance")  # فقط المعتمد الآمن
    def _compute_financial_type(self):
        def _balance_get(line_ids, keywords):
            return sum(
                line.balance
                for line in line_ids
                if any(kw in line.account_id.display_name.lower() for kw in keywords)
            )

        for move in self:
            lines = move.line_ids
            account_names = " ".join(lines.mapped("account_id.display_name")).lower()

            if "cash" in account_names or "bank" in account_names:
                move.financial_type = "liquidity"
            elif "payable" in account_names:
                balance = _balance_get(lines, ["payable"])
                move.financial_type = "payable" if balance < 0 else "payable_refund"
            elif "receivable" in account_names:
                balance = _balance_get(lines, ["receivable"])
                move.financial_type = "receivable" if balance > 0 else "receivable_refund"
            else:
                move.financial_type = "other"
