# -*- coding: utf-8 -*-

from odoo import models, fields, api
from odoo.addons import decimal_precision as dp


class PurchaseOrderLine(models.Model):
    _inherit = 'purchase.order.line'

    # Override fields with increased decimal precision
    price_unit = fields.Float(
        'Unit Price',
        required=True,
        digits='Purchase Price 4 Decimals'
    )
    
    product_qty = fields.Float(
        string='Quantity',
        digits='Purchase Quantity 4 Decimals',
        required=True
    )
    
    price_subtotal = fields.Monetary(
        compute='_compute_amount',
        string='Subtotal',
        store=True,
        digits='Purchase Price 4 Decimals'
    )
    
    price_total = fields.Monetary(
        compute='_compute_amount',
        string='Total',
        store=True,
        digits='Purchase Price 4 Decimals'
    )
    
    @api.depends('product_qty', 'price_unit', 'taxes_id')
    def _compute_amount(self):
        """Compute the amounts of the PO line with 4 decimal precision."""
        for line in self:
            vals = line._prepare_compute_all_values()
            taxes = line.taxes_id.compute_all(
                vals['price_unit'],
                vals['currency_id'],
                vals['product_qty'],
                product=vals['product'],
                partner=vals['partner']
            )
            line.update({
                'price_tax': sum(t.get('amount', 0.0) for t in taxes.get('taxes', [])),
                'price_total': taxes['total_included'],
                'price_subtotal': taxes['total_excluded'],
            })

    def _prepare_compute_all_values(self):
        """Prepare values for tax computation with proper precision."""
        self.ensure_one()
        return {
            'price_unit': self.price_unit,
            'currency_id': self.order_id.currency_id,
            'product_qty': self.product_qty,
            'product': self.product_id,
            'partner': self.order_id.partner_id,
        }
