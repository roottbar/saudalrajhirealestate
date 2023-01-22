# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError


class SaleOrder(models.Model):
    _inherit = "sale.order"

    discount_type = fields.Selection([
        ("percentage", "Percentage"),
        ("fixed", "Fixed")], string="Discount Type", default="percentage", tracking=True, copy=False)
    discount_total = fields.Float(string='Discount (%)', digits='Account', default=0.0, tracking=True, copy=False)
    amount_discount = fields.Monetary('Amount Discount', compute='_compute_amount_discount', store=True, readonly=True)

    @api.constrains("discount_total", "discount_type")
    def _check_discount_total(self):
        if self.discount_type:
            if self.discount_type == "percentage":
                if self.discount_total < 0 or self.discount_total > 100:
                    raise ValidationError(_("Discount percentage must be between 0 and 100"))
            else:
                if self.discount_total < 0:
                    raise ValidationError(_("Discount must be greater than or equal to zero"))

    @api.depends("order_line.price_unit", "order_line.product_uom_qty", "order_line.discount")
    def _compute_amount_discount(self):
        for order in self:
            amount_discount = 0
            for line in order.order_line.filtered(lambda l: not l.display_type):
                amount_discount += ((line.price_unit * (line.discount or 0.0) / 100.0) * line.product_uom_qty)

            order.amount_discount = amount_discount

    @api.onchange("discount_total", "discount_type")
    def onchange_discount_total(self):
        lines = self.order_line.filtered(lambda l: not l.display_type)
        if len(lines) != 0:
            # set all lines to zero discount before compute discount every line
            for line in lines:
                line.discount = 0

            if self.discount_type == "percentage":
                discount = self.discount_total
            elif self.discount_type == "fixed":
                discount = self.amount_untaxed != 0 and (self.discount_total / self.amount_untaxed) * 100 or 0

                if discount > 100:
                    discount = 0
            else:
                discount = 0

            # set all lines to new discount
            if discount != 0:
                for line in lines:
                    line.discount = discount
