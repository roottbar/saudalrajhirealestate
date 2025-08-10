from odoo import models, fields, api

class AccountPayment(models.Model):
    _inherit = 'account.payment'
    
    rental_order_id = fields.Many2one(
        'sale.order',
        string='Rental Order',
        domain="[('is_rental_order', '=', True)]",
        help="Select rental order to auto-populate related invoices"
    )
    
    rental_invoice_ids = fields.One2many(
        'account.move',
        compute='_compute_rental_invoices',
        string='Related Rental Invoices',
        help="Invoices related to the selected rental order"
    )
    
    rental_analytic_line_ids = fields.One2many(
        'account.move.line',
        compute='_compute_rental_analytic_lines',
        string='Rental Invoice Lines with Analytics',
        help="Invoice lines with analytical accounts from rental order"
    )
    
    @api.depends('rental_order_id')
    def _compute_rental_invoices(self):
        """Compute invoices related to selected rental order"""
        for payment in self:
            if payment.rental_order_id:
                invoices = self.env['account.move'].search([
                    ('invoice_origin', '=', payment.rental_order_id.name),
                    ('move_type', 'in', ['out_invoice', 'out_refund']),
                    ('state', '!=', 'cancel')
                ])
                payment.rental_invoice_ids = invoices
            else:
                payment.rental_invoice_ids = False
    
    @api.depends('rental_invoice_ids')
    def _compute_rental_analytic_lines(self):
        """Compute invoice lines with analytical accounts"""
        for payment in self:
            if payment.rental_invoice_ids:
                lines = payment.rental_invoice_ids.mapped('invoice_line_ids').filtered(
                    lambda l: l.analytic_account_id
                )
                payment.rental_analytic_line_ids = lines
            else:
                payment.rental_analytic_line_ids = False
    
    @api.onchange('rental_order_id')
    def _onchange_rental_order_id(self):
        """Update partner when rental order changes"""
        if self.rental_order_id:
            self.partner_id = self.rental_order_id.partner_id
            # Auto-populate reconciled invoices
            self.reconciled_invoice_ids = [(6, 0, self.rental_invoice_ids.ids)]
    
    def _prepare_move_line_default_vals(self, write_off_line_vals=None):
        """Override to add analytical accounts from rental invoices"""
        line_vals_list = super()._prepare_move_line_default_vals(write_off_line_vals)
        
        if self.rental_order_id and self.rental_invoice_ids:
            # Get analytical accounts from rental invoices
            analytic_accounts = self.rental_invoice_ids.mapped('invoice_line_ids.analytic_account_id')
            if analytic_accounts:
                # Apply first analytical account found to payment lines
                main_analytic_account = analytic_accounts[0]
                for line_vals in line_vals_list:
                    if line_vals.get('account_id') and not line_vals.get('analytic_account_id'):
                        line_vals['analytic_account_id'] = main_analytic_account.id
        
        return line_vals_list
    
    def _create_payment_entry(self, amount):
        """Override to ensure analytical accounts are properly set"""
        move = super()._create_payment_entry(amount)
        
        if self.rental_order_id and self.rental_invoice_ids:
            # Update move lines with analytical accounts from invoices
            for move_line in move.line_ids:
                if not move_line.analytic_account_id:
                    # Find matching analytical account from rental invoices
                    for invoice in self.rental_invoice_ids:
                        for inv_line in invoice.invoice_line_ids:
                            if inv_line.analytic_account_id:
                                move_line.analytic_account_id = inv_line.analytic_account_id
                                break
                        if move_line.analytic_account_id:
                            break
        
        return move
