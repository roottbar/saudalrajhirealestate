# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError, UserError
import re
import logging

_logger = logging.getLogger(__name__)


class EjarTenant(models.Model):
    """Ejar platform tenant management"""
    _name = 'ejar.tenant'
    _description = 'Ejar Tenant'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'name'
    _rec_name = 'name'

    # Basic Information
    name = fields.Char(string='Full Name', required=True, tracking=True)
    ejar_tenant_id = fields.Char(string='Ejar Tenant ID', readonly=True, copy=False)
    
    # Identification
    national_id = fields.Char(string='National ID / Iqama', required=True, tracking=True)
    id_type = fields.Selection([
        ('national_id', 'National ID'),
        ('iqama', 'Iqama'),
        ('passport', 'Passport'),
        ('gcc_id', 'GCC ID')
    ], string='ID Type', required=True, default='national_id')
    
    passport_number = fields.Char(string='Passport Number')
    nationality = fields.Many2one('res.country', string='Nationality', required=True)
    
    # Personal Information
    birth_date = fields.Date(string='Birth Date', tracking=True)
    age = fields.Integer(string='Age', compute='_compute_age', store=True)
    gender = fields.Selection([
        ('male', 'Male'),
        ('female', 'Female')
    ], string='Gender', required=True)
    
    marital_status = fields.Selection([
        ('single', 'Single'),
        ('married', 'Married'),
        ('divorced', 'Divorced'),
        ('widowed', 'Widowed')
    ], string='Marital Status', default='single')
    
    # Contact Information
    phone = fields.Char(string='Phone', required=True, tracking=True)
    mobile = fields.Char(string='Mobile')
    email = fields.Char(string='Email', tracking=True)
    
    # Address Information
    address = fields.Text(string='Current Address', required=True)
    city = fields.Char(string='City', required=True)
    district = fields.Char(string='District')
    postal_code = fields.Char(string='Postal Code')
    
    # Emergency Contact
    emergency_contact_name = fields.Char(string='Emergency Contact Name')
    emergency_contact_phone = fields.Char(string='Emergency Contact Phone')
    emergency_contact_relation = fields.Char(string='Relation')
    
    # Employment Information
    employer_name = fields.Char(string='Employer Name')
    job_title = fields.Char(string='Job Title')
    monthly_income = fields.Monetary(string='Monthly Income', tracking=True)
    employment_type = fields.Selection([
        ('employee', 'Employee'),
        ('self_employed', 'Self Employed'),
        ('business_owner', 'Business Owner'),
        ('retired', 'Retired'),
        ('student', 'Student'),
        ('unemployed', 'Unemployed')
    ], string='Employment Type', default='employee')
    
    work_address = fields.Text(string='Work Address')
    work_phone = fields.Char(string='Work Phone')
    
    # Financial Information
    currency_id = fields.Many2one('res.currency', string='Currency', 
                                  default=lambda self: self.env.company.currency_id)
    bank_name = fields.Char(string='Bank Name')
    bank_account_number = fields.Char(string='Bank Account Number')
    iban = fields.Char(string='IBAN')
    
    # Credit Information
    credit_score = fields.Integer(string='Credit Score')
    has_previous_rental_issues = fields.Boolean(string='Previous Rental Issues')
    rental_issues_description = fields.Text(string='Rental Issues Description')
    
    # Family Information
    family_size = fields.Integer(string='Family Size', default=1)
    children_count = fields.Integer(string='Number of Children', default=0)
    dependents_count = fields.Integer(string='Number of Dependents', default=0)
    
    # Preferences
    preferred_property_type = fields.Many2one('ejar.property.type', string='Preferred Property Type')
    max_budget = fields.Monetary(string='Maximum Budget')
    preferred_location = fields.Char(string='Preferred Location')
    
    # Status
    state = fields.Selection([
        ('draft', 'Draft'),
        ('verified', 'Verified'),
        ('approved', 'Approved'),
        ('blacklisted', 'Blacklisted')
    ], string='Status', default='draft', tracking=True)
    
    # Ejar Integration
    ejar_status = fields.Selection([
        ('not_registered', 'Not Registered'),
        ('pending', 'Pending Registration'),
        ('registered', 'Registered'),
        ('rejected', 'Rejected')
    ], string='Ejar Status', default='not_registered', tracking=True)
    
    # Related Records
    partner_id = fields.Many2one('res.partner', string='Related Partner')
    contract_ids = fields.One2many('ejar.contract', 'tenant_id', string='Contracts')
    active_contract_id = fields.Many2one('ejar.contract', string='Active Contract', 
                                         compute='_compute_active_contract')
    contract_count = fields.Integer(string='Contract Count', compute='_compute_contract_count')
    
    # Documents
    document_ids = fields.One2many('ejar.tenant.document', 'tenant_id', string='Documents')
    
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
            if record.birth_date:
                record.age = today.year - record.birth_date.year - \
                           ((today.month, today.day) < (record.birth_date.month, record.birth_date.day))
            else:
                record.age = 0
    
    @api.depends('contract_ids')
    def _compute_active_contract(self):
        """Get active contract"""
        for record in self:
            active_contract = record.contract_ids.filtered(lambda c: c.state == 'active')
            record.active_contract_id = active_contract[0] if active_contract else False
    
    @api.depends('contract_ids')
    def _compute_contract_count(self):
        """Count contracts"""
        for record in self:
            record.contract_count = len(record.contract_ids)
    
    @api.constrains('national_id')
    def _check_national_id(self):
        """Validate national ID format"""
        for record in self:
            if record.national_id:
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
                    raise ValidationError(_('A tenant with this ID already exists'))
    
    @api.constrains('phone', 'mobile')
    def _check_phone_numbers(self):
        """Validate phone number formats"""
        for record in self:
            if record.phone:
                # Saudi phone number validation
                clean_phone = re.sub(r'[^\d+]', '', record.phone)
                if not re.match(r'^(\+966|966|0)?[5][0-9]{8}$', clean_phone):
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
    
    @api.constrains('monthly_income', 'max_budget')
    def _check_financial_amounts(self):
        """Validate financial amounts"""
        for record in self:
            if record.monthly_income < 0:
                raise ValidationError(_('Monthly income cannot be negative'))
            
            if record.max_budget < 0:
                raise ValidationError(_('Maximum budget cannot be negative'))
    
    @api.constrains('family_size', 'children_count', 'dependents_count')
    def _check_family_counts(self):
        """Validate family counts"""
        for record in self:
            if record.family_size < 1:
                raise ValidationError(_('Family size must be at least 1'))
            
            if record.children_count < 0:
                raise ValidationError(_('Children count cannot be negative'))
            
            if record.dependents_count < 0:
                raise ValidationError(_('Dependents count cannot be negative'))
    
    def action_register_with_ejar(self):
        """Register tenant with Ejar platform"""
        self.ensure_one()
        
        if self.ejar_status != 'not_registered':
            raise UserError(_('Tenant is already registered or pending registration'))
        
        # Validate required documents
        required_docs = ['national_id', 'salary_certificate', 'bank_statement']
        existing_docs = self.document_ids.mapped('document_type')
        missing_docs = [doc for doc in required_docs if doc not in existing_docs]
        
        if missing_docs:
            raise UserError(_('Missing required documents: %s') % ', '.join(missing_docs))
        
        try:
            # Prepare tenant data for Ejar API
            tenant_data = self._prepare_ejar_tenant_data()
            
            # Submit to Ejar API
            api_connector = self.env['ejar.api.connector']
            response = api_connector.register_tenant(tenant_data)
            
            if response.get('success'):
                self.write({
                    'ejar_tenant_id': response.get('tenant_id'),
                    'ejar_status': 'pending',
                    'sync_status': 'synced',
                    'sync_error_message': False,
                    'last_sync_date': fields.Datetime.now()
                })
                
                self.message_post(
                    body=_('Tenant successfully registered with Ejar platform. ID: %s') % response.get('tenant_id'),
                    message_type='notification'
                )
                
                return {
                    'type': 'ir.actions.client',
                    'tag': 'display_notification',
                    'params': {
                        'title': _('Success'),
                        'message': _('Tenant registered with Ejar platform successfully!'),
                        'type': 'success',
                    }
                }
            else:
                raise UserError(_('Failed to register tenant with Ejar: %s') % response.get('error', 'Unknown error'))
                
        except Exception as e:
            self.write({
                'sync_status': 'error',
                'sync_error_message': str(e)
            })
            _logger.error(f"Failed to register tenant {self.name} with Ejar: {e}")
            raise UserError(_('Failed to register tenant with Ejar: %s') % str(e))
    
    def _prepare_ejar_tenant_data(self):
        """Prepare tenant data for Ejar API"""
        return {
            'name': self.name,
            'identification': {
                'national_id': self.national_id,
                'id_type': self.id_type,
                'passport_number': self.passport_number,
                'nationality': self.nationality.code,
            },
            'personal_info': {
                'birth_date': self.birth_date.isoformat() if self.birth_date else None,
                'gender': self.gender,
                'marital_status': self.marital_status,
            },
            'contact_info': {
                'phone': self.phone,
                'mobile': self.mobile,
                'email': self.email,
                'address': self.address,
                'city': self.city,
                'district': self.district,
                'postal_code': self.postal_code,
            },
            'emergency_contact': {
                'name': self.emergency_contact_name,
                'phone': self.emergency_contact_phone,
                'relation': self.emergency_contact_relation,
            },
            'employment': {
                'employer_name': self.employer_name,
                'job_title': self.job_title,
                'monthly_income': self.monthly_income,
                'employment_type': self.employment_type,
                'work_address': self.work_address,
                'work_phone': self.work_phone,
            },
            'financial': {
                'bank_name': self.bank_name,
                'bank_account_number': self.bank_account_number,
                'iban': self.iban,
                'credit_score': self.credit_score,
            },
            'family': {
                'family_size': self.family_size,
                'children_count': self.children_count,
                'dependents_count': self.dependents_count,
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
    
    def action_verify_tenant(self):
        """Verify tenant information"""
        self.ensure_one()
        
        if self.state != 'draft':
            raise UserError(_('Only draft tenants can be verified'))
        
        # Perform verification checks
        verification_errors = []
        
        # Check required fields
        required_fields = ['name', 'national_id', 'phone', 'address', 'city']
        for field in required_fields:
            if not getattr(self, field):
                verification_errors.append(_('Missing required field: %s') % self._fields[field].string)
        
        # Check documents
        required_docs = ['national_id', 'salary_certificate']
        existing_docs = self.document_ids.mapped('document_type')
        missing_docs = [doc for doc in required_docs if doc not in existing_docs]
        
        if missing_docs:
            verification_errors.append(_('Missing required documents: %s') % ', '.join(missing_docs))
        
        if verification_errors:
            raise UserError('\n'.join(verification_errors))
        
        self.write({'state': 'verified'})
        
        self.message_post(
            body=_('Tenant information verified successfully'),
            message_type='notification'
        )
    
    def action_approve_tenant(self):
        """Approve tenant"""
        self.ensure_one()
        
        if self.state != 'verified':
            raise UserError(_('Tenant must be verified before approval'))
        
        self.write({'state': 'approved'})
        
        self.message_post(
            body=_('Tenant approved successfully'),
            message_type='notification'
        )
    
    def action_blacklist_tenant(self):
        """Blacklist tenant"""
        self.ensure_one()
        
        self.write({'state': 'blacklisted'})
        
        self.message_post(
            body=_('Tenant blacklisted'),
            message_type='notification'
        )
    
    def action_view_contracts(self):
        """View tenant contracts"""
        self.ensure_one()
        return {
            'name': _('Tenant Contracts'),
            'type': 'ir.actions.act_window',
            'res_model': 'ejar.contract',
            'view_mode': 'tree,form',
            'domain': [('tenant_id', '=', self.id)],
            'context': {'default_tenant_id': self.id}
        }
    
    def action_create_partner(self):
        """Create res.partner from tenant"""
        self.ensure_one()
        
        if self.partner_id:
            raise UserError(_('Partner already exists for this tenant'))
        
        partner_vals = {
            'name': self.name,
            'phone': self.phone,
            'mobile': self.mobile,
            'email': self.email,
            'street': self.address,
            'city': self.city,
            'country_id': self.nationality.id,
            'is_company': False,
            'customer_rank': 1,
            'supplier_rank': 0,
        }
        
        partner = self.env['res.partner'].create(partner_vals)
        self.partner_id = partner.id
        
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'res.partner',
            'res_id': partner.id,
            'view_mode': 'form',
            'target': 'current',
        }


class EjarTenantDocument(models.Model):
    """Tenant documents"""
    _name = 'ejar.tenant.document'
    _description = 'Tenant Document'
    _order = 'document_type, name'

    tenant_id = fields.Many2one('ejar.tenant', string='Tenant', required=True, ondelete='cascade')
    name = fields.Char(string='Document Name', required=True)
    document_type = fields.Selection([
        ('national_id', 'National ID / Iqama'),
        ('passport', 'Passport'),
        ('salary_certificate', 'Salary Certificate'),
        ('bank_statement', 'Bank Statement'),
        ('employment_letter', 'Employment Letter'),
        ('family_card', 'Family Card'),
        ('previous_rental', 'Previous Rental Agreement'),
        ('reference_letter', 'Reference Letter'),
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
        
        self.tenant_id.message_post(
            body=_('Document %s verified') % self.name,
            message_type='notification'
        )