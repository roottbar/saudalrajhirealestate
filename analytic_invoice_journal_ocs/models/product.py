from odoo import models, fields


class ProductProduct(models.Model):
    _inherit = 'product.product'

    analytic_account_id = fields.Many2one(
        'account.analytic.account',
        string='الحساب التحليلي الافتراضي',
        company_dependent=True,
        help='الحساب التحليلي الذي سيتم تطبيقه عند استخدام هذا المنتج'
    )


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    analytic_account_id = fields.Many2one(
        'account.analytic.account',
        string='الحساب التحليلي الافتراضي',
        company_dependent=True,
        help='الحساب التحليلي الذي سيتم تطبيقه عند استخدام هذا المنتج'
    )