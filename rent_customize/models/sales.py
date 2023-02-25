# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError


class RentalOrder(models.TransientModel):
    _inherit = 'rental.order.wizard'

    def apply(self):
        res = super(RentalOrder, self).apply()
        for rec in self:
            if rec.status == 'return':
                rec.order_id.state = 'termination'
            if rec.status == 'pickup':
                rec.order_id.state = 'occupied'
        return res


class SaleOrder(models.Model):
    _inherit = "sale.order"
    state = fields.Selection([
        ('draft', 'Quotation'),
        ('sent', 'Quotation Sent'),
        ('sale', 'Acceptance'),
        ('done', 'Locked'),
        ('cancel', 'Cancelled'),
        ('occupied', 'Occupied'),
        ('termination', 'Termination'),
    ], string='Status', readonly=True, copy=False, index=True, tracking=3, default='draft')
    @api.depends('state', 'order_line', 'order_line.product_uom_qty', 'order_line.qty_delivered', 'order_line.qty_returned')
    def _compute_rental_status(self):
        # TODO replace multiple assignations by one write?
        for order in self:
            print("XXXXXXXXXXXXXXXXXXXXXX", order.state)
            if order.state in ['sale', 'done', 'occupied', 'termination'] and order.is_rental_order:
                rental_order_lines = order.order_line.filtered('is_rental')
                pickeable_lines = rental_order_lines.filtered(lambda sol: sol.qty_delivered < sol.product_uom_qty)
                returnable_lines = rental_order_lines.filtered(lambda sol: sol.qty_returned < sol.qty_delivered)
                min_pickup_date = min(pickeable_lines.mapped('pickup_date')) if pickeable_lines else 0
                min_return_date = min(returnable_lines.mapped('return_date')) if returnable_lines else 0
                if pickeable_lines and (not returnable_lines or min_pickup_date <= min_return_date):
                    order.rental_status = 'pickup'
                    order.next_action_date = min_pickup_date
                elif returnable_lines:
                    order.rental_status = 'return'
                    order.next_action_date = min_return_date
                else:
                    if order.state != 'termination':
                        order.rental_status = 'returned'
                        order.next_action_date = False
                order.has_pickable_lines = bool(pickeable_lines)
                order.has_returnable_lines = bool(returnable_lines)
            else:
                order.has_pickable_lines = False
                order.has_returnable_lines = False
                order.rental_status = order.state if order.is_rental_order else False
                order.next_action_date = False

    def action_pickup(self):
        self.write({'state': 'occupied', 'rental_status': 'return'})

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
