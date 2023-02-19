from odoo import models, fields


class AccountInvoiceReport(models.Model):
    _inherit = 'account.invoice.report'

    branch_id = fields.Many2one('branch.branch', 'Branch', readonly=True)

    def _select(self):
        return super(AccountInvoiceReport, self)._select() + ", move.branch_id as branch_id"
