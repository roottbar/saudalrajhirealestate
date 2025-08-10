from odoo import models, fields, api

class AccountPayment(models.Model):
    _inherit = 'account.payment'
    
    rental_order_id = fields.Many2one(
        'sale.order',
        string='Rental Order',
        domain="[('is_rental_order', '=', True)]",
        help="Select rental order to auto-populate related invoices"
    )
    
    rental_invoice_line_ids = fields.One2many(
        'payment.rental.invoice.line',
        'payment_id',
        string='Selected Invoices',
        help="Selected invoices with analytical accounts and amounts"
    )
    
    @api.onchange('rental_order_id')
    def _onchange_rental_order_id(self):
        """Update partner and available invoices when rental order changes"""
        if self.rental_order_id:
            self.partner_id = self.rental_order_id.partner_id
            # Clear existing lines
            self.rental_invoice_line_ids = [(5, 0, 0)]
        else:
            self.rental_invoice_line_ids = [(5, 0, 0)]
    
    @api.onchange('amount', 'rental_invoice_line_ids')
    def _onchange_amount_distribution(self):
        """Distribute payment amount across selected invoices"""
        if self.amount and self.rental_invoice_line_ids:
            selected_lines = self.rental_invoice_line_ids.filtered('selected')
            if selected_lines:
                amount_per_invoice = self.amount / len(selected_lines)
                for line in selected_lines:
                    # Don't exceed the remaining amount of the invoice
                    max_amount = line.invoice_id.amount_residual
                    line.payment_amount = min(amount_per_invoice, max_amount)
    
    def action_post(self):
        """Override to apply analytical accounts and process payments"""
        # Apply analytical accounts to invoice lines before posting
        for rental_line in self.rental_invoice_line_ids.filtered('selected'):
            if rental_line.analytic_account_id:
                # Update invoice lines with the selected analytical account
                invoice_lines = rental_line.invoice_id.invoice_line_ids
                invoice_lines.write({
                    'analytic_account_id': rental_line.analytic_account_id.id
                })
        
        # Call parent method
        result = super().action_post()
        
        # Process partial payments for selected invoices
        self._process_rental_invoice_payments()
        
        return result
    
    def _process_rental_invoice_payments(self):
        """Process payments for selected rental invoices"""
        for rental_line in self.rental_invoice_line_ids.filtered('selected'):
            if rental_line.payment_amount > 0:
                # Create payment entry for this specific invoice
                self._reconcile_invoice_payment(rental_line.invoice_id, rental_line.payment_amount)
    
    def _reconcile_invoice_payment(self, invoice, amount):
        """Reconcile payment with specific invoice"""
        # Find the payment move lines
        payment_lines = self.move_id.line_ids.filtered(
            lambda l: l.account_id == self.destination_account_id and l.credit > 0
        )
        
        # Find the invoice receivable lines
        invoice_lines = invoice.line_ids.filtered(
            lambda l: l.account_id.user_type_id.type == 'receivable' and l.debit > 0
        )
        
        if payment_lines and invoice_lines:
            # Partial reconciliation based on the amount
            (payment_lines + invoice_lines).reconcile()


class PaymentRentalInvoiceLine(models.Model):
    _name = 'payment.rental.invoice.line'
    _description = 'Payment Rental Invoice Line'
    
    payment_id = fields.Many2one('account.payment', string='Payment', ondelete='cascade')
    invoice_id = fields.Many2one('account.move', string='Invoice', required=True)
    selected = fields.Boolean(string='Selected', default=False)
    analytic_account_id = fields.Many2one(
        'account.analytic.account',
        string='Analytical Account',
        help="Analytical account to apply to this invoice"
    )
    payment_amount = fields.Monetary(
        string='Payment Amount',
        currency_field='currency_id',
        help="Amount to pay for this invoice"
    )
    currency_id = fields.Many2one(
        related='payment_id.currency_id',
        string='Currency'
    )
    
    # Invoice information fields
    invoice_date = fields.Date(related='invoice_id.invoice_date', string='Invoice Date')
    amount_total = fields.Monetary(related='invoice_id.amount_total', string='Total Amount')
    amount_residual = fields.Monetary(related='invoice_id.amount_residual', string='Remaining Amount')
    state = fields.Selection(related='invoice_id.state', string='State')
    
    @api.onchange('selected')
    def _onchange_selected(self):
        """Trigger amount redistribution when selection changes"""
        if self.payment_id:
            self.payment_id._onchange_amount_distribution()