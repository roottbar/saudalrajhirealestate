# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError, UserError
import logging

_logger = logging.getLogger(__name__)


class AccountMoveInherit(models.Model):
    """Inherit Account Move (Invoice) to integrate with Ejar platform"""
    _inherit = 'account.move'

    # Ejar Integration Fields
    is_ejar_rental_invoice = fields.Boolean(string='Is Ejar Rental Invoice', default=False,
                                           help='Check if this invoice is related to Ejar rental')
    
    ejar_contract_id = fields.Many2one('ejar.contract', string='Ejar Contract',
                                      help='Related Ejar contract')
    
    ejar_property_id = fields.Many2one('ejar.property', string='Ejar Property',
                                      help='Related Ejar property')
    
    ejar_tenant_id = fields.Many2one('ejar.tenant', string='Ejar Tenant',
                                    help='Related Ejar tenant')
    
    ejar_landlord_id = fields.Many2one('ejar.landlord', string='Ejar Landlord',
                                      help='Related Ejar landlord')
    
    ejar_broker_id = fields.Many2one('ejar.broker', string='Ejar Broker',
                                    help='Related Ejar broker')
    
    # Invoice Type for Ejar
    ejar_invoice_type = fields.Selection([
        ('rent', 'Rent Payment'),
        ('security_deposit', 'Security Deposit'),
        ('broker_commission', 'Broker Commission'),
        ('maintenance', 'Maintenance Fee'),
        ('penalty', 'Penalty Fee'),
        ('utility', 'Utility Bill'),
        ('other', 'Other')
    ], string='Ejar Invoice Type', help='Type of Ejar-related invoice')
    
    # Rental Period
    rental_period_start = fields.Date(string='Rental Period Start')
    rental_period_end = fields.Date(string='Rental Period End')
    
    # Payment Information
    ejar_payment_method = fields.Selection([
        ('bank_transfer', 'Bank Transfer'),
        ('cash', 'Cash'),
        ('check', 'Check'),
        ('credit_card', 'Credit Card'),
        ('online', 'Online Payment')
    ], string='Ejar Payment Method')
    
    ejar_payment_reference = fields.Char(string='Ejar Payment Reference',
                                        help='Payment reference from Ejar platform')
    
    # Ejar Sync Status
    ejar_sync_status = fields.Selection([
        ('not_synced', 'Not Synced'),
        ('pending', 'Pending'),
        ('synced', 'Synced'),
        ('error', 'Error')
    ], string='Ejar Sync Status', default='not_synced', readonly=True)
    
    ejar_sync_date = fields.Datetime(string='Last Ejar Sync Date', readonly=True)
    ejar_sync_error = fields.Text(string='Ejar Sync Error', readonly=True)
    ejar_invoice_id = fields.Char(string='Ejar Invoice ID', readonly=True,
                                 help='Invoice ID from Ejar platform')
    
    # Auto-sync
    auto_sync_ejar = fields.Boolean(string='Auto Sync with Ejar', default=True,
                                   help='Automatically sync with Ejar when invoice is posted')
    
    # Due Date Management
    ejar_due_date = fields.Date(string='Ejar Due Date',
                               help='Due date as per Ejar contract terms')
    
    # Late Payment
    is_late_payment = fields.Boolean(string='Is Late Payment', compute='_compute_is_late_payment')
    days_overdue = fields.Integer(string='Days Overdue', compute='_compute_days_overdue')
    late_fee_amount = fields.Monetary(string='Late Fee Amount')
    
    @api.depends('ejar_due_date', 'payment_state')
    def _compute_is_late_payment(self):
        """Check if payment is late"""
        today = fields.Date.today()
        for invoice in self:
            if (invoice.ejar_due_date and invoice.payment_state != 'paid' and 
                invoice.ejar_due_date < today):
                invoice.is_late_payment = True
            else:
                invoice.is_late_payment = False
    
    @api.depends('ejar_due_date')
    def _compute_days_overdue(self):
        """Calculate days overdue"""
        today = fields.Date.today()
        for invoice in self:
            if invoice.ejar_due_date and invoice.payment_state != 'paid':
                delta = today - invoice.ejar_due_date
                invoice.days_overdue = max(delta.days, 0)
            else:
                invoice.days_overdue = 0
    
    @api.constrains('rental_period_start', 'rental_period_end')
    def _check_rental_period(self):
        """Validate rental period"""
        for invoice in self:
            if (invoice.is_ejar_rental_invoice and 
                invoice.rental_period_start and invoice.rental_period_end):
                if invoice.rental_period_end <= invoice.rental_period_start:
                    raise ValidationError(_('Rental period end date must be after start date'))
    
    @api.onchange('is_ejar_rental_invoice')
    def _onchange_is_ejar_rental_invoice(self):
        """Handle Ejar rental invoice flag change"""
        if not self.is_ejar_rental_invoice:
            # Clear Ejar-related fields
            self.ejar_contract_id = False
            self.ejar_property_id = False
            self.ejar_tenant_id = False
            self.ejar_landlord_id = False
            self.ejar_broker_id = False
            self.ejar_invoice_type = False
            self.rental_period_start = False
            self.rental_period_end = False
    
    @api.onchange('ejar_contract_id')
    def _onchange_ejar_contract(self):
        """Handle contract change"""
        if self.ejar_contract_id:
            contract = self.ejar_contract_id
            
            # Set related fields from contract
            self.ejar_property_id = contract.property_id
            self.ejar_tenant_id = contract.tenant_id
            self.ejar_landlord_id = contract.landlord_id
            self.ejar_broker_id = contract.broker_id
            
            # Set partner from tenant
            if contract.tenant_id and contract.tenant_id.partner_id:
                self.partner_id = contract.tenant_id.partner_id
            
            # Set rental period (current month by default)
            if not self.rental_period_start:
                today = fields.Date.today()
                self.rental_period_start = today.replace(day=1)
                
                # Calculate end of month
                if today.month == 12:
                    next_month = today.replace(year=today.year + 1, month=1, day=1)
                else:
                    next_month = today.replace(month=today.month + 1, day=1)
                
                self.rental_period_end = next_month - fields.timedelta(days=1)
            
            # Set due date based on contract payment terms
            if contract.payment_frequency == 'monthly':
                self.ejar_due_date = self.rental_period_start + fields.timedelta(days=30)
            elif contract.payment_frequency == 'quarterly':
                self.ejar_due_date = self.rental_period_start + fields.timedelta(days=90)
            elif contract.payment_frequency == 'semi_annual':
                self.ejar_due_date = self.rental_period_start + fields.timedelta(days=180)
            elif contract.payment_frequency == 'annual':
                self.ejar_due_date = self.rental_period_start + fields.timedelta(days=365)
    
    def action_post(self):
        """Override post to handle Ejar integration"""
        result = super(AccountMoveInherit, self).action_post()
        
        # Handle Ejar rental invoices
        for invoice in self:
            if invoice.is_ejar_rental_invoice and invoice.auto_sync_ejar:
                try:
                    invoice._sync_with_ejar()
                except Exception as e:
                    _logger.error(f"Failed to sync invoice {invoice.name} with Ejar: {e}")
                    invoice.write({
                        'ejar_sync_status': 'error',
                        'ejar_sync_error': str(e),
                        'ejar_sync_date': fields.Datetime.now(),
                    })
        
        return result
    
    def _sync_with_ejar(self):
        """Sync invoice with Ejar platform"""
        self.ensure_one()
        
        if not self.is_ejar_rental_invoice:
            return
        
        # Get API connector
        connector = self.env['ejar.api.connector'].get_active_connector()
        if not connector:
            raise UserError(_('No active Ejar API connector found'))
        
        # Prepare invoice data for Ejar
        invoice_data = self._prepare_ejar_invoice_data()
        
        try:
            # Submit invoice to Ejar
            response = connector.create_invoice(invoice_data)
            
            if response.get('success'):
                self.write({
                    'ejar_sync_status': 'synced',
                    'ejar_sync_date': fields.Datetime.now(),
                    'ejar_sync_error': False,
                    'ejar_invoice_id': response.get('invoice_id'),
                })
                
                # Log sync success
                self.env['ejar.sync.log'].create_log(
                    operation_type='invoice_create',
                    direction='outbound',
                    status='success',
                    related_model='account.move',
                    related_id=self.id,
                    ejar_id=response.get('invoice_id'),
                    request_data=invoice_data,
                    response_data=response
                )
                
            else:
                error_msg = response.get('error', 'Unknown error')
                self.write({
                    'ejar_sync_status': 'error',
                    'ejar_sync_error': error_msg,
                    'ejar_sync_date': fields.Datetime.now(),
                })
                
                # Log sync error
                self.env['ejar.sync.log'].create_log(
                    operation_type='invoice_create',
                    direction='outbound',
                    status='failed',
                    related_model='account.move',
                    related_id=self.id,
                    request_data=invoice_data,
                    response_data=response,
                    error_message=error_msg
                )
                
                raise UserError(_('Ejar sync failed: %s') % error_msg)
                
        except Exception as e:
            self.write({
                'ejar_sync_status': 'error',
                'ejar_sync_error': str(e),
                'ejar_sync_date': fields.Datetime.now(),
            })
            
            # Log sync error
            self.env['ejar.sync.log'].create_log(
                operation_type='invoice_create',
                direction='outbound',
                status='failed',
                related_model='account.move',
                related_id=self.id,
                request_data=invoice_data,
                error_message=str(e)
            )
            
            raise
    
    def _prepare_ejar_invoice_data(self):
        """Prepare invoice data for Ejar API"""
        self.ensure_one()
        
        # Prepare invoice lines
        lines = []
        for line in self.invoice_line_ids:
            if line.display_type not in ('line_section', 'line_note'):
                lines.append({
                    'description': line.name,
                    'quantity': line.quantity,
                    'unit_price': line.price_unit,
                    'total': line.price_subtotal,
                    'tax_amount': line.price_total - line.price_subtotal,
                })
        
        return {
            'invoice_number': self.name,
            'invoice_date': self.invoice_date.isoformat() if self.invoice_date else None,
            'due_date': self.ejar_due_date.isoformat() if self.ejar_due_date else None,
            'contract_id': self.ejar_contract_id.ejar_contract_id if self.ejar_contract_id else None,
            'property_id': self.ejar_property_id.ejar_property_id if self.ejar_property_id else None,
            'tenant_id': self.ejar_tenant_id.ejar_tenant_id if self.ejar_tenant_id else None,
            'landlord_id': self.ejar_landlord_id.ejar_landlord_id if self.ejar_landlord_id else None,
            'broker_id': self.ejar_broker_id.ejar_broker_id if self.ejar_broker_id else None,
            'invoice_type': self.ejar_invoice_type,
            'rental_period': {
                'start_date': self.rental_period_start.isoformat() if self.rental_period_start else None,
                'end_date': self.rental_period_end.isoformat() if self.rental_period_end else None,
            },
            'amount_total': self.amount_total,
            'amount_tax': self.amount_tax,
            'amount_untaxed': self.amount_untaxed,
            'currency': self.currency_id.name,
            'payment_method': self.ejar_payment_method,
            'payment_reference': self.ejar_payment_reference,
            'lines': lines,
            'notes': self.narration or '',
        }
    
    def action_sync_with_ejar(self):
        """Manually sync with Ejar"""
        self.ensure_one()
        
        if not self.is_ejar_rental_invoice:
            raise UserError(_('This invoice is not marked as Ejar rental invoice'))
        
        if self.state != 'posted':
            raise UserError(_('Invoice must be posted before syncing with Ejar'))
        
        try:
            self._sync_with_ejar()
            
            return {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'title': _('Sync Successful'),
                    'message': _('Invoice successfully synced with Ejar'),
                    'type': 'success',
                }
            }
            
        except Exception as e:
            raise UserError(_('Sync failed: %s') % str(e))
    
    def action_register_payment_ejar(self):
        """Register payment and sync with Ejar"""
        self.ensure_one()
        
        # Open payment registration wizard
        action = self.env.ref('account.action_account_payment_register').read()[0]
        action['context'] = {
            'active_model': 'account.move',
            'active_ids': self.ids,
            'default_ejar_sync': True,
        }
        
        return action
    
    def action_calculate_late_fee(self):
        """Calculate and add late fee"""
        self.ensure_one()
        
        if not self.is_late_payment:
            raise UserError(_('This invoice is not overdue'))
        
        if not self.ejar_contract_id:
            raise UserError(_('No Ejar contract found for late fee calculation'))
        
        # Calculate late fee based on contract terms
        contract = self.ejar_contract_id
        late_fee_rate = contract.late_fee_percentage / 100 if contract.late_fee_percentage else 0.05  # Default 5%
        
        # Calculate late fee amount
        late_fee = self.amount_total * late_fee_rate * (self.days_overdue / 30)  # Monthly rate
        
        if late_fee > 0:
            # Create late fee invoice line
            late_fee_line = self.env['account.move.line'].create({
                'move_id': self.id,
                'name': _('Late Payment Fee (%d days overdue)') % self.days_overdue,
                'quantity': 1,
                'price_unit': late_fee,
                'account_id': self.env['account.account'].search([
                    ('user_type_id.name', '=', 'Income')
                ], limit=1).id,
            })
            
            self.late_fee_amount = late_fee
            
            # Recompute invoice totals
            self._recompute_dynamic_lines()
            
            return {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'title': _('Late Fee Added'),
                    'message': _('Late fee of %s added to invoice') % late_fee,
                    'type': 'success',
                }
            }
    
    def action_view_ejar_contract(self):
        """View related Ejar contract"""
        self.ensure_one()
        
        if not self.ejar_contract_id:
            raise UserError(_('No Ejar contract found for this invoice'))
        
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'ejar.contract',
            'res_id': self.ejar_contract_id.id,
            'view_mode': 'form',
            'target': 'current',
        }
    
    @api.model
    def _cron_sync_ejar_invoices(self):
        """Cron job to sync pending Ejar invoices"""
        pending_invoices = self.search([
            ('is_ejar_rental_invoice', '=', True),
            ('state', '=', 'posted'),
            ('ejar_sync_status', 'in', ['not_synced', 'error']),
            ('auto_sync_ejar', '=', True)
        ])
        
        for invoice in pending_invoices:
            try:
                invoice._sync_with_ejar()
                _logger.info(f"Successfully synced invoice {invoice.name} with Ejar")
            except Exception as e:
                _logger.error(f"Failed to sync invoice {invoice.name} with Ejar: {e}")
    
    @api.model
    def _cron_check_overdue_invoices(self):
        """Cron job to check and notify overdue invoices"""
        overdue_invoices = self.search([
            ('is_ejar_rental_invoice', '=', True),
            ('payment_state', '!=', 'paid'),
            ('ejar_due_date', '<', fields.Date.today())
        ])
        
        for invoice in overdue_invoices:
            # Send overdue notification
            if invoice.ejar_contract_id:
                self.env['ejar.notification'].create({
                    'title': _('Overdue Payment'),
                    'message': _('Invoice %s is overdue by %d days') % (invoice.name, invoice.days_overdue),
                    'notification_type': 'payment_overdue',
                    'priority': 'high',
                    'contract_id': invoice.ejar_contract_id.id,
                    'tenant_id': invoice.ejar_tenant_id.id if invoice.ejar_tenant_id else False,
                    'landlord_id': invoice.ejar_landlord_id.id if invoice.ejar_landlord_id else False,
                })


class AccountMoveLineInherit(models.Model):
    """Inherit Account Move Line for Ejar integration"""
    _inherit = 'account.move.line'

    # Ejar Integration
    is_ejar_rental_line = fields.Boolean(string='Is Ejar Rental Line',
                                        related='move_id.is_ejar_rental_invoice', store=True)
    
    ejar_property_id = fields.Many2one('ejar.property', string='Ejar Property',
                                      related='move_id.ejar_property_id', store=True)
    
    # Line Type for Ejar
    ejar_line_type = fields.Selection([
        ('rent', 'Rent'),
        ('security_deposit', 'Security Deposit'),
        ('broker_commission', 'Broker Commission'),
        ('maintenance', 'Maintenance Fee'),
        ('penalty', 'Penalty Fee'),
        ('utility', 'Utility Bill'),
        ('late_fee', 'Late Fee'),
        ('other', 'Other')
    ], string='Ejar Line Type')
    
    # Rental Period for this line
    rental_period_start = fields.Date(string='Rental Period Start')
    rental_period_end = fields.Date(string='Rental Period End')
    
    @api.onchange('ejar_line_type')
    def _onchange_ejar_line_type(self):
        """Handle line type change"""
        if self.ejar_line_type and self.is_ejar_rental_line:
            # Set default account based on line type
            if self.ejar_line_type == 'rent':
                # Set rental income account
                account = self.env['account.account'].search([
                    ('code', 'like', '4%'),  # Income accounts
                    ('name', 'ilike', 'rent')
                ], limit=1)
                if account:
                    self.account_id = account
            
            elif self.ejar_line_type == 'security_deposit':
                # Set liability account for security deposit
                account = self.env['account.account'].search([
                    ('code', 'like', '2%'),  # Liability accounts
                    ('name', 'ilike', 'deposit')
                ], limit=1)
                if account:
                    self.account_id = account