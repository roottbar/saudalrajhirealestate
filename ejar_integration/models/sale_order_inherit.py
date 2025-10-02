# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError, UserError
import logging

_logger = logging.getLogger(__name__)


class SaleOrderInherit(models.Model):
    """Inherit Sale Order to integrate with Ejar platform"""
    _inherit = 'sale.order'

    # Ejar Integration Fields
    is_ejar_rental = fields.Boolean(string='Is Ejar Rental', default=False,
                                   help='Check if this sale order is related to Ejar rental')
    
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
    
    # Contract Details
    rental_start_date = fields.Date(string='Rental Start Date')
    rental_end_date = fields.Date(string='Rental End Date')
    rental_duration_months = fields.Integer(string='Rental Duration (Months)',
                                           compute='_compute_rental_duration', store=True)
    
    monthly_rent = fields.Monetary(string='Monthly Rent')
    security_deposit = fields.Monetary(string='Security Deposit')
    broker_commission = fields.Monetary(string='Broker Commission')
    
    # Payment Terms
    payment_frequency = fields.Selection([
        ('monthly', 'Monthly'),
        ('quarterly', 'Quarterly'),
        ('semi_annual', 'Semi-Annual'),
        ('annual', 'Annual')
    ], string='Payment Frequency', default='monthly')
    
    advance_payment_months = fields.Integer(string='Advance Payment (Months)', default=1)
    
    # Ejar Status
    ejar_sync_status = fields.Selection([
        ('not_synced', 'Not Synced'),
        ('pending', 'Pending'),
        ('synced', 'Synced'),
        ('error', 'Error')
    ], string='Ejar Sync Status', default='not_synced', readonly=True)
    
    ejar_sync_date = fields.Datetime(string='Last Ejar Sync Date', readonly=True)
    ejar_sync_error = fields.Text(string='Ejar Sync Error', readonly=True)
    
    # Auto-sync
    auto_sync_ejar = fields.Boolean(string='Auto Sync with Ejar', default=True,
                                   help='Automatically sync with Ejar when order is confirmed')
    
    @api.depends('rental_start_date', 'rental_end_date')
    def _compute_rental_duration(self):
        """Calculate rental duration in months"""
        for order in self:
            if order.rental_start_date and order.rental_end_date:
                # Calculate months between dates
                start = order.rental_start_date
                end = order.rental_end_date
                
                months = (end.year - start.year) * 12 + (end.month - start.month)
                if end.day >= start.day:
                    months += 1
                
                order.rental_duration_months = max(months, 0)
            else:
                order.rental_duration_months = 0
    
    @api.constrains('rental_start_date', 'rental_end_date')
    def _check_rental_dates(self):
        """Validate rental dates"""
        for order in self:
            if order.is_ejar_rental and order.rental_start_date and order.rental_end_date:
                if order.rental_end_date <= order.rental_start_date:
                    raise ValidationError(_('Rental end date must be after start date'))
    
    @api.constrains('monthly_rent', 'security_deposit', 'broker_commission')
    def _check_amounts(self):
        """Validate amounts"""
        for order in self:
            if order.is_ejar_rental:
                if order.monthly_rent <= 0:
                    raise ValidationError(_('Monthly rent must be greater than zero'))
                
                if order.security_deposit < 0:
                    raise ValidationError(_('Security deposit cannot be negative'))
                
                if order.broker_commission < 0:
                    raise ValidationError(_('Broker commission cannot be negative'))
    
    @api.onchange('is_ejar_rental')
    def _onchange_is_ejar_rental(self):
        """Handle Ejar rental flag change"""
        if not self.is_ejar_rental:
            # Clear Ejar-related fields
            self.ejar_contract_id = False
            self.ejar_property_id = False
            self.ejar_tenant_id = False
            self.ejar_landlord_id = False
            self.ejar_broker_id = False
            self.rental_start_date = False
            self.rental_end_date = False
            self.monthly_rent = 0
            self.security_deposit = 0
            self.broker_commission = 0
    
    @api.onchange('ejar_property_id')
    def _onchange_ejar_property(self):
        """Handle property change"""
        if self.ejar_property_id:
            # Set property-related information
            property_rec = self.ejar_property_id
            
            # Update order lines with property
            if property_rec.product_template_id:
                # Clear existing lines
                self.order_line = [(5, 0, 0)]
                
                # Add property as order line
                self.order_line = [(0, 0, {
                    'product_id': property_rec.product_template_id.product_variant_id.id,
                    'name': property_rec.name,
                    'product_uom_qty': 1,
                    'price_unit': property_rec.monthly_rent or 0,
                })]
            
            # Set monthly rent from property
            if property_rec.monthly_rent:
                self.monthly_rent = property_rec.monthly_rent
    
    @api.onchange('ejar_tenant_id')
    def _onchange_ejar_tenant(self):
        """Handle tenant change"""
        if self.ejar_tenant_id:
            tenant = self.ejar_tenant_id
            
            # Set customer from tenant's partner
            if tenant.partner_id:
                self.partner_id = tenant.partner_id
            else:
                # Create partner if not exists
                partner_vals = {
                    'name': tenant.name,
                    'phone': tenant.phone or tenant.mobile,
                    'email': tenant.email,
                    'is_company': False,
                    'customer_rank': 1,
                }
                
                if tenant.address:
                    partner_vals['street'] = tenant.address
                if tenant.city:
                    partner_vals['city'] = tenant.city
                
                partner = self.env['res.partner'].create(partner_vals)
                tenant.partner_id = partner.id
                self.partner_id = partner.id
    
    @api.onchange('ejar_landlord_id')
    def _onchange_ejar_landlord(self):
        """Handle landlord change"""
        if self.ejar_landlord_id:
            landlord = self.ejar_landlord_id
            
            # Set additional information from landlord
            if landlord.partner_id and not self.partner_id:
                # If no tenant selected, use landlord as partner
                pass
    
    def action_confirm(self):
        """Override confirm to handle Ejar integration"""
        result = super(SaleOrderInherit, self).action_confirm()
        
        # Handle Ejar rental orders
        for order in self:
            if order.is_ejar_rental and order.auto_sync_ejar:
                try:
                    order._create_or_update_ejar_contract()
                except Exception as e:
                    _logger.error(f"Failed to sync order {order.name} with Ejar: {e}")
                    order.write({
                        'ejar_sync_status': 'error',
                        'ejar_sync_error': str(e),
                        'ejar_sync_date': fields.Datetime.now(),
                    })
        
        return result
    
    def _create_or_update_ejar_contract(self):
        """Create or update Ejar contract from sale order"""
        self.ensure_one()
        
        if not self.is_ejar_rental:
            return
        
        # Prepare contract data
        contract_vals = {
            'sale_order_id': self.id,
            'property_id': self.ejar_property_id.id if self.ejar_property_id else False,
            'tenant_id': self.ejar_tenant_id.id if self.ejar_tenant_id else False,
            'landlord_id': self.ejar_landlord_id.id if self.ejar_landlord_id else False,
            'broker_id': self.ejar_broker_id.id if self.ejar_broker_id else False,
            'start_date': self.rental_start_date,
            'end_date': self.rental_end_date,
            'monthly_rent': self.monthly_rent,
            'security_deposit': self.security_deposit,
            'broker_commission': self.broker_commission,
            'payment_frequency': self.payment_frequency,
            'advance_payment_months': self.advance_payment_months,
            'company_id': self.company_id.id,
        }
        
        # Add contract type if available
        if self.ejar_property_id and self.ejar_property_id.property_type:
            contract_type = self.env['ejar.contract.type'].search([
                ('code', '=', 'residential' if self.ejar_property_id.property_type == 'residential' else 'commercial')
            ], limit=1)
            if contract_type:
                contract_vals['contract_type_id'] = contract_type.id
        
        if self.ejar_contract_id:
            # Update existing contract
            self.ejar_contract_id.write(contract_vals)
            contract = self.ejar_contract_id
        else:
            # Create new contract
            contract = self.env['ejar.contract'].create(contract_vals)
            self.ejar_contract_id = contract.id
        
        # Submit to Ejar if auto-sync is enabled
        try:
            contract.action_submit_to_ejar()
            
            self.write({
                'ejar_sync_status': 'synced',
                'ejar_sync_date': fields.Datetime.now(),
                'ejar_sync_error': False,
            })
            
        except Exception as e:
            self.write({
                'ejar_sync_status': 'error',
                'ejar_sync_error': str(e),
                'ejar_sync_date': fields.Datetime.now(),
            })
            raise
    
    def action_sync_with_ejar(self):
        """Manually sync with Ejar"""
        self.ensure_one()
        
        if not self.is_ejar_rental:
            raise UserError(_('This order is not marked as Ejar rental'))
        
        try:
            self._create_or_update_ejar_contract()
            
            return {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'title': _('Sync Successful'),
                    'message': _('Order successfully synced with Ejar'),
                    'type': 'success',
                }
            }
            
        except Exception as e:
            raise UserError(_('Sync failed: %s') % str(e))
    
    def action_view_ejar_contract(self):
        """View related Ejar contract"""
        self.ensure_one()
        
        if not self.ejar_contract_id:
            raise UserError(_('No Ejar contract found for this order'))
        
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'ejar.contract',
            'res_id': self.ejar_contract_id.id,
            'view_mode': 'form',
            'target': 'current',
        }
    
    def action_create_ejar_contract(self):
        """Create Ejar contract from sale order"""
        self.ensure_one()
        
        if self.ejar_contract_id:
            raise UserError(_('Ejar contract already exists for this order'))
        
        if not self.is_ejar_rental:
            raise UserError(_('This order is not marked as Ejar rental'))
        
        # Validate required fields
        if not self.ejar_property_id:
            raise UserError(_('Property is required for Ejar contract'))
        
        if not self.ejar_tenant_id:
            raise UserError(_('Tenant is required for Ejar contract'))
        
        if not self.rental_start_date or not self.rental_end_date:
            raise UserError(_('Rental dates are required for Ejar contract'))
        
        try:
            self._create_or_update_ejar_contract()
            
            return self.action_view_ejar_contract()
            
        except Exception as e:
            raise UserError(_('Failed to create Ejar contract: %s') % str(e))
    
    def _prepare_invoice_line(self, line):
        """Override to add Ejar-specific invoice line data"""
        vals = super(SaleOrderInherit, self)._prepare_invoice_line(line)
        
        if self.is_ejar_rental:
            # Add Ejar-specific information to invoice line
            vals.update({
                'name': vals.get('name', '') + (
                    f'\nRental Period: {self.rental_start_date} - {self.rental_end_date}'
                    if self.rental_start_date and self.rental_end_date else ''
                )
            })
        
        return vals
    
    @api.model
    def _cron_sync_ejar_orders(self):
        """Cron job to sync pending Ejar orders"""
        pending_orders = self.search([
            ('is_ejar_rental', '=', True),
            ('state', 'in', ['sale', 'done']),
            ('ejar_sync_status', 'in', ['not_synced', 'error']),
            ('auto_sync_ejar', '=', True)
        ])
        
        for order in pending_orders:
            try:
                order._create_or_update_ejar_contract()
                _logger.info(f"Successfully synced order {order.name} with Ejar")
            except Exception as e:
                _logger.error(f"Failed to sync order {order.name} with Ejar: {e}")
    
    def write(self, vals):
        """Override write to handle Ejar field changes"""
        result = super(SaleOrderInherit, self).write(vals)
        
        # Check if Ejar-related fields changed and order is confirmed
        ejar_fields = ['ejar_property_id', 'ejar_tenant_id', 'ejar_landlord_id', 
                      'rental_start_date', 'rental_end_date', 'monthly_rent']
        
        if any(field in vals for field in ejar_fields):
            for order in self:
                if (order.is_ejar_rental and order.state in ['sale', 'done'] and 
                    order.ejar_contract_id and order.auto_sync_ejar):
                    try:
                        order._create_or_update_ejar_contract()
                    except Exception as e:
                        _logger.error(f"Failed to update Ejar contract for order {order.name}: {e}")
        
        return result


class SaleOrderLineInherit(models.Model):
    """Inherit Sale Order Line for Ejar integration"""
    _inherit = 'sale.order.line'

    # Ejar Integration
    is_ejar_rental_line = fields.Boolean(string='Is Ejar Rental Line',
                                        related='order_id.is_ejar_rental', store=True)
    
    ejar_property_id = fields.Many2one('ejar.property', string='Ejar Property',
                                      related='order_id.ejar_property_id', store=True)
    
    # Rental specific fields
    rental_period_start = fields.Date(string='Rental Period Start')
    rental_period_end = fields.Date(string='Rental Period End')
    
    is_security_deposit = fields.Boolean(string='Is Security Deposit', default=False)
    is_broker_commission = fields.Boolean(string='Is Broker Commission', default=False)
    is_maintenance_fee = fields.Boolean(string='Is Maintenance Fee', default=False)
    
    @api.onchange('product_id')
    def _onchange_product_id_ejar(self):
        """Handle product change for Ejar rental lines"""
        if self.is_ejar_rental_line and self.product_id:
            # Check if product is related to a property
            property_rec = self.env['ejar.property'].search([
                ('product_template_id', '=', self.product_id.product_tmpl_id.id)
            ], limit=1)
            
            if property_rec:
                self.rental_period_start = self.order_id.rental_start_date
                self.rental_period_end = self.order_id.rental_end_date
    
    def _prepare_invoice_line(self, **optional_values):
        """Override to add Ejar-specific invoice line data"""
        vals = super(SaleOrderLineInherit, self)._prepare_invoice_line(**optional_values)
        
        if self.is_ejar_rental_line:
            # Add rental period information
            if self.rental_period_start and self.rental_period_end:
                period_info = f'\nRental Period: {self.rental_period_start} - {self.rental_period_end}'
                vals['name'] = vals.get('name', '') + period_info
            
            # Add line type information
            if self.is_security_deposit:
                vals['name'] = vals.get('name', '') + '\n(Security Deposit)'
            elif self.is_broker_commission:
                vals['name'] = vals.get('name', '') + '\n(Broker Commission)'
            elif self.is_maintenance_fee:
                vals['name'] = vals.get('name', '') + '\n(Maintenance Fee)'
        
        return vals