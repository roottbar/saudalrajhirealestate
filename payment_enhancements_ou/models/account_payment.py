from odoo import models, fields


class AccountPayment(models.Model):
    _inherit = 'account.payment'

    sale_order_id = fields.Many2one(
        'sale.order',
        string='أمر المبيعات',
        help='مرجع أمر المبيعات المرتبط بالدفعة (للعملاء).'
    )
    purchase_order_id = fields.Many2one(
        'purchase.order',
        string='أمر الشراء',
        help='مرجع أمر الشراء المرتبط بالدفعة (للموردين).'
    )
    sale_order_name = fields.Char(
        string='رقم أمر المبيعات',
        related='sale_order_id.name',
        store=False,
        readonly=True,
    )
    purchase_order_name = fields.Char(
        string='رقم أمر الشراء',
        related='purchase_order_id.name',
        store=False,
        readonly=True,
    )