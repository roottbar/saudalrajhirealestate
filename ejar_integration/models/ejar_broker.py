# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError, UserError
import re
import logging

_logger = logging.getLogger(__name__)


class EjarBroker(models.Model):
    """Ejar platform broker management"""
    _name = 'ejar.broker'
    _description = 'Ejar Broker'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'name'
    _rec_name = 'name'

    # Basic Information
    name = fields.Char(string='Broker Name / Company Name', required=True, tracking=True)
    ejar_broker_id = fields.Char(string='Ejar Broker ID', readonly=True, copy=False)
    
    # License Information
    broker_license_number = fields.Char(string='Broker License Number', required=True, tracking=True)
    license_type = fields.Selection([
        ('individual', 'Individual Broker License'),
        ('company', 'Company Broker License'),
        ('branch', 'Branch License')
    ], string='License Type', required=True, default='individual')
    
    license_issue_date = fields.Date(string='License Issue Date')
    license_expiry_date = fields.Date(string='License Expiry Date')
    license_authority = fields.Char(string='License Authority', default='Ministry of Housing')
    
    # Entity Type
    entity_type = fields.Selection([
        ('individual', 'Individual'),
        ('company', 'Company')
    ], string='Entity Type', required=True, default='individual', tracking=True)
    
    # Identification (Individual)
    national_id = fields.Char(string='National ID / Iqama', tracking=True)
    id_type = fields.Selection([
        ('national_id', 'National ID'),
        ('iqama', 'Iqama'),
        ('passport', 'Passport'),
        ('gcc_id', 'GCC ID')
    ], string='ID Type', default='national_id')
    
    passport_number = fields.Char(string='Passport Number')
    nationality = fields.Many2one('res.country', string='Nationality')
    
    # Company Information
    commercial_registration = fields.Char(string='Commercial Registration Number')
    tax_number = fields.Char(string='Tax Number')
    company_type = fields.Selection([
        ('llc', 'Limited Liability Company'),
        ('joint_stock', 'Joint Stock Company'),
        ('partnership', 'Partnership'),
        ('sole_proprietorship', 'Sole Proprietorship'),
        ('other', 'Other')
    ], string='Company Type')
    
    # Personal Information (Individual)
    birth_date = fields.Date(string='Birth Date', tracking=True)
    age = fields.Integer(string='Age', compute='_compute_age', store=True)
    gender = fields.Selection([
        ('male', 'Male'),
        ('female', 'Female')
    ], string='Gender')
    
    # Contact Information
    phone = fields.Char(string='Phone', required=True, tracking=True)
    mobile = fields.Char(string='Mobile')
    email = fields.Char(string='Email', required=True, tracking=True)
    website = fields.Char(string='Website')
    
    # Address Information
    address = fields.Text(string='Address', required=True)
    city = fields.Char(string='City', required=True)
    district = fields.Char(string='District')
    postal_code = fields.Char(string='Postal Code')
    
    # Office Information
    office_name = fields.Char(string='Office Name')
    office_address = fields.Text(string='Office Address')
    office_phone = fields.Char(string='Office Phone')
    office_email = fields.Char(string='Office Email')
    
    # Legal Representative (for companies)
    legal_representative_name = fields.Char(string='Legal Representative Name')
    legal_representative_id = fields.Char(string='Legal Representative ID')
    legal_representative_phone = fields.Char(string='Legal Representative Phone')
    
    # Financial Information
    currency_id = fields.Many2one('res.currency', string='Currency', 
                                  default=lambda self: self.env.company.currency_id)
    bank_name = fields.Char(string='Bank Name')
    bank_account_number = fields.Char(string='Bank Account Number')
    iban = fields.Char(string='IBAN')
    
    # Commission Structure
    default_commission_rate = fields.Float(string='Default Commission Rate (%)', digits=(5, 2))
    commission_type = fields.Selection([
        ('percentage', 'Percentage of Rent'),
        ('fixed', 'Fixed Amount'),
        ('negotiable', 'Negotiable')
    ], string='Commission Type', default='percentage')
    
    min_commission = fields.Monetary(string='Minimum Commission')
    max_commission = fields.Monetary(string='Maximum Commission')
    
    # Service Areas
    service_area_ids = fields.Many2many('ejar.service.area', string='Service Areas')
    specialization_ids = fields.Many2many('ejar.property.type', string='Property Specializations')
    
    # Contracts and Properties
    contract_ids = fields.One2many('ejar.contract', 'broker_id', string='Contracts')
    property_ids = fields.One2many('ejar.property', 'broker_id', string='Managed Properties')
    landlord_ids = fields.Many2many('ejar.landlord', string='Landlord Clients')
    tenant_ids = fields.Many2many('ejar.tenant', string='Tenant Clients')
    
    # Statistics
    contract_count = fields.Integer(string='Contract Count', compute='_compute_statistics')
    property_count = fields.Integer(string='Property Count', compute='_compute_statistics')
    total_commission_earned = fields.Monetary(string='Total Commission Earned', compute='_compute_statistics')
    active_contracts = fields.Integer(string='Active Contracts', compute='_compute_statistics')
    
    # Status
    state = fields.Selection([
        ('draft', 'Draft'),
        ('verified', 'Verified'),
        ('approved', 'Approved'),
        ('suspended', 'Suspended'),
        ('blacklisted', 'Blacklisted')
    ], string='Status', default='draft', tracking=True)
    
    # Ejar Integration
    ejar_status = fields.Selection([
        ('not_registered', 'Not Registered'),
        ('pending', 'Pending Registration'),
        ('registered', 'Registered'),
        ('rejected', 'Rejected')
    ], string='Ejar Status', default='not_registered', tracking=True)
    
    # Performance Metrics
    rating = fields.Float(string='Rating', digits=(2, 1), readonly=True)
    review_count = fields.Integer(string='Review Count', readonly=True)
    success_rate = fields.Float(string='Success Rate (%)', digits=(5, 2), readonly=True)
    average_deal_time = fields.Integer(string='Average Deal Time (Days)', readonly=True)
    
    # Preferences
    auto_assignment = fields.Boolean(string='Auto Assignment', default=True)
    notification_preferences = fields.Selection([
        ('all', 'All Notifications'),
        ('important', 'Important Only'),
        ('none', 'None')
    ], string='Notification Preferences', default='all')
    
    # Related Records
    partner_id = fields.Many2one('res.partner', string='Related Partner')
    user_id = fields.Many2one('res.users', string='Related User')
    
    # Documents
    document_ids = fields.One2many('ejar.broker.document', 'broker_id', string='Documents')
    
    # Company
    company_id = fields.Many2one('res.company', string='Company', 
                                 default=lambda self: self.env.company)
    operating_unit_id = fields.Many2one('operating.unit', string='Operating Unit')
    
    # Sync Information
    last_sync_date = fields.Datetime(string='Last Sync Date', readonly=True)
    sync_status = fields.Selection([
        ('pending', 'Pending'),
        ('synced', 'Synced'),
        ('error', 'Error')
    ], string='Sync Status', default='pending')
    sync_error_message = fields.Text(string='Sync Error Message', readonly=True)
    
    @api.depends('birth_date')
    def _compute_age(self):
        """Calculate age from birth date"""
        today = fields.Date.today()
        for record in self:
            if record.birth_date and record.entity_type == 'individual':
                record.age = today.year - record.birth_date.year - \
                           ((today.month, today.day) < (record.birth_date.month, record.birth_date.day))
            else:
                record.age = 0
    
    @api.depends('contract_ids', 'property_ids')
    def _compute_statistics(self):
        """Calculate broker statistics"""
        for record in self:
            record.contract_count = len(record.contract_ids)
            record.property_count = len(record.property_ids)
            record.active_contracts = len(record.contract_ids.filtered(lambda c: c.state == 'active'))
            
            # Calculate total commission earned
            total_commission = 0
            for contract in record.contract_ids.filtered(lambda c: c.state in ['active', 'completed']):
                if contract.broker_commission_amount:
                    total_commission += contract.broker_commission_amount
            record.total_commission_earned = total_commission
    
    @api.constrains('broker_license_number')
    def _check_broker_license(self):
        """Validate broker license number"""
        for record in self:
            if record.broker_license_number:
                # Check uniqueness
                existing = self.search([
                    ('broker_license_number', '=', record.broker_license_number),
                    ('id', '!=', record.id)
                ])
                if existing:
                    raise ValidationError(_('A broker with this license number already exists'))
    
    @api.constrains('national_id')
    def _check_national_id(self):
        """Validate national ID format for individuals"""
        for record in self:
            if record.entity_type == 'individual' and record.national_id:
                # Remove spaces and special characters
                clean_id = re.sub(r'[^\d]', '', record.national_id)
                
                if record.id_type == 'national_id':
                    # Saudi National ID validation (10 digits, starts with 1 or 2)
                    if not re.match(r'^[12]\d{9}$', clean_id):
                        raise ValidationError(_('Invalid Saudi National ID format'))
                elif record.id_type == 'iqama':
                    # Iqama validation (10 digits, starts with 1 or 2)
                    if not re.match(r'^[12]\d{9}$', clean_id):
                        raise ValidationError(_('Invalid Iqama number format'))
                
                # Check uniqueness
                existing = self.search([
                    ('national_id', '=', record.national_id),
                    ('id', '!=', record.id)
                ])
                if existing:
                    raise ValidationError(_('A broker with this ID already exists'))
    
    @api.constrains('commercial_registration')
    def _check_commercial_registration(self):
        """Validate commercial registration for companies"""
        for record in self:
            if record.entity_type == 'company' and record.commercial_registration:
                # Saudi CR validation (10 digits)
                clean_cr = re.sub(r'[^\d]', '', record.commercial_registration)
                if not re.match(r'^\d{10}$', clean_cr):
                    raise ValidationError(_('Invalid Commercial Registration format (must be 10 digits)'))
                
                # Check uniqueness
                existing = self.search([
                    ('commercial_registration', '=', record.commercial_registration),
                    ('id', '!=', record.id)
                ])
                if existing:
                    raise ValidationError(_('A broker with this Commercial Registration already exists'))
    
    @api.constrains('phone', 'mobile')
    def _check_phone_numbers(self):
        """Validate phone number formats"""
        for record in self:
            if record.phone:
                # Saudi phone number validation
                clean_phone = re.sub(r'[^\d+]', '', record.phone)
                if not re.match(r'^(\+966|966|0)?[1-9][0-9]{7,8}$', clean_phone):
                    raise ValidationError(_('Invalid phone number format'))
            
            if record.mobile:
                clean_mobile = re.sub(r'[^\d+]', '', record.mobile)
                if not re.match(r'^(\+966|966|0)?[5][0-9]{8}$', clean_mobile):
                    raise ValidationError(_('Invalid mobile number format'))
    
    @api.constrains('email')
    def _check_email(self):
        """Validate email format"""
        for record in self:
            if record.email:
                if not re.match(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$', record.email):
                    raise ValidationError(_('Invalid email format'))
    
    @api.constrains('license_issue_date', 'license_expiry_date')
    def _check_license_dates(self):
        """Validate license dates"""
        for record in self:
            if record.license_issue_date and record.license_expiry_date:
                if record.license_issue_date >= record.license_expiry_date:
                    raise ValidationError(_('License expiry date must be after issue date'))
    
    @api.constrains('default_commission_rate')
    def _check_commission_rate(self):
        """Validate commission rate"""
        for record in self:
            if record.default_commission_rate < 0 or record.default_commission_rate > 100:
                raise ValidationError(_('Commission rate must be between 0 and 100'))
    
    @api.onchange('entity_type')
    def _onchange_entity_type(self):
        """Clear irrelevant fields based on entity type"""
        if self.entity_type == 'company':
            self.birth_date = False
            self.gender = False
            self.passport_number = False
        elif self.entity_type == 'individual':
            self.commercial_registration = False
            self.tax_number = False
            self.company_type = False
            self.legal_representative_name = False
            self.legal_representative_id = False
            self.legal_representative_phone = False
    
    def action_register_with_ejar(self):
        """Register broker with Ejar platform"""
        self.ensure_one()
        
        if self.ejar_status != 'not_registered':
            raise UserError(_('Broker is already registered or pending registration'))
        
        # Validate required documents
        required_docs = ['broker_license', 'national_id']
        if self.entity_type == 'company':
            required_docs.extend(['commercial_registration', 'authorization_letter'])
        
        existing_docs = self.document_ids.mapped('document_type')
        missing_docs = [doc for doc in required_docs if doc not in existing_docs]
        
        if missing_docs:
            raise UserError(_('Missing required documents: %s') % ', '.join(missing_docs))
        
        # Check license validity
        if self.license_expiry_date and self.license_expiry_date < fields.Date.today():
            raise UserError(_('Broker license has expired'))
        
        try:
            # Prepare broker data for Ejar API
            broker_data = self._prepare_ejar_broker_data()
            
            # Submit to Ejar API
            api_connector = self.env['ejar.api.connector']
            response = api_connector.register_broker(broker_data)
            
            if response.get('success'):
                self.write({
                    'ejar_broker_id': response.get('broker_id'),
                    'ejar_status': 'pending',
                    'sync_status': 'synced',
                    'sync_error_message': False,
                    'last_sync_date': fields.Datetime.now()
                })
                
                self.message_post(
                    body=_('Broker successfully registered with Ejar platform. ID: %s') % response.get('broker_id'),
                    message_type='notification'
                )
                
                return {
                    'type': 'ir.actions.client',
                    'tag': 'display_notification',
                    'params': {
                        'title': _('Success'),
                        'message': _('Broker registered with Ejar platform successfully!'),
                        'type': 'success',
                    }
                }
            else:
                raise UserError(_('Failed to register broker with Ejar: %s') % response.get('error', 'Unknown error'))
                
        except Exception as e:
            self.write({
                'sync_status': 'error',
                'sync_error_message': str(e)
            })
            _logger.error(f"Failed to register broker {self.name} with Ejar: {e}")
            raise UserError(_('Failed to register broker with Ejar: %s') % str(e))
    
    def _prepare_ejar_broker_data(self):
        """Prepare broker data for Ejar API"""
        data = {
            'name': self.name,
            'entity_type': self.entity_type,
            'license_info': {
                'license_number': self.broker_license_number,
                'license_type': self.license_type,
                'issue_date': self.license_issue_date.isoformat() if self.license_issue_date else None,
                'expiry_date': self.license_expiry_date.isoformat() if self.license_expiry_date else None,
                'authority': self.license_authority,
            },
            'contact_info': {
                'phone': self.phone,
                'mobile': self.mobile,
                'email': self.email,
                'website': self.website,
                'address': self.address,
                'city': self.city,
                'district': self.district,
                'postal_code': self.postal_code,
            },
            'office_info': {
                'name': self.office_name,
                'address': self.office_address,
                'phone': self.office_phone,
                'email': self.office_email,
            },
            'financial': {
                'bank_name': self.bank_name,
                'bank_account_number': self.bank_account_number,
                'iban': self.iban,
            },
            'commission': {
                'default_rate': self.default_commission_rate,
                'type': self.commission_type,
                'min_amount': self.min_commission,
                'max_amount': self.max_commission,
            },
            'service_areas': [area.name for area in self.service_area_ids],
            'specializations': [spec.name for spec in self.specialization_ids],
            'documents': [
                {
                    'type': doc.document_type,
                    'name': doc.name,
                    'attachment_id': doc.attachment_id.id,
                }
                for doc in self.document_ids
            ]
        }
        
        if self.entity_type == 'individual':
            data['individual_info'] = {
                'national_id': self.national_id,
                'id_type': self.id_type,
                'passport_number': self.passport_number,
                'nationality': self.nationality.code if self.nationality else None,
                'birth_date': self.birth_date.isoformat() if self.birth_date else None,
                'gender': self.gender,
            }
        else:
            data['company_info'] = {
                'commercial_registration': self.commercial_registration,
                'tax_number': self.tax_number,
                'company_type': self.company_type,
                'legal_representative': {
                    'name': self.legal_representative_name,
                    'id': self.legal_representative_id,
                    'phone': self.legal_representative_phone,
                }
            }
        
        return data
    
    def action_verify_broker(self):
        """Verify broker information"""
        self.ensure_one()
        
        if self.state != 'draft':
            raise UserError(_('Only draft brokers can be verified'))
        
        # Perform verification checks
        verification_errors = []
        
        # Check required fields
        required_fields = ['name', 'broker_license_number', 'phone', 'email', 'address', 'city']
        if self.entity_type == 'individual':
            required_fields.extend(['national_id', 'nationality'])
        else:
            required_fields.extend(['commercial_registration', 'legal_representative_name'])
        
        for field in required_fields:
            if not getattr(self, field):
                verification_errors.append(_('Missing required field: %s') % self._fields[field].string)
        
        # Check license validity
        if self.license_expiry_date and self.license_expiry_date < fields.Date.today():
            verification_errors.append(_('Broker license has expired'))
        
        # Check documents
        required_docs = ['broker_license', 'national_id']
        if self.entity_type == 'company':
            required_docs.extend(['commercial_registration'])
        
        existing_docs = self.document_ids.mapped('document_type')
        missing_docs = [doc for doc in required_docs if doc not in existing_docs]
        
        if missing_docs:
            verification_errors.append(_('Missing required documents: %s') % ', '.join(missing_docs))
        
        if verification_errors:
            raise UserError('\n'.join(verification_errors))
        
        self.write({'state': 'verified'})
        
        self.message_post(
            body=_('Broker information verified successfully'),
            message_type='notification'
        )
    
    def action_approve_broker(self):
        """Approve broker"""
        self.ensure_one()
        
        if self.state != 'verified':
            raise UserError(_('Broker must be verified before approval'))
        
        self.write({'state': 'approved'})
        
        self.message_post(
            body=_('Broker approved successfully'),
            message_type='notification'
        )
    
    def action_suspend_broker(self):
        """Suspend broker"""
        self.ensure_one()
        
        self.write({'state': 'suspended'})
        
        self.message_post(
            body=_('Broker suspended'),
            message_type='notification'
        )
    
    def action_view_contracts(self):
        """View broker contracts"""
        self.ensure_one()
        return {
            'name': _('Broker Contracts'),
            'type': 'ir.actions.act_window',
            'res_model': 'ejar.contract',
            'view_mode': 'tree,form',
            'domain': [('broker_id', '=', self.id)],
            'context': {'default_broker_id': self.id}
        }
    
    def action_view_properties(self):
        """View managed properties"""
        self.ensure_one()
        return {
            'name': _('Managed Properties'),
            'type': 'ir.actions.act_window',
            'res_model': 'ejar.property',
            'view_mode': 'tree,form',
            'domain': [('broker_id', '=', self.id)],
            'context': {'default_broker_id': self.id}
        }
    
    def action_create_partner(self):
        """Create res.partner from broker"""
        self.ensure_one()
        
        if self.partner_id:
            raise UserError(_('Partner already exists for this broker'))
        
        partner_vals = {
            'name': self.name,
            'phone': self.phone,
            'mobile': self.mobile,
            'email': self.email,
            'website': self.website,
            'street': self.address,
            'city': self.city,
            'country_id': self.nationality.id if self.nationality else False,
            'is_company': self.entity_type != 'individual',
            'customer_rank': 1,
            'supplier_rank': 1,
            'category_id': [(4, self.env.ref('base.res_partner_category_0').id)],  # Vendor category
        }
        
        if self.entity_type == 'company':
            partner_vals.update({
                'vat': self.tax_number,
                'company_registry': self.commercial_registration,
            })
        
        partner = self.env['res.partner'].create(partner_vals)
        self.partner_id = partner.id
        
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'res.partner',
            'res_id': partner.id,
            'view_mode': 'form',
            'target': 'current',
        }


class EjarBrokerDocument(models.Model):
    """Broker documents"""
    _name = 'ejar.broker.document'
    _description = 'Broker Document'
    _order = 'document_type, name'

    broker_id = fields.Many2one('ejar.broker', string='Broker', required=True, ondelete='cascade')
    name = fields.Char(string='Document Name', required=True)
    document_type = fields.Selection([
        ('broker_license', 'Broker License'),
        ('national_id', 'National ID / Iqama'),
        ('passport', 'Passport'),
        ('commercial_registration', 'Commercial Registration'),
        ('tax_certificate', 'Tax Certificate'),
        ('authorization_letter', 'Authorization Letter'),
        ('power_of_attorney', 'Power of Attorney'),
        ('bank_certificate', 'Bank Certificate'),
        ('insurance_certificate', 'Insurance Certificate'),
        ('other', 'Other')
    ], string='Document Type', required=True)
    
    attachment_id = fields.Many2one('ir.attachment', string='Attachment', required=True)
    description = fields.Text(string='Description')
    issue_date = fields.Date(string='Issue Date')
    expiry_date = fields.Date(string='Expiry Date')
    is_verified = fields.Boolean(string='Verified')
    verified_by = fields.Many2one('res.users', string='Verified By')
    verified_date = fields.Datetime(string='Verified Date')
    
    @api.constrains('issue_date', 'expiry_date')
    def _check_dates(self):
        """Validate document dates"""
        for record in self:
            if record.issue_date and record.expiry_date:
                if record.issue_date >= record.expiry_date:
                    raise ValidationError(_('Expiry date must be after issue date'))
    
    def action_verify_document(self):
        """Verify document"""
        self.ensure_one()
        
        self.write({
            'is_verified': True,
            'verified_by': self.env.user.id,
            'verified_date': fields.Datetime.now()
        })
        
        self.broker_id.message_post(
            body=_('Document %s verified') % self.name,
            message_type='notification'
        )


class EjarServiceArea(models.Model):
    """Service areas for brokers"""
    _name = 'ejar.service.area'
    _description = 'Service Area'
    _order = 'name'

    name = fields.Char(string='Area Name', required=True)
    code = fields.Char(string='Area Code')
    city = fields.Char(string='City')
    region = fields.Char(string='Region')
    active = fields.Boolean(string='Active', default=True)