from odoo import models, fields, api


class AccountMoveLine(models.Model):
    _inherit = 'account.move.line'

    @api.model
    def default_get(self, fields_list):
        res = super().default_get(fields_list)
        if self._context.get('default_move_type', False) in ('out_invoice', 'out_refund', 'in_invoice', 'in_refund'):
            if 'product_id' in res and not res.get('analytic_account_id'):
                product = self.env['product.product'].browse(res['product_id'])
                analytic_account = product.analytic_account_id or product.product_tmpl_id.analytic_account_id
                if analytic_account:
                    res['analytic_account_id'] = analytic_account.id
        return res