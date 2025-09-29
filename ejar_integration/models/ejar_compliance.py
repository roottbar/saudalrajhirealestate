# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError, UserError
from datetime import datetime, timedelta
import logging

_logger = logging.getLogger(__name__)


class EjarCompliance(models.Model):
    """Ejar platform compliance management"""
    _name = 'ejar.compliance'
    _description = 'Ejar Compliance'
    _order = 'create_date desc'
    _rec_name = 'compliance_type'

    # Basic Information
    compliance_type = fields.Selection([
        ('contract_compliance', 'Contract Compliance'),
        ('property_compliance', 'Property Compliance'),
        ('tenant_compliance', 'Tenant Compliance'),
        ('landlord_compliance', 'Landlord Compliance'),
        ('broker_compliance', 'Broker Compliance'),
        ('payment_compliance', 'Payment Compliance'),
        ('document_compliance', 'Document Compliance'),
        ('legal_compliance', 'Legal Compliance'),
        ('regulatory_compliance', 'Regulatory Compliance'),
        ('data_compliance', 'Data Compliance')
    ], string='Compliance Type', required=True, index=True)
    
    title = fields.Char(string='Title', required=True)
    description = fields.Text(string='Description')
    
    # Status
    status = fields.Selection([
        ('draft', 'Draft'),
        ('active', 'Active'),
        ('violated', 'Violated'),
        ('resolved', 'Resolved'),
        ('expired', 'Expired'),
        ('cancelled', 'Cancelled')
    ], string='Status', default='draft', index=True)
    
    severity = fields.Selection([
        ('low', 'Low'),
        ('medium', 'Medium'),
        ('high', 'High'),
        ('critical', 'Critical')
    ], string='Severity', default='medium', required=True)
    
    # Related Records
    model_name = fields.Char(string='Model Name', index=True)
    record_id = fields.Integer(string='Record ID', index=True)
    record_name = fields.Char(string='Record Name')
    
    # Ejar Information
    ejar_rule_id = fields.Char(string='Ejar Rule ID')
    ejar_regulation_code = fields.Char(string='Ejar Regulation Code')
    
    # Compliance Rule
    rule_name = fields.Char(string='Rule Name', required=True)
    rule_description = fields.Text(string='Rule Description')
    rule_category = fields.Selection([
        ('mandatory', 'Mandatory'),
        ('recommended', 'Recommended'),
        ('optional', 'Optional')
    ], string='Rule Category', default='mandatory')
    
    # Dates
    effective_date = fields.Date(string='Effective Date', default=fields.Date.today)
    expiry_date = fields.Date(string='Expiry Date')
    check_date = fields.Datetime(string='Last Check Date')
    next_check_date = fields.Datetime(string='Next Check Date')
    
    # Violation Information
    violation_date = fields.Datetime(string='Violation Date')
    violation_details = fields.Text(string='Violation Details')
    violation_evidence = fields.Text(string='Violation Evidence')
    
    # Resolution
    resolution_required = fields.Boolean(string='Resolution Required', default=True)
    resolution_deadline = fields.Datetime(string='Resolution Deadline')
    resolution_status = fields.Selection([
        ('pending', 'Pending'),
        ('in_progress', 'In Progress'),
        ('completed', 'Completed'),
        ('overdue', 'Overdue')
    ], string='Resolution Status', default='pending')
    resolution_notes = fields.Text(string='Resolution Notes')
    resolution_date = fields.Datetime(string='Resolution Date')
    
    # Responsible Parties
    responsible_user_id = fields.Many2one('res.users', string='Responsible User')
    responsible_department = fields.Char(string='Responsible Department')
    
    # Notifications
    notify_violation = fields.Boolean(string='Notify on Violation', default=True)
    notify_deadline = fields.Boolean(string='Notify Before Deadline', default=True)
    notification_days = fields.Integer(string='Notification Days Before Deadline', default=7)
    
    # Attachments
    attachment_ids = fields.Many2many('ir.attachment', string='Attachments')
    
    # Company
    company_id = fields.Many2one('res.company', string='Company', 
                                 default=lambda self: self.env.company)
    
    # Computed Fields
    is_overdue = fields.Boolean(string='Is Overdue', compute='_compute_is_overdue', store=True)
    days_to_deadline = fields.Integer(string='Days to Deadline', compute='_compute_days_to_deadline')
    
    @api.depends('resolution_deadline', 'resolution_status')
    def _compute_is_overdue(self):
        """Check if resolution is overdue"""
        now = fields.Datetime.now()
        for record in self:
            if (record.resolution_deadline and 
                record.resolution_status in ['pending', 'in_progress'] and 
                record.resolution_deadline < now):
                record.is_overdue = True
            else:
                record.is_overdue = False
    
    @api.depends('resolution_deadline')
    def _compute_days_to_deadline(self):
        """Calculate days to deadline"""
        now = fields.Datetime.now()
        for record in self:
            if record.resolution_deadline:
                delta = record.resolution_deadline - now
                record.days_to_deadline = delta.days
            else:
                record.days_to_deadline = 0
    
    @api.constrains('effective_date', 'expiry_date')
    def _check_dates(self):
        """Validate dates"""
        for record in self:
            if record.expiry_date and record.effective_date and record.expiry_date < record.effective_date:
                raise ValidationError(_('Expiry date cannot be before effective date'))
    
    @api.constrains('resolution_deadline')
    def _check_resolution_deadline(self):
        """Validate resolution deadline"""
        for record in self:
            if record.resolution_deadline and record.violation_date and record.resolution_deadline < record.violation_date:
                raise ValidationError(_('Resolution deadline cannot be before violation date'))
    
    def name_get(self):
        """Custom name display"""
        result = []
        for record in self:
            name = f"{record.compliance_type} - {record.title}"
            if record.status == 'violated':
                name += f" ({_('VIOLATED')})"
            elif record.is_overdue:
                name += f" ({_('OVERDUE')})"
            result.append((record.id, name))
        return result
    
    @api.model
    def create_compliance_check(self, compliance_type, model_name, record_id, rule_name, **kwargs):
        """Create a new compliance check"""
        vals = {
            'compliance_type': compliance_type,
            'model_name': model_name,
            'record_id': record_id,
            'rule_name': rule_name,
            'check_date': fields.Datetime.now(),
            'status': 'active',
        }
        
        # Add optional fields
        for field in ['title', 'description', 'rule_description', 'rule_category', 
                     'severity', 'ejar_rule_id', 'ejar_regulation_code', 
                     'responsible_user_id', 'resolution_deadline']:
            if field in kwargs:
                vals[field] = kwargs[field]
        
        # Get record name if possible
        if model_name and record_id:
            try:
                record = self.env[model_name].browse(record_id)
                if record.exists():
                    vals['record_name'] = record.display_name
            except Exception as e:
                _logger.warning(f"Could not get record name for {model_name}:{record_id}: {e}")
        
        # Set default title if not provided
        if 'title' not in vals:
            vals['title'] = f"{compliance_type.replace('_', ' ').title()} - {rule_name}"
        
        # Calculate next check date
        vals['next_check_date'] = self._calculate_next_check_date(compliance_type)
        
        return self.create(vals)
    
    def _calculate_next_check_date(self, compliance_type):
        """Calculate next check date based on compliance type"""
        now = fields.Datetime.now()
        
        # Define check intervals by compliance type
        intervals = {
            'contract_compliance': 30,  # Monthly
            'property_compliance': 90,  # Quarterly
            'tenant_compliance': 180,   # Semi-annually
            'landlord_compliance': 180, # Semi-annually
            'broker_compliance': 90,    # Quarterly
            'payment_compliance': 30,   # Monthly
            'document_compliance': 60,  # Bi-monthly
            'legal_compliance': 365,    # Annually
            'regulatory_compliance': 90, # Quarterly
            'data_compliance': 30,      # Monthly
        }
        
        days = intervals.get(compliance_type, 90)  # Default to quarterly
        return now + timedelta(days=days)
    
    def action_check_compliance(self):
        """Check compliance status"""
        self.ensure_one()
        
        try:
            # Update check date
            self.check_date = fields.Datetime.now()
            
            # Perform compliance check based on type
            is_compliant = self._perform_compliance_check()
            
            if is_compliant:
                if self.status == 'violated':
                    self.action_resolve_violation()
                else:
                    self.status = 'active'
            else:
                self.action_report_violation()
            
            # Schedule next check
            self.next_check_date = self._calculate_next_check_date(self.compliance_type)
            
        except Exception as e:
            _logger.error(f"Compliance check failed for {self.id}: {e}")
            raise UserError(_('Compliance check failed: %s') % str(e))
    
    def _perform_compliance_check(self):
        """Perform actual compliance check based on type and rule"""
        if not self.model_name or not self.record_id:
            return True
        
        try:
            record = self.env[self.model_name].browse(self.record_id)
            if not record.exists():
                return False
            
            # Delegate to specific compliance check methods
            method_name = f'_check_{self.compliance_type}'
            if hasattr(self, method_name):
                return getattr(self, method_name)(record)
            else:
                # Generic compliance check
                return self._generic_compliance_check(record)
                
        except Exception as e:
            _logger.error(f"Compliance check error: {e}")
            return False
    
    def _check_contract_compliance(self, contract):
        """Check contract compliance"""
        if self.rule_name == 'contract_registration':
            return contract.ejar_status == 'submitted'
        elif self.rule_name == 'contract_dates':
            return contract.start_date and contract.end_date and contract.start_date < contract.end_date
        elif self.rule_name == 'contract_amount':
            return contract.monthly_rent > 0
        elif self.rule_name == 'contract_parties':
            return contract.tenant_id and contract.landlord_id
        elif self.rule_name == 'contract_property':
            return contract.property_id and contract.property_id.ejar_status == 'registered'
        return True
    
    def _check_property_compliance(self, property_rec):
        """Check property compliance"""
        if self.rule_name == 'property_registration':
            return property_rec.ejar_status == 'registered'
        elif self.rule_name == 'property_documents':
            return len(property_rec.document_ids) > 0
        elif self.rule_name == 'property_title_deed':
            return bool(property_rec.title_deed_number)
        elif self.rule_name == 'property_location':
            return property_rec.city and property_rec.district
        elif self.rule_name == 'property_specifications':
            return property_rec.total_area > 0 and property_rec.bedrooms >= 0
        return True
    
    def _check_tenant_compliance(self, tenant):
        """Check tenant compliance"""
        if self.rule_name == 'tenant_registration':
            return tenant.ejar_status == 'registered'
        elif self.rule_name == 'tenant_identification':
            return tenant.national_id or tenant.passport_number
        elif self.rule_name == 'tenant_documents':
            return len(tenant.document_ids) > 0
        elif self.rule_name == 'tenant_contact':
            return tenant.phone or tenant.mobile
        elif self.rule_name == 'tenant_income_verification':
            return tenant.monthly_income > 0 and tenant.employment_type
        return True
    
    def _check_landlord_compliance(self, landlord):
        """Check landlord compliance"""
        if self.rule_name == 'landlord_registration':
            return landlord.ejar_status == 'registered'
        elif self.rule_name == 'landlord_identification':
            if landlord.entity_type == 'individual':
                return bool(landlord.national_id)
            else:
                return bool(landlord.commercial_registration)
        elif self.rule_name == 'landlord_documents':
            return len(landlord.document_ids) > 0
        elif self.rule_name == 'landlord_contact':
            return landlord.phone or landlord.mobile
        elif self.rule_name == 'landlord_bank_details':
            return landlord.bank_name and landlord.iban
        return True
    
    def _check_broker_compliance(self, broker):
        """Check broker compliance"""
        if self.rule_name == 'broker_registration':
            return broker.ejar_status == 'registered'
        elif self.rule_name == 'broker_license':
            return broker.broker_license and broker.license_expiry_date
        elif self.rule_name == 'broker_license_validity':
            return broker.license_expiry_date and broker.license_expiry_date > fields.Date.today()
        elif self.rule_name == 'broker_identification':
            if broker.entity_type == 'individual':
                return bool(broker.national_id)
            else:
                return bool(broker.commercial_registration)
        elif self.rule_name == 'broker_documents':
            return len(broker.document_ids) > 0
        return True
    
    def _generic_compliance_check(self, record):
        """Generic compliance check"""
        # Basic checks that apply to most records
        if hasattr(record, 'ejar_status'):
            return record.ejar_status in ['registered', 'submitted', 'approved']
        return True
    
    def action_report_violation(self, violation_details=None):
        """Report compliance violation"""
        self.ensure_one()
        
        vals = {
            'status': 'violated',
            'violation_date': fields.Datetime.now(),
            'resolution_status': 'pending',
        }
        
        if violation_details:
            vals['violation_details'] = violation_details
        
        # Set resolution deadline if not set
        if not self.resolution_deadline:
            days_to_resolve = self._get_resolution_days()
            vals['resolution_deadline'] = fields.Datetime.now() + timedelta(days=days_to_resolve)
        
        self.write(vals)
        
        # Send notification if enabled
        if self.notify_violation:
            self._send_violation_notification()
        
        # Log the violation
        self._log_compliance_event('violation_reported', violation_details)
    
    def action_resolve_violation(self, resolution_notes=None):
        """Resolve compliance violation"""
        self.ensure_one()
        
        if self.status != 'violated':
            raise UserError(_('Only violated compliance records can be resolved'))
        
        vals = {
            'status': 'resolved',
            'resolution_status': 'completed',
            'resolution_date': fields.Datetime.now(),
        }
        
        if resolution_notes:
            vals['resolution_notes'] = resolution_notes
        
        self.write(vals)
        
        # Log the resolution
        self._log_compliance_event('violation_resolved', resolution_notes)
    
    def _get_resolution_days(self):
        """Get resolution days based on severity"""
        days_map = {
            'critical': 1,
            'high': 3,
            'medium': 7,
            'low': 14,
        }
        return days_map.get(self.severity, 7)
    
    def _send_violation_notification(self):
        """Send violation notification"""
        try:
            # Create notification record
            notification_vals = {
                'title': f'Compliance Violation: {self.title}',
                'message': f'A compliance violation has been detected for {self.record_name or "record"}.\n\n'
                          f'Rule: {self.rule_name}\n'
                          f'Severity: {self.severity}\n'
                          f'Resolution Deadline: {self.resolution_deadline}\n\n'
                          f'Please take immediate action to resolve this violation.',
                'notification_type': 'compliance_violation',
                'priority': 'high' if self.severity in ['high', 'critical'] else 'medium',
                'status': 'pending',
                'delivery_email': True,
                'delivery_system': True,
            }
            
            # Add recipients
            if self.responsible_user_id:
                notification_vals['user_ids'] = [(4, self.responsible_user_id.id)]
            
            # Add related record reference
            if self.model_name and self.record_id:
                notification_vals.update({
                    'related_model': self.model_name,
                    'related_record_id': self.record_id,
                })
            
            notification = self.env['ejar.notification'].create(notification_vals)
            notification.action_send()
            
        except Exception as e:
            _logger.error(f"Failed to send violation notification: {e}")
    
    def _log_compliance_event(self, event_type, details=None):
        """Log compliance event"""
        try:
            log_vals = {
                'operation_type': 'compliance_check',
                'model_name': 'ejar.compliance',
                'record_id': self.id,
                'record_name': self.display_name,
                'status': 'success',
                'notes': f'Compliance event: {event_type}',
            }
            
            if details:
                log_vals['notes'] += f'\nDetails: {details}'
            
            self.env['ejar.sync.log'].create_sync_log(**log_vals)
            
        except Exception as e:
            _logger.error(f"Failed to log compliance event: {e}")
    
    @api.model
    def _cron_check_compliance(self):
        """Cron job to check compliance"""
        # Find compliance records that need checking
        records_to_check = self.search([
            ('status', 'in', ['active', 'violated']),
            ('next_check_date', '<=', fields.Datetime.now())
        ])
        
        for record in records_to_check:
            try:
                record.action_check_compliance()
            except Exception as e:
                _logger.error(f"Failed to check compliance for {record.id}: {e}")
    
    @api.model
    def _cron_check_deadlines(self):
        """Cron job to check resolution deadlines"""
        # Find overdue resolutions
        overdue_records = self.search([
            ('status', '=', 'violated'),
            ('resolution_status', 'in', ['pending', 'in_progress']),
            ('resolution_deadline', '<', fields.Datetime.now())
        ])
        
        for record in overdue_records:
            record.resolution_status = 'overdue'
            
            # Send overdue notification
            if record.notify_deadline:
                record._send_overdue_notification()
        
        # Find records approaching deadline
        approaching_deadline = self.search([
            ('status', '=', 'violated'),
            ('resolution_status', 'in', ['pending', 'in_progress']),
            ('resolution_deadline', '>', fields.Datetime.now()),
            ('resolution_deadline', '<=', fields.Datetime.now() + timedelta(days=7))
        ])
        
        for record in approaching_deadline:
            if record.notify_deadline and record.days_to_deadline <= record.notification_days:
                record._send_deadline_notification()
    
    def _send_overdue_notification(self):
        """Send overdue notification"""
        try:
            notification_vals = {
                'title': f'Compliance Resolution Overdue: {self.title}',
                'message': f'The resolution deadline for compliance violation has passed.\n\n'
                          f'Rule: {self.rule_name}\n'
                          f'Deadline: {self.resolution_deadline}\n'
                          f'Days Overdue: {abs(self.days_to_deadline)}\n\n'
                          f'Immediate action is required.',
                'notification_type': 'compliance_overdue',
                'priority': 'high',
                'status': 'pending',
                'delivery_email': True,
                'delivery_system': True,
            }
            
            if self.responsible_user_id:
                notification_vals['user_ids'] = [(4, self.responsible_user_id.id)]
            
            notification = self.env['ejar.notification'].create(notification_vals)
            notification.action_send()
            
        except Exception as e:
            _logger.error(f"Failed to send overdue notification: {e}")
    
    def _send_deadline_notification(self):
        """Send deadline approaching notification"""
        try:
            notification_vals = {
                'title': f'Compliance Resolution Deadline Approaching: {self.title}',
                'message': f'The resolution deadline for compliance violation is approaching.\n\n'
                          f'Rule: {self.rule_name}\n'
                          f'Deadline: {self.resolution_deadline}\n'
                          f'Days Remaining: {self.days_to_deadline}\n\n'
                          f'Please take action to resolve this violation.',
                'notification_type': 'compliance_deadline',
                'priority': 'medium',
                'status': 'pending',
                'delivery_email': True,
                'delivery_system': True,
            }
            
            if self.responsible_user_id:
                notification_vals['user_ids'] = [(4, self.responsible_user_id.id)]
            
            notification = self.env['ejar.notification'].create(notification_vals)
            notification.action_send()
            
        except Exception as e:
            _logger.error(f"Failed to send deadline notification: {e}")
    
    def action_view_related_record(self):
        """View related record"""
        self.ensure_one()
        
        if not self.model_name or not self.record_id:
            raise UserError(_('No related record found'))
        
        try:
            record = self.env[self.model_name].browse(self.record_id)
            if not record.exists():
                raise UserError(_('Related record no longer exists'))
            
            return {
                'type': 'ir.actions.act_window',
                'res_model': self.model_name,
                'res_id': self.record_id,
                'view_mode': 'form',
                'target': 'current',
            }
        except Exception as e:
            raise UserError(_('Could not open related record: %s') % str(e))


class EjarComplianceRule(models.Model):
    """Ejar compliance rules configuration"""
    _name = 'ejar.compliance.rule'
    _description = 'Ejar Compliance Rule'
    _order = 'sequence, name'

    name = fields.Char(string='Rule Name', required=True)
    code = fields.Char(string='Rule Code', required=True)
    description = fields.Text(string='Description')
    
    # Configuration
    compliance_type = fields.Selection([
        ('contract_compliance', 'Contract Compliance'),
        ('property_compliance', 'Property Compliance'),
        ('tenant_compliance', 'Tenant Compliance'),
        ('landlord_compliance', 'Landlord Compliance'),
        ('broker_compliance', 'Broker Compliance'),
        ('payment_compliance', 'Payment Compliance'),
        ('document_compliance', 'Document Compliance'),
        ('legal_compliance', 'Legal Compliance'),
        ('regulatory_compliance', 'Regulatory Compliance'),
        ('data_compliance', 'Data Compliance')
    ], string='Compliance Type', required=True)
    
    model_name = fields.Char(string='Model Name', required=True)
    
    category = fields.Selection([
        ('mandatory', 'Mandatory'),
        ('recommended', 'Recommended'),
        ('optional', 'Optional')
    ], string='Category', default='mandatory', required=True)
    
    severity = fields.Selection([
        ('low', 'Low'),
        ('medium', 'Medium'),
        ('high', 'High'),
        ('critical', 'Critical')
    ], string='Default Severity', default='medium', required=True)
    
    # Ejar Integration
    ejar_rule_id = fields.Char(string='Ejar Rule ID')
    ejar_regulation_code = fields.Char(string='Ejar Regulation Code')
    
    # Automation
    auto_check = fields.Boolean(string='Auto Check', default=True)
    check_interval_days = fields.Integer(string='Check Interval (Days)', default=30)
    
    # Resolution
    resolution_days = fields.Integer(string='Resolution Days', default=7)
    auto_notify = fields.Boolean(string='Auto Notify', default=True)
    
    # Status
    active = fields.Boolean(string='Active', default=True)
    sequence = fields.Integer(string='Sequence', default=10)
    
    # Company
    company_id = fields.Many2one('res.company', string='Company', 
                                 default=lambda self: self.env.company)
    
    @api.constrains('code')
    def _check_code_unique(self):
        """Ensure rule code is unique per company"""
        for record in self:
            existing = self.search([
                ('code', '=', record.code),
                ('company_id', '=', record.company_id.id),
                ('id', '!=', record.id)
            ])
            if existing:
                raise ValidationError(_('Rule code must be unique per company'))
    
    def action_create_compliance_checks(self):
        """Create compliance checks for all applicable records"""
        self.ensure_one()
        
        if not self.active:
            raise UserError(_('Cannot create checks for inactive rules'))
        
        try:
            # Get all records of the specified model
            records = self.env[self.model_name].search([])
            
            created_count = 0
            for record in records:
                # Check if compliance check already exists
                existing = self.env['ejar.compliance'].search([
                    ('compliance_type', '=', self.compliance_type),
                    ('model_name', '=', self.model_name),
                    ('record_id', '=', record.id),
                    ('rule_name', '=', self.code),
                    ('status', 'in', ['active', 'violated'])
                ])
                
                if not existing:
                    # Create new compliance check
                    self.env['ejar.compliance'].create_compliance_check(
                        compliance_type=self.compliance_type,
                        model_name=self.model_name,
                        record_id=record.id,
                        rule_name=self.code,
                        title=f"{self.name} - {record.display_name}",
                        description=self.description,
                        rule_description=self.description,
                        rule_category=self.category,
                        severity=self.severity,
                        ejar_rule_id=self.ejar_rule_id,
                        ejar_regulation_code=self.ejar_regulation_code,
                    )
                    created_count += 1
            
            return {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'title': _('Compliance Checks Created'),
                    'message': _('%d compliance checks created successfully') % created_count,
                    'type': 'success',
                }
            }
            
        except Exception as e:
            raise UserError(_('Failed to create compliance checks: %s') % str(e))