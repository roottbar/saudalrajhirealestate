# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError, UserError
import re
import logging

_logger = logging.getLogger(__name__)


class EjarLandlord(models.Model):
    """Ejar platform landlord management"""
    _name = 'ejar.landlord'
    _description = 'Ejar Landlord'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'name'
    _rec_name = 'name'

    # Basic Information
    name = fields.Char(string='Full Name / Company Name', required=True, tracking=True)
    ejar_landlord_id = fields.Char(string='Ejar Landlord ID', readonly=True, copy=False)
    
    # Entity Type
    entity_type = fields.Selection([
        ('individual', 'Individual'),
        ('company', 'Company'),
        ('government', 'Government Entity')
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
    email = fields.Char(string='Email', tracking=True)
    website = fields.Char(string='Website')
    
    # Address Information
    address = fields.Text(string='Address', required=True)
    city = fields.Char(string='City', required=True)
    district = fields.Char(string='District')
    postal_code = fields.Char(string='Postal Code')
    
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
    
    # Property Portfolio
    property_ids = fields.One2many('ejar.property', 'landlord_id', string='Properties')
    property_count = fields.Integer(string='Property Count', compute='_compute_property_count')
    total_portfolio_value = fields.Monetary(string='Total Portfolio Value', compute='_compute_portfolio_value')
    
    # Contracts
    contract_ids = fields.One2many('ejar.contract', 'landlord_id', string='Contracts')
    active_contract_ids = fields.One2many('ejar.contract', 'landlord_id', 
                                          domain=[('state', '=', 'active')], string='Active Contracts')
    contract_count = fields.Integer(string='Contract Count', compute='_compute_contract_count')
    
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
    
    # Broker Information
    uses_broker = fields.Boolean(string='Uses Broker Services')
    preferred_broker_id = fields.Many2one('ejar.broker', string='Preferred Broker')
    
    # Preferences
    auto_renewal = fields.Boolean(string='Auto Contract Renewal', default=True)
    payment_terms = fields.Selection([
        ('monthly', 'Monthly'),
        ('quarterly', 'Quarterly'),
        ('semi_annual', 'Semi-Annual'),
        ('annual', 'Annual')
    ], string='Preferred Payment Terms', default='annual')
    
    # Rating and Reviews
    rating = fields.Float(string='Rating', digits=(2, 1), readonly=True)
    review_count = fields.Integer(string='Review Count', readonly=True)
    
    # Related Records
    partner_id = fields.Many2one('res.partner', string='Related Partner')
    
    # Documents
    document_ids = fields.One2many('ejar.landlord.document', 'landlord_id', string='Documents')
    
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
    
    @api.depends('property_ids')
    def _compute_property_count(self):
        """Count properties"""
        for record in self:
            record.property_count = len(record.property_ids)
    
    @api.depends('property_ids.market_value')
    def _compute_portfolio_value(self):
        """Calculate total portfolio value"""
        for record in self:
            record.total_portfolio_value = sum(record.property_ids.mapped('market_value'))
    
    @api.depends('contract_ids')
    def _compute_contract_count(self):
        """Count contracts"""
        for record in self:
            record.contract_count = len(record.contract_ids)
    
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
                    raise ValidationError(_('A landlord with this ID already exists'))
    
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
                    raise ValidationError(_('A landlord with this Commercial Registration already exists'))
    
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
        """Register landlord with Ejar platform"""
        self.ensure_one()
        
        if self.ejar_status != 'not_registered':
            raise UserError(_('Landlord is already registered or pending registration'))
        
        # Validate required documents
        if self.entity_type == 'individual':
            required_docs = ['national_id', 'property_deed']
        else:
            required_docs = ['commercial_registration', 'property_deed', 'authorization_letter']
        
        existing_docs = self.document_ids.mapped('document_type')
        missing_docs = [doc for doc in required_docs if doc not in existing_docs]
        
        if missing_docs:
            raise UserError(_('Missing required documents: %s') % ', '.join(missing_docs))
        
        try:
            # Prepare landlord data for Ejar API
            landlord_data = self._prepare_ejar_landlord_data()
            
            # Submit to Ejar API
            api_connector = self.env['ejar.api.connector']
            response = api_connector.register_landlord(landlord_data)
            
            if response.get('success'):
                self.write({
                    'ejar_landlord_id': response.get('landlord_id'),
                    'ejar_status': 'pending',
                    'sync_status': 'synced',
                    'sync_error_message': False,
                    'last_sync_date': fields.Datetime.now()
                })
                
                self.message_post(
                    body=_('Landlord successfully registered with Ejar platform. ID: %s') % response.get('landlord_id'),
                    message_type='notification'
                )
                
                return {
                    'type': 'ir.actions.client',
                    'tag': 'display_notification',
                    'params': {
                        'title': _('Success'),
                        'message': _('Landlord registered with Ejar platform successfully!'),
                        'type': 'success',
                    }
                }
            else:
                raise UserError(_('Failed to register landlord with Ejar: %s') % response.get('error', 'Unknown error'))
                
        except Exception as e:
            self.write({
                'sync_status': 'error',
                'sync_error_message': str(e)
            })
            _logger.error(f"Failed to register landlord {self.name} with Ejar: {e}")
            raise UserError(_('Failed to register landlord with Ejar: %s') % str(e))
    
    def _prepare_ejar_landlord_data(self):
        """Prepare landlord data for Ejar API"""
        data = {
            'name': self.name,
            'entity_type': self.entity_type,
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
            'financial': {
                'bank_name': self.bank_name,
                'bank_account_number': self.bank_account_number,
                'iban': self.iban,
            },
            'preferences': {
                'auto_renewal': self.auto_renewal,
                'payment_terms': self.payment_terms,
                'uses_broker': self.uses_broker,
            },
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
    
    def action_verify_landlord(self):
        """Verify landlord information"""
        self.ensure_one()
        
        if self.state != 'draft':
            raise UserError(_('Only draft landlords can be verified'))
        
        # Perform verification checks
        verification_errors = []
        
        # Check required fields
        required_fields = ['name', 'phone', 'address', 'city']
        if self.entity_type == 'individual':
            required_fields.extend(['national_id', 'nationality'])
        else:
            required_fields.extend(['commercial_registration', 'legal_representative_name'])
        
        for field in required_fields:
            if not getattr(self, field):
                verification_errors.append(_('Missing required field: %s') % self._fields[field].string)
        
        # Check documents
        if self.entity_type == 'individual':
            required_docs = ['national_id']
        else:
            required_docs = ['commercial_registration']
        
        existing_docs = self.document_ids.mapped('document_type')
        missing_docs = [doc for doc in required_docs if doc not in existing_docs]
        
        if missing_docs:
            verification_errors.append(_('Missing required documents: %s') % ', '.join(missing_docs))
        
        if verification_errors:
            raise UserError('\n'.join(verification_errors))
        
        self.write({'state': 'verified'})
        
        self.message_post(
            body=_('Landlord information verified successfully'),
            message_type='notification'
        )
    
    def action_approve_landlord(self):
        """Approve landlord"""
        self.ensure_one()
        
        if self.state != 'verified':
            raise UserError(_('Landlord must be verified before approval'))
        
        self.write({'state': 'approved'})
        
        self.message_post(
            body=_('Landlord approved successfully'),
            message_type='notification'
        )
    
    def action_suspend_landlord(self):
        """Suspend landlord"""
        self.ensure_one()
        
        self.write({'state': 'suspended'})
        
        self.message_post(
            body=_('Landlord suspended'),
            message_type='notification'
        )
    
    def action_view_properties(self):
        """View landlord properties"""
        self.ensure_one()
        return {
            'name': _('Landlord Properties'),
            'type': 'ir.actions.act_window',
            'res_model': 'ejar.property',
            'view_mode': 'tree,form',
            'domain': [('landlord_id', '=', self.id)],
            'context': {'default_landlord_id': self.id}
        }
    
    def action_view_contracts(self):
        """View landlord contracts"""
        self.ensure_one()
        return {
            'name': _('Landlord Contracts'),
            'type': 'ir.actions.act_window',
            'res_model': 'ejar.contract',
            'view_mode': 'tree,form',
            'domain': [('landlord_id', '=', self.id)],
            'context': {'default_landlord_id': self.id}
        }
    
    def action_create_partner(self):
        """Create res.partner from landlord"""
        self.ensure_one()
        
        if self.partner_id:
            raise UserError(_('Partner already exists for this landlord'))
        
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
            'customer_rank': 0,
            'supplier_rank': 1,
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


class EjarLandlordDocument(models.Model):
    """Landlord documents"""
    _name = 'ejar.landlord.document'
    _description = 'Landlord Document'
    _order = 'document_type, name'

    landlord_id = fields.Many2one('ejar.landlord', string='Landlord', required=True, ondelete='cascade')
    name = fields.Char(string='Document Name', required=True)
    document_type = fields.Selection([
        ('national_id', 'National ID / Iqama'),
        ('passport', 'Passport'),
        ('commercial_registration', 'Commercial Registration'),
        ('tax_certificate', 'Tax Certificate'),
        ('property_deed', 'Property Deed'),
        ('authorization_letter', 'Authorization Letter'),
        ('power_of_attorney', 'Power of Attorney'),
        ('bank_certificate', 'Bank Certificate'),
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
        
        self.landlord_id.message_post(
            body=_('Document %s verified') % self.name,
            message_type='notification'
        )