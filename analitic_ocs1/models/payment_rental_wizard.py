from odoo import models, fields, api

class PaymentRentalInvoiceWizard(models.TransientModel):
    _name = 'payment.rental.invoice.wizard'
    _description = 'Add Rental Invoices to Payment'
    
    payment_id = fields.Many2one('account.payment', string='Payment')
    rental_order_id = fields.Many2one('sale.order', string='Rental Order')
    invoice_ids = fields.Many2many(
        'account.move',
        string='Available Invoices',
        domain="[('invoice_origin', '=', rental_order_id.name), ('move_type', 'in', ['out_invoice', 'out_refund']), ('state', '=', 'posted'), ('payment_state', 'in', ['not_paid', 'partial'])]"
    )
    
    def action_add_invoices(self):
        """Add selected invoices to payment"""
        if self.payment_id and self.invoice_ids:
            lines_to_create = []
            for invoice in self.invoice_ids:
                lines_to_create.append((0, 0, {
                    'invoice_id': invoice.id,
                    'selected': True,
                    'payment_amount': 0,  # Will be calculated automatically
                }))
            
            self.payment_id.write({
                'rental_invoice_line_ids': lines_to_create
            })
            
            # Trigger amount distribution
            self.payment_id._onchange_amount_distribution()
        
        return {'type': 'ir.actions.act_window_close'}