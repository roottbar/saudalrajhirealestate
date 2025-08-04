from odoo import models, fields, api


class AccountMove(models.Model):
    _inherit = 'account.move'

    def _prepare_invoice_line_from_product(self, product):
        """تطبيق الحساب التحليلي عند إنشاء بند فاتورة من منتج"""
        res = super()._prepare_invoice_line_from_product(product)
        analytic_account = product.analytic_account_id or product.product_tmpl_id.analytic_account_id
        if analytic_account:
            res['analytic_account_id'] = analytic_account.id
        return res

    def _post(self, soft=True):
        """تطبيق الحساب التحليلي على جميع بنود اليومية عند الترحيل"""
        for move in self:
            # تطبيق على بنود الفاتورة الأصلية
            for line in move.invoice_line_ids.filtered(lambda l: l.product_id):
                analytic_account = line.product_id.analytic_account_id or line.product_id.product_tmpl_id.analytic_account_id
                if analytic_account and not line.analytic_account_id:
                    line.analytic_account_id = analytic_account

            # ترحيل الحسابات التحليلية لبنود اليومية
            for line in move.line_ids:
                if line.product_id and not line.analytic_account_id:
                    analytic_account = line.product_id.analytic_account_id or line.product_id.product_tmpl_id.analytic_account_id
                    if analytic_account:
                        line.analytic_account_id = analytic_account
                elif line.move_id.invoice_line_ids and not line.analytic_account_id:
                    # بنود الضرائب والإقفال تأخذ الحساب التحليلي من أول بند فاتورة
                    first_line = next((l for l in move.invoice_line_ids if l.analytic_account_id), None)
                    if first_line and first_line.analytic_account_id:
                        line.analytic_account_id = first_line.analytic_account_id

        return super()._post(soft)