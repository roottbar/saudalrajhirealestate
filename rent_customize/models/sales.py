# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError


class SaleOrder(models.Model):
    _inherit = "sale.order"

    def action_pickup(self):
        self.write({'rental_status': 'return'})

    def _compute_has_late_lines(self):
        for order in self:
            order.has_late_lines = False

    @api.depends('state', 'amount_total', 'order_contract_invoice', 'order_contract_invoice.status')
    def _get_invoice_status(self):

        for order in self:
            invoice_lines = order.order_contract_invoice.mapped('status')
            if order.amount_total <= 0:
                order.invoice_status = 'no'
            elif any(invoice_status == 'uninvoiced' for invoice_status in invoice_lines) or not invoice_lines:
                order.invoice_status = 'to invoice'
            elif all(invoice_status == 'invoiced' for invoice_status in invoice_lines):
                order.invoice_status = 'invoiced'
