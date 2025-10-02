# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError, UserError
import logging

_logger = logging.getLogger(__name__)


class ResPartnerInherit(models.Model):
    """Inherit res.partner to integrate with Ejar platform"""
    _inherit = 'res.partner'

    # Ejar Integration Fields
    is_ejar_integrated = fields.Boolean(string='Is Ejar Integrated', default=False,
                                       help='Check if this partner is integrated with Ejar platform')
    
    # Ejar Entity Types
    ejar_entity_type = fields.Selection([
        ('tenant', 'Tenant'),
        ('landlord', 'Landlord'),
        ('broker', 'Broker'),
        ('vendor', 'Vendor'),
        ('contractor', 'Contractor')
    ], string='Ejar Entity Type', help='Type of entity in Ejar platform')
    
    # Related Ejar Records
    ejar_tenant_id = fields.Many2one('ejar.tenant', string='Ejar Tenant Record',
                                    help='Related Ejar tenant record')
    
    ejar_landlord_id = fields.Many2one('ejar.landlord', string='Ejar Landlord Record',
                                      help='Related Ejar landlord record')
    
    ejar_broker_id = fields.Many2one('ejar.broker', string='Ejar Broker Record',
                                    help='Related Ejar broker record')
    
    # Saudi-specific fields
    national_id = fields.Char(string='National ID', size=10,
                             help='Saudi National ID or Iqama number')
    
    id_type = fields.Selection([
        ('national_id', 'National ID'),
        ('iqama', 'Iqama'),
        ('passport', 'Passport'),
        ('gcc_id', 'GCC ID')
    ], string='ID Type', default='national_id')
    
    passport_number = fields.Char(string='Passport Number')
    nationality_id = fields.Many2one('res.country', string='Nationality')
    
    # Personal Information
    birth_date = fields.Date(string='Birth Date')
    age = fields.Integer(string='Age', compute='_compute_age', store=True)
    gender = fields.Selection([
        ('male', 'Male'),
        ('female', 'Female')
    ], string='Gender')
    
    marital_status = fields.Selection([
        ('single', 'Single'),
        ('married', 'Married'),
        ('divorced', 'Divorced'),
        ('widowed', 'Widowed')
    ], string='Marital Status')
    
    # Contact Information
    mobile_2 = fields.Char(string='Mobile 2')
    whatsapp = fields.Char(string='WhatsApp Number')
    
    # Address Details
    building_number = fields.Char(string='Building Number')
    street_name = fields.Char(string='Street Name')
    district = fields.Char(string='District')
    postal_code = fields.Char(string='Postal Code')
    additional_number = fields.Char(string='Additional Number')
    
    # Emergency Contact
    emergency_contact_name = fields.Char(string='Emergency Contact Name')
    emergency_contact_phone = fields.Char(string='Emergency Contact Phone')
    emergency_contact_relation = fields.Char(string='Emergency Contact Relation')
    
    # Employment Information
    employer_name = fields.Char(string='Employer Name')
    job_title = fields.Char(string='Job Title')
    monthly_income = fields.Monetary(string='Monthly Income')
    employment_type = fields.Selection([
        ('employee', 'Employee'),
        ('self_employed', 'Self Employed'),
        ('business_owner', 'Business Owner'),
        ('retired', 'Retired'),
        ('student', 'Student'),
        ('unemployed', 'Unemployed')
    ], string='Employment Type')
    
    # Financial Information
    bank_name = fields.Char(string='Bank Name')
    iban = fields.Char(string='IBAN')
    
    # Credit Information
    credit_score = fields.Integer(string='Credit Score')
    credit_status = fields.Selection([
        ('excellent', 'Excellent'),
        ('good', 'Good'),
        ('fair', 'Fair'),
        ('poor', 'Poor'),
        ('unknown', 'Unknown')
    ], string='Credit Status', default='unknown')
    
    # Family Information
    family_size = fields.Integer(string='Family Size', default=1)
    children_count = fields.Integer(string='Children Count', default=0)
    
    # Ejar Sync Status
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
                                   help='Automatically sync with Ejar when partner is updated')
    
    # Statistics
    ejar_contracts_count = fields.Integer(string='Ejar Contracts Count',
                                         compute='_compute_ejar_statistics')
    ejar_properties_count = fields.Integer(string='Ejar Properties Count',
                                          compute='_compute_ejar_statistics')
    
    @api.depends('birth_date')
    def _compute_age(self):
        """Calculate age from birth date"""
        today = fields.Date.today()
        for partner in self:
            if partner.birth_date:
                partner.age = today.year - partner.birth_date.year - (
                    (today.month, today.day) < (partner.birth_date.month, partner.birth_date.day)
                )
            else:
                partner.age = 0
    
    def _compute_ejar_statistics(self):
        """Compute Ejar-related statistics"""
        for partner in self:
            contracts_count = 0
            properties_count = 0
            
            if partner.ejar_tenant_id:
                contracts_count += len(partner.ejar_tenant_id.contract_ids)
            
            if partner.ejar_landlord_id:
                contracts_count += len(partner.ejar_landlord_id.contract_ids)
                properties_count += len(partner.ejar_landlord_id.property_ids)
            
            if partner.ejar_broker_id:
                contracts_count += len(partner.ejar_broker_id.contract_ids)
                properties_count += len(partner.ejar_broker_id.property_ids)
            
            partner.ejar_contracts_count = contracts_count
            partner.ejar_properties_count = properties_count
    
    @api.constrains('national_id')
    def _check_national_id(self):
        """Validate Saudi National ID"""
        for partner in self:
            if partner.national_id and partner.id_type == 'national_id':
                if not partner.national_id.isdigit() or len(partner.national_id) != 10:
                    raise ValidationError(_('National ID must be 10 digits'))
                
                # Check for duplicate national ID
                existing = self.search([
                    ('national_id', '=', partner.national_id),
                    ('id', '!=', partner.id)
                ])
                if existing:
                    raise ValidationError(_('National ID already exists for another partner'))
    
    @api.constrains('iban')
    def _check_iban(self):
        """Validate IBAN format"""
        for partner in self:
            if partner.iban:
                # Basic IBAN validation for Saudi Arabia
                if not partner.iban.startswith('SA') or len(partner.iban) != 24:
                    raise ValidationError(_('Invalid Saudi IBAN format. Must start with SA and be 24 characters long'))
    
    @api.constrains('mobile', 'phone', 'mobile_2')
    def _check_phone_numbers(self):
        """Validate phone numbers"""
        for partner in self:
            for field_name in ['mobile', 'phone', 'mobile_2']:
                phone = getattr(partner, field_name)
                if phone:
                    # Remove spaces and special characters
                    clean_phone = ''.join(filter(str.isdigit, phone))
                    
                    # Check Saudi mobile format
                    if field_name in ['mobile', 'mobile_2']:
                        if not (clean_phone.startswith('966') and len(clean_phone) == 12) and \
                           not (clean_phone.startswith('05') and len(clean_phone) == 10):
                            raise ValidationError(_(f'{field_name.title()} must be in Saudi format (05XXXXXXXX or 966XXXXXXXXX)'))
    
    @api.constrains('email')
    def _check_email_format(self):
        """Validate email format"""
        for partner in self:
            if partner.email:
                import re
                email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
                if not re.match(email_pattern, partner.email):
                    raise ValidationError(_('Invalid email format'))
    
    @api.constrains('family_size', 'children_count')
    def _check_family_info(self):
        """Validate family information"""
        for partner in self:
            if partner.family_size < 0:
                raise ValidationError(_('Family size cannot be negative'))
            
            if partner.children_count < 0:
                raise ValidationError(_('Children count cannot be negative'))
            
            if partner.children_count > partner.family_size:
                raise ValidationError(_('Children count cannot exceed family size'))
    
    @api.onchange('is_ejar_integrated')
    def _onchange_is_ejar_integrated(self):
        """Handle Ejar integration flag change"""
        if not self.is_ejar_integrated:
            # Clear Ejar-related fields
            self.ejar_entity_type = False
            self.ejar_tenant_id = False
            self.ejar_landlord_id = False
            self.ejar_broker_id = False
    
    @api.onchange('ejar_entity_type')
    def _onchange_ejar_entity_type(self):
        """Handle entity type change"""
        if self.ejar_entity_type:
            self.is_ejar_integrated = True
            
            # Clear other entity records
            if self.ejar_entity_type != 'tenant':
                self.ejar_tenant_id = False
            if self.ejar_entity_type != 'landlord':
                self.ejar_landlord_id = False
            if self.ejar_entity_type != 'broker':
                self.ejar_broker_id = False
    
    @api.onchange('country_id')
    def _onchange_country(self):
        """Handle country change"""
        if self.country_id:
            # Set nationality same as country if not set
            if not self.nationality_id:
                self.nationality_id = self.country_id
    
    def action_create_ejar_tenant(self):
        """Create Ejar tenant record from partner"""
        self.ensure_one()
        
        if self.ejar_tenant_id:
            raise UserError(_('Ejar tenant record already exists for this partner'))
        
        # Prepare tenant data
        tenant_vals = self._prepare_ejar_tenant_data()
        
        # Create tenant record
        tenant = self.env['ejar.tenant'].create(tenant_vals)
        
        # Link to partner
        self.write({
            'ejar_tenant_id': tenant.id,
            'ejar_entity_type': 'tenant',
            'is_ejar_integrated': True,
        })
        
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'ejar.tenant',
            'res_id': tenant.id,
            'view_mode': 'form',
            'target': 'current',
        }
    
    def action_create_ejar_landlord(self):
        """Create Ejar landlord record from partner"""
        self.ensure_one()
        
        if self.ejar_landlord_id:
            raise UserError(_('Ejar landlord record already exists for this partner'))
        
        # Prepare landlord data
        landlord_vals = self._prepare_ejar_landlord_data()
        
        # Create landlord record
        landlord = self.env['ejar.landlord'].create(landlord_vals)
        
        # Link to partner
        self.write({
            'ejar_landlord_id': landlord.id,
            'ejar_entity_type': 'landlord',
            'is_ejar_integrated': True,
        })
        
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'ejar.landlord',
            'res_id': landlord.id,
            'view_mode': 'form',
            'target': 'current',
        }
    
    def action_create_ejar_broker(self):
        """Create Ejar broker record from partner"""
        self.ensure_one()
        
        if self.ejar_broker_id:
            raise UserError(_('Ejar broker record already exists for this partner'))
        
        # Prepare broker data
        broker_vals = self._prepare_ejar_broker_data()
        
        # Create broker record
        broker = self.env['ejar.broker'].create(broker_vals)
        
        # Link to partner
        self.write({
            'ejar_broker_id': broker.id,
            'ejar_entity_type': 'broker',
            'is_ejar_integrated': True,
        })
        
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'ejar.broker',
            'res_id': broker.id,
            'view_mode': 'form',
            'target': 'current',
        }
    
    def _prepare_ejar_tenant_data(self):
        """Prepare data for Ejar tenant creation"""
        return {
            'name': self.name,
            'partner_id': self.id,
            'national_id': self.national_id,
            'id_type': self.id_type,
            'passport_number': self.passport_number,
            'nationality_id': self.nationality_id.id if self.nationality_id else False,
            'birth_date': self.birth_date,
            'gender': self.gender,
            'marital_status': self.marital_status,
            'phone': self.phone,
            'mobile': self.mobile,
            'email': self.email,
            'address': self._get_full_address(),
            'city': self.city,
            'emergency_contact_name': self.emergency_contact_name,
            'emergency_contact_phone': self.emergency_contact_phone,
            'emergency_contact_relation': self.emergency_contact_relation,
            'employer_name': self.employer_name,
            'job_title': self.job_title,
            'monthly_income': self.monthly_income,
            'employment_type': self.employment_type,
            'bank_name': self.bank_name,
            'iban': self.iban,
            'credit_score': self.credit_score,
            'credit_status': self.credit_status,
            'family_size': self.family_size,
            'children_count': self.children_count,
            'company_id': self.company_id.id,
        }
    
    def _prepare_ejar_landlord_data(self):
        """Prepare data for Ejar landlord creation"""
        return {
            'name': self.name,
            'partner_id': self.id,
            'entity_type': 'company' if self.is_company else 'individual',
            'national_id': self.national_id,
            'commercial_registration': self.vat if self.is_company else False,
            'birth_date': self.birth_date if not self.is_company else False,
            'gender': self.gender if not self.is_company else False,
            'phone': self.phone,
            'mobile': self.mobile,
            'email': self.email,
            'address': self._get_full_address(),
            'city': self.city,
            'bank_name': self.bank_name,
            'iban': self.iban,
            'company_id': self.company_id.id,
        }
    
    def _prepare_ejar_broker_data(self):
        """Prepare data for Ejar broker creation"""
        return {
            'name': self.name,
            'partner_id': self.id,
            'entity_type': 'company' if self.is_company else 'individual',
            'national_id': self.national_id,
            'commercial_registration': self.vat if self.is_company else False,
            'birth_date': self.birth_date if not self.is_company else False,
            'gender': self.gender if not self.is_company else False,
            'phone': self.phone,
            'mobile': self.mobile,
            'email': self.email,
            'address': self._get_full_address(),
            'city': self.city,
            'office_name': self.name if self.is_company else False,
            'office_address': self._get_full_address() if self.is_company else False,
            'bank_name': self.bank_name,
            'iban': self.iban,
            'company_id': self.company_id.id,
        }
    
    def _get_full_address(self):
        """Get formatted full address"""
        address_parts = []
        
        if self.building_number:
            address_parts.append(f"Building {self.building_number}")
        
        if self.street_name:
            address_parts.append(self.street_name)
        elif self.street:
            address_parts.append(self.street)
        
        if self.district:
            address_parts.append(self.district)
        
        if self.city:
            address_parts.append(self.city)
        
        if self.state_id:
            address_parts.append(self.state_id.name)
        
        if self.country_id:
            address_parts.append(self.country_id.name)
        
        return ', '.join(address_parts)
    
    def action_sync_with_ejar(self):
        """Manually sync with Ejar"""
        self.ensure_one()
        
        if not self.is_ejar_integrated:
            raise UserError(_('This partner is not integrated with Ejar'))
        
        try:
            if self.ejar_tenant_id:
                self.ejar_tenant_id.action_register_with_ejar()
            
            if self.ejar_landlord_id:
                self.ejar_landlord_id.action_register_with_ejar()
            
            if self.ejar_broker_id:
                self.ejar_broker_id.action_register_with_ejar()
            
            self.write({
                'ejar_sync_status': 'synced',
                'ejar_sync_date': fields.Datetime.now(),
                'ejar_sync_error': False,
            })
            
            return {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'title': _('Sync Successful'),
                    'message': _('Partner successfully synced with Ejar'),
                    'type': 'success',
                }
            }
            
        except Exception as e:
            self.write({
                'ejar_sync_status': 'error',
                'ejar_sync_error': str(e),
                'ejar_sync_date': fields.Datetime.now(),
            })
            
            raise UserError(_('Sync failed: %s') % str(e))
    
    def action_view_ejar_contracts(self):
        """View Ejar contracts for this partner"""
        self.ensure_one()
        
        contract_ids = []
        
        if self.ejar_tenant_id:
            contract_ids.extend(self.ejar_tenant_id.contract_ids.ids)
        
        if self.ejar_landlord_id:
            contract_ids.extend(self.ejar_landlord_id.contract_ids.ids)
        
        if self.ejar_broker_id:
            contract_ids.extend(self.ejar_broker_id.contract_ids.ids)
        
        if not contract_ids:
            raise UserError(_('No Ejar contracts found for this partner'))
        
        return {
            'type': 'ir.actions.act_window',
            'name': _('Ejar Contracts'),
            'res_model': 'ejar.contract',
            'view_mode': 'tree,form',
            'domain': [('id', 'in', contract_ids)],
            'target': 'current',
        }
    
    def action_view_ejar_properties(self):
        """View Ejar properties for this partner"""
        self.ensure_one()
        
        property_ids = []
        
        if self.ejar_landlord_id:
            property_ids.extend(self.ejar_landlord_id.property_ids.ids)
        
        if self.ejar_broker_id:
            property_ids.extend(self.ejar_broker_id.property_ids.ids)
        
        if not property_ids:
            raise UserError(_('No Ejar properties found for this partner'))
        
        return {
            'type': 'ir.actions.act_window',
            'name': _('Ejar Properties'),
            'res_model': 'ejar.property',
            'view_mode': 'tree,form',
            'domain': [('id', 'in', property_ids)],
            'target': 'current',
        }
    
    @api.model
    def _cron_sync_ejar_partners(self):
        """Cron job to sync pending Ejar partners"""
        pending_partners = self.search([
            ('is_ejar_integrated', '=', True),
            ('ejar_sync_status', 'in', ['not_synced', 'error']),
            ('auto_sync_ejar', '=', True)
        ])
        
        for partner in pending_partners:
            try:
                partner.action_sync_with_ejar()
                _logger.info(f"Successfully synced partner {partner.name} with Ejar")
            except Exception as e:
                _logger.error(f"Failed to sync partner {partner.name} with Ejar: {e}")
    
    def write(self, vals):
        """Override write to handle Ejar field changes"""
        result = super(ResPartnerInherit, self).write(vals)
        
        # Check if Ejar-related fields changed
        ejar_fields = ['name', 'phone', 'mobile', 'email', 'street', 'city', 
                      'national_id', 'birth_date', 'gender', 'marital_status']
        
        if any(field in vals for field in ejar_fields):
            for partner in self:
                if partner.is_ejar_integrated and partner.auto_sync_ejar:
                    # Update related Ejar records
                    if partner.ejar_tenant_id:
                        partner.ejar_tenant_id._update_from_partner()
                    
                    if partner.ejar_landlord_id:
                        partner.ejar_landlord_id._update_from_partner()
                    
                    if partner.ejar_broker_id:
                        partner.ejar_broker_id._update_from_partner()
        
        return result