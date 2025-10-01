# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError, UserError
from datetime import datetime, timedelta
import logging

_logger = logging.getLogger(__name__)


class EjarContract(models.Model):
    """Ejar platform contract management"""
    _name = 'ejar.contract'
    _description = 'Ejar Contract'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'create_date desc'
    _rec_name = 'contract_number'

    # Basic Information
    contract_number = fields.Char(string='Contract Number', required=True, copy=False, tracking=True)
    ejar_contract_id = fields.Char(string='Ejar Contract ID', readonly=True, copy=False)
    ejar_reference = fields.Char(string='Ejar Reference', readonly=True, copy=False)
    
    # Related Records
    sale_order_id = fields.Many2one('sale.order', string='Sale Order', ondelete='cascade')
    property_id = fields.Many2one('ejar.property', string='Property', required=True, tracking=True)
    tenant_id = fields.Many2one('ejar.tenant', string='Tenant', required=True, tracking=True)
    landlord_id = fields.Many2one('ejar.landlord', string='Landlord', required=True, tracking=True)
    broker_id = fields.Many2one('ejar.broker', string='Broker', tracking=True)
    
    # Contract Details
    contract_type_id = fields.Many2one('ejar.contract.type', string='Contract Type', required=True)
    start_date = fields.Date(string='Start Date', required=True, tracking=True)
    end_date = fields.Date(string='End Date', required=True, tracking=True)
    duration_months = fields.Integer(string='Duration (Months)', compute='_compute_duration', store=True)
    
    # Financial Information
    monthly_rent = fields.Monetary(string='Monthly Rent', required=True, tracking=True)
    total_rent = fields.Monetary(string='Total Rent', compute='_compute_total_rent', store=True)
    security_deposit = fields.Monetary(string='Security Deposit', tracking=True)
    broker_commission = fields.Monetary(string='Broker Commission', tracking=True)
    
    currency_id = fields.Many2one('res.currency', string='Currency', 
                                  default=lambda self: self.env.company.currency_id)
    
    # Payment Terms
    payment_frequency = fields.Selection([
        ('monthly', 'Monthly'),
        ('quarterly', 'Quarterly'),
        ('semi_annual', 'Semi-Annual'),
        ('annual', 'Annual')
    ], string='Payment Frequency', default='monthly', required=True)
    
    payment_method = fields.Selection([
        ('bank_transfer', 'Bank Transfer'),
        ('check', 'Check'),
        ('cash', 'Cash'),
        ('online', 'Online Payment')
    ], string='Payment Method', default='bank_transfer')
    
    # Contract Status
    state = fields.Selection([
        ('draft', 'Draft'),
        ('pending_approval', 'Pending Approval'),
        ('approved', 'Approved'),
        ('active', 'Active'),
        ('expired', 'Expired'),
        ('terminated', 'Terminated'),
        ('cancelled', 'Cancelled')
    ], string='Status', default='draft', tracking=True)
    
    # Ejar Integration Status
    ejar_status = fields.Selection([
        ('not_submitted', 'Not Submitted'),
        ('submitted', 'Submitted'),
        ('under_review', 'Under Review'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
        ('registered', 'Registered')
    ], string='Ejar Status', default='not_submitted', tracking=True)
    
    # Contract Terms
    terms_and_conditions = fields.Html(string='Terms and Conditions')
    special_conditions = fields.Text(string='Special Conditions')
    renewal_option = fields.Boolean(string='Renewal Option', default=True)
    early_termination_allowed = fields.Boolean(string='Early Termination Allowed')
    early_termination_penalty = fields.Monetary(string='Early Termination Penalty')
    
    # Utilities and Services
    utilities_included = fields.Boolean(string='Utilities Included')
    electricity_included = fields.Boolean(string='Electricity Included')
    water_included = fields.Boolean(string='Water Included')
    internet_included = fields.Boolean(string='Internet Included')
    maintenance_included = fields.Boolean(string='Maintenance Included')
    
    # Legal Information
    legal_representative = fields.Char(string='Legal Representative')
    witness_1 = fields.Char(string='Witness 1')
    witness_2 = fields.Char(string='Witness 2')
    notary_public = fields.Char(string='Notary Public')
    
    # Dates
    signed_date = fields.Date(string='Signed Date', tracking=True)
    submitted_to_ejar_date = fields.Datetime(string='Submitted to Ejar Date', readonly=True)
    ejar_approval_date = fields.Datetime(string='Ejar Approval Date', readonly=True)
    registration_date = fields.Datetime(string='Registration Date', readonly=True)
    
    # Company
    company_id = fields.Many2one('res.company', string='Company', 
                                 default=lambda self: self.env.company)
    operating_unit_id = fields.Many2one('operating.unit', string='Operating Unit')
    
    # Attachments
    contract_attachment_ids = fields.One2many('ir.attachment', 'res_id', 
                                              domain=[('res_model', '=', 'ejar.contract')],
                                              string='Contract Attachments')
    
    # Sync Information
    last_sync_date = fields.Datetime(string='Last Sync Date', readonly=True)
    sync_status = fields.Selection([
        ('pending', 'Pending'),
        ('synced', 'Synced'),
        ('error', 'Error')
    ], string='Sync Status', default='pending')
    sync_error_message = fields.Text(string='Sync Error Message', readonly=True)
    
    @api.depends('start_date', 'end_date')
    def _compute_duration(self):
        """Calculate contract duration in months"""
        for record in self:
            if record.start_date and record.end_date:
                delta = record.end_date - record.start_date
                record.duration_months = round(delta.days / 30.44)  # Average days per month
            else:
                record.duration_months = 0
    
    @api.depends('monthly_rent', 'duration_months')
    def _compute_total_rent(self):
        """Calculate total rent amount"""
        for record in self:
            record.total_rent = record.monthly_rent * record.duration_months
    
    @api.constrains('start_date', 'end_date')
    def _check_dates(self):
        """Validate contract dates"""
        for record in self:
            if record.start_date and record.end_date:
                if record.start_date >= record.end_date:
                    raise ValidationError(_('End date must be after start date'))
                
                # Check minimum duration based on contract type
                if record.contract_type_id and record.duration_months < record.contract_type_id.min_duration_months:
                    raise ValidationError(_('Contract duration is less than minimum required for this contract type'))
                
                if record.contract_type_id and record.duration_months > record.contract_type_id.max_duration_months:
                    raise ValidationError(_('Contract duration exceeds maximum allowed for this contract type'))
    
    @api.constrains('monthly_rent', 'security_deposit')
    def _check_amounts(self):
        """Validate financial amounts"""
        for record in self:
            if record.monthly_rent <= 0:
                raise ValidationError(_('Monthly rent must be greater than zero'))
            
            if record.security_deposit < 0:
                raise ValidationError(_('Security deposit cannot be negative'))
    
    @api.model
    def create(self, vals):
        """Override create to generate contract number"""
        if not vals.get('contract_number'):
            vals['contract_number'] = self.env['ir.sequence'].next_by_code('ejar.contract') or _('New')
        return super(EjarContract, self).create(vals)
    
    def action_submit_to_ejar(self):
        """Submit contract to Ejar platform"""
        self.ensure_one()
        
        if self.ejar_status != 'not_submitted':
            raise UserError(_('Contract has already been submitted to Ejar'))
        
        try:
            # Get Ejar configuration
            config = self.env['ejar.config'].get_active_config()
            
            # Prepare contract data for Ejar API
            contract_data = self._prepare_ejar_contract_data()
            
            # Submit to Ejar API
            api_connector = self.env['ejar.api.connector']
            response = api_connector.submit_contract(contract_data)
            
            if response.get('success'):
                self.write({
                    'ejar_contract_id': response.get('contract_id'),
                    'ejar_reference': response.get('reference'),
                    'ejar_status': 'submitted',
                    'submitted_to_ejar_date': fields.Datetime.now(),
                    'sync_status': 'synced',
                    'sync_error_message': False
                })
                
                # Log activity
                self.message_post(
                    body=_('Contract successfully submitted to Ejar platform. Reference: %s') % response.get('reference'),
                    message_type='notification'
                )
                
                return {
                    'type': 'ir.actions.client',
                    'tag': 'display_notification',
                    'params': {
                        'title': _('Success'),
                        'message': _('Contract submitted to Ejar platform successfully!'),
                        'type': 'success',
                    }
                }
            else:
                raise UserError(_('Failed to submit contract to Ejar: %s') % response.get('error', 'Unknown error'))
                
        except Exception as e:
            self.write({
                'sync_status': 'error',
                'sync_error_message': str(e)
            })
            _logger.error(f"Failed to submit contract {self.contract_number} to Ejar: {e}")
            raise UserError(_('Failed to submit contract to Ejar: %s') % str(e))
    
    def _prepare_ejar_contract_data(self):
        """Prepare contract data for Ejar API submission"""
        return {
            'contract_number': self.contract_number,
            'property': {
                'id': self.property_id.ejar_property_id,
                'address': self.property_id.address,
                'type': self.property_id.property_type_id.code,
            },
            'tenant': {
                'id': self.tenant_id.ejar_tenant_id,
                'national_id': self.tenant_id.national_id,
                'name': self.tenant_id.name,
                'phone': self.tenant_id.phone,
                'email': self.tenant_id.email,
            },
            'landlord': {
                'id': self.landlord_id.ejar_landlord_id,
                'national_id': self.landlord_id.national_id,
                'name': self.landlord_id.name,
                'phone': self.landlord_id.phone,
                'email': self.landlord_id.email,
            },
            'contract_details': {
                'type': self.contract_type_id.code,
                'start_date': self.start_date.isoformat(),
                'end_date': self.end_date.isoformat(),
                'monthly_rent': self.monthly_rent,
                'security_deposit': self.security_deposit,
                'payment_frequency': self.payment_frequency,
                'payment_method': self.payment_method,
            },
            'terms': {
                'renewal_option': self.renewal_option,
                'early_termination_allowed': self.early_termination_allowed,
                'early_termination_penalty': self.early_termination_penalty,
                'utilities_included': self.utilities_included,
                'special_conditions': self.special_conditions,
            }
        }
    
    def action_check_ejar_status(self):
        """Check contract status on Ejar platform"""
        self.ensure_one()
        
        if not self.ejar_contract_id:
            raise UserError(_('Contract has not been submitted to Ejar yet'))
        
        try:
            api_connector = self.env['ejar.api.connector']
            status_data = api_connector.get_contract_status(self.ejar_contract_id)
            
            if status_data.get('success'):
                old_status = self.ejar_status
                new_status = status_data.get('status')
                
                self.write({
                    'ejar_status': new_status,
                    'last_sync_date': fields.Datetime.now(),
                    'sync_status': 'synced',
                    'sync_error_message': False
                })
                
                # Update approval date if status changed to approved
                if new_status == 'approved' and old_status != 'approved':
                    self.ejar_approval_date = fields.Datetime.now()
                
                # Update registration date if status changed to registered
                if new_status == 'registered' and old_status != 'registered':
                    self.registration_date = fields.Datetime.now()
                
                # Log status change
                if old_status != new_status:
                    self.message_post(
                        body=_('Ejar status updated from %s to %s') % (old_status, new_status),
                        message_type='notification'
                    )
                
                return {
                    'type': 'ir.actions.client',
                    'tag': 'display_notification',
                    'params': {
                        'title': _('Status Updated'),
                        'message': _('Contract status updated to: %s') % new_status,
                        'type': 'success',
                    }
                }
            else:
                raise UserError(_('Failed to get contract status from Ejar: %s') % status_data.get('error'))
                
        except Exception as e:
            self.write({
                'sync_status': 'error',
                'sync_error_message': str(e)
            })
            _logger.error(f"Failed to check Ejar status for contract {self.contract_number}: {e}")
            raise UserError(_('Failed to check Ejar status: %s') % str(e))
    
    def action_activate_contract(self):
        """Activate the contract"""
        self.ensure_one()
        
        if self.state != 'approved':
            raise UserError(_('Contract must be approved before activation'))
        
        if self.ejar_status not in ['approved', 'registered']:
            raise UserError(_('Contract must be approved by Ejar before activation'))
        
        self.write({
            'state': 'active',
            'signed_date': fields.Date.today()
        })
        
        # Update related sale order
        if self.sale_order_id:
            self.sale_order_id.write({'state': 'sale'})
        
        self.message_post(
            body=_('Contract activated successfully'),
            message_type='notification'
        )
    
    def action_terminate_contract(self):
        """Terminate the contract"""
        self.ensure_one()
        
        if self.state not in ['active']:
            raise UserError(_('Only active contracts can be terminated'))
        
        self.write({
            'state': 'terminated',
            'end_date': fields.Date.today()
        })
        
        self.message_post(
            body=_('Contract terminated'),
            message_type='notification'
        )
    
    @api.model
    def sync_all_contracts(self):
        """Sync all contracts with Ejar platform"""
        contracts = self.search([
            ('ejar_contract_id', '!=', False),
            ('ejar_status', 'in', ['submitted', 'under_review', 'approved'])
        ])
        
        for contract in contracts:
            try:
                contract.action_check_ejar_status()
            except Exception as e:
                _logger.error(f"Failed to sync contract {contract.contract_number}: {e}")
                continue
    
    def name_get(self):
        """Custom name_get method"""
        result = []
        for record in self:
            name = f"{record.contract_number}"
            if record.property_id:
                name += f" - {record.property_id.name}"
            if record.tenant_id:
                name += f" ({record.tenant_id.name})"
            result.append((record.id, name))
        return result


class EjarContractLine(models.Model):
    """Contract line items for additional services or charges"""
    _name = 'ejar.contract.line'
    _description = 'Ejar Contract Line'
    _order = 'sequence, id'

    contract_id = fields.Many2one('ejar.contract', string='Contract', required=True, ondelete='cascade')
    sequence = fields.Integer(string='Sequence', default=10)
    
    name = fields.Char(string='Description', required=True)
    product_id = fields.Many2one('product.product', string='Product')
    quantity = fields.Float(string='Quantity', default=1.0)
    price_unit = fields.Monetary(string='Unit Price', required=True)
    price_subtotal = fields.Monetary(string='Subtotal', compute='_compute_price_subtotal', store=True)
    
    currency_id = fields.Many2one(related='contract_id.currency_id', string='Currency')
    
    # Service details
    service_type = fields.Selection([
        ('rent', 'Rent'),
        ('deposit', 'Security Deposit'),
        ('commission', 'Commission'),
        ('maintenance', 'Maintenance'),
        ('utilities', 'Utilities'),
        ('insurance', 'Insurance'),
        ('other', 'Other')
    ], string='Service Type', default='other')
    
    is_recurring = fields.Boolean(string='Recurring')
    recurring_frequency = fields.Selection([
        ('monthly', 'Monthly'),
        ('quarterly', 'Quarterly'),
        ('annual', 'Annual')
    ], string='Recurring Frequency')
    
    @api.depends('quantity', 'price_unit')
    def _compute_price_subtotal(self):
        """Calculate line subtotal"""
        for line in self:
            line.price_subtotal = line.quantity * line.price_unit