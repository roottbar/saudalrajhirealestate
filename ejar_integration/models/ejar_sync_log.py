# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError, UserError
import json
import logging

_logger = logging.getLogger(__name__)


class EjarSyncLog(models.Model):
    """Ejar platform synchronization log"""
    _name = 'ejar.sync.log'
    _description = 'Ejar Sync Log'
    _order = 'create_date desc'
    _rec_name = 'operation_type'

    # Basic Information
    operation_type = fields.Selection([
        ('property_sync', 'Property Sync'),
        ('contract_sync', 'Contract Sync'),
        ('tenant_sync', 'Tenant Sync'),
        ('landlord_sync', 'Landlord Sync'),
        ('broker_sync', 'Broker Sync'),
        ('payment_sync', 'Payment Sync'),
        ('notification_sync', 'Notification Sync'),
        ('document_sync', 'Document Sync'),
        ('full_sync', 'Full Sync'),
        ('status_check', 'Status Check'),
        ('webhook_receive', 'Webhook Receive'),
        ('other', 'Other')
    ], string='Operation Type', required=True, index=True)
    
    sync_direction = fields.Selection([
        ('to_ejar', 'To Ejar'),
        ('from_ejar', 'From Ejar'),
        ('bidirectional', 'Bidirectional')
    ], string='Sync Direction', required=True, default='to_ejar')
    
    # Status
    status = fields.Selection([
        ('pending', 'Pending'),
        ('in_progress', 'In Progress'),
        ('success', 'Success'),
        ('partial_success', 'Partial Success'),
        ('failed', 'Failed'),
        ('cancelled', 'Cancelled')
    ], string='Status', default='pending', index=True)
    
    # Related Records
    model_name = fields.Char(string='Model Name', index=True)
    record_id = fields.Integer(string='Record ID', index=True)
    record_name = fields.Char(string='Record Name')
    
    # Ejar Information
    ejar_id = fields.Char(string='Ejar ID', index=True)
    ejar_endpoint = fields.Char(string='Ejar Endpoint')
    ejar_method = fields.Selection([
        ('GET', 'GET'),
        ('POST', 'POST'),
        ('PUT', 'PUT'),
        ('PATCH', 'PATCH'),
        ('DELETE', 'DELETE')
    ], string='HTTP Method')
    
    # Request/Response Data
    request_data = fields.Text(string='Request Data')
    response_data = fields.Text(string='Response Data')
    error_message = fields.Text(string='Error Message')
    error_code = fields.Char(string='Error Code')
    
    # Timing Information
    start_time = fields.Datetime(string='Start Time')
    end_time = fields.Datetime(string='End Time')
    duration = fields.Float(string='Duration (seconds)', compute='_compute_duration', store=True)
    
    # Retry Information
    retry_count = fields.Integer(string='Retry Count', default=0)
    max_retries = fields.Integer(string='Max Retries', default=3)
    next_retry_time = fields.Datetime(string='Next Retry Time')
    
    # Batch Information
    batch_id = fields.Char(string='Batch ID', index=True)
    batch_size = fields.Integer(string='Batch Size')
    processed_count = fields.Integer(string='Processed Count')
    success_count = fields.Integer(string='Success Count')
    failed_count = fields.Integer(string='Failed Count')
    
    # Additional Information
    user_id = fields.Many2one('res.users', string='User', default=lambda self: self.env.user)
    company_id = fields.Many2one('res.company', string='Company', 
                                 default=lambda self: self.env.company)
    
    # Webhook specific
    webhook_signature = fields.Char(string='Webhook Signature')
    webhook_event = fields.Char(string='Webhook Event')
    
    # Notes
    notes = fields.Text(string='Notes')
    
    @api.depends('start_time', 'end_time')
    def _compute_duration(self):
        """Calculate operation duration"""
        for record in self:
            if record.start_time and record.end_time:
                delta = record.end_time - record.start_time
                record.duration = delta.total_seconds()
            else:
                record.duration = 0
    
    def name_get(self):
        """Custom name display"""
        result = []
        for record in self:
            name = f"{record.operation_type} - {record.status}"
            if record.record_name:
                name += f" ({record.record_name})"
            result.append((record.id, name))
        return result
    
    @api.model
    def create_sync_log(self, operation_type, model_name=None, record_id=None, 
                       sync_direction='to_ejar', **kwargs):
        """Create a new sync log entry"""
        vals = {
            'operation_type': operation_type,
            'model_name': model_name,
            'record_id': record_id,
            'sync_direction': sync_direction,
            'start_time': fields.Datetime.now(),
            'status': 'in_progress',
        }
        
        # Add optional fields
        for field in ['ejar_endpoint', 'ejar_method', 'batch_id', 'batch_size', 
                     'webhook_event', 'webhook_signature', 'notes']:
            if field in kwargs:
                vals[field] = kwargs[field]
        
        # Get record name if possible
        if model_name and record_id:
            try:
                record = self.env[model_name].browse(record_id)
                if record.exists():
                    vals['record_name'] = record.display_name
                    if hasattr(record, 'ejar_property_id') and record.ejar_property_id:
                        vals['ejar_id'] = record.ejar_property_id
                    elif hasattr(record, 'ejar_contract_id') and record.ejar_contract_id:
                        vals['ejar_id'] = record.ejar_contract_id
                    elif hasattr(record, 'ejar_tenant_id') and record.ejar_tenant_id:
                        vals['ejar_id'] = record.ejar_tenant_id
                    elif hasattr(record, 'ejar_landlord_id') and record.ejar_landlord_id:
                        vals['ejar_id'] = record.ejar_landlord_id
                    elif hasattr(record, 'ejar_broker_id') and record.ejar_broker_id:
                        vals['ejar_id'] = record.ejar_broker_id
            except Exception as e:
                _logger.warning(f"Could not get record name for {model_name}:{record_id}: {e}")
        
        return self.create(vals)
    
    def log_success(self, response_data=None, **kwargs):
        """Log successful operation"""
        self.ensure_one()
        
        vals = {
            'status': 'success',
            'end_time': fields.Datetime.now(),
        }
        
        if response_data:
            vals['response_data'] = json.dumps(response_data) if isinstance(response_data, dict) else str(response_data)
        
        # Update counts for batch operations
        if 'success_count' in kwargs:
            vals['success_count'] = kwargs['success_count']
        if 'processed_count' in kwargs:
            vals['processed_count'] = kwargs['processed_count']
        
        self.write(vals)
        
        # Update related record sync status
        self._update_record_sync_status('synced')
    
    def log_failure(self, error_message, error_code=None, response_data=None, **kwargs):
        """Log failed operation"""
        self.ensure_one()
        
        vals = {
            'status': 'failed',
            'end_time': fields.Datetime.now(),
            'error_message': str(error_message),
        }
        
        if error_code:
            vals['error_code'] = str(error_code)
        
        if response_data:
            vals['response_data'] = json.dumps(response_data) if isinstance(response_data, dict) else str(response_data)
        
        # Update counts for batch operations
        if 'failed_count' in kwargs:
            vals['failed_count'] = kwargs['failed_count']
        if 'processed_count' in kwargs:
            vals['processed_count'] = kwargs['processed_count']
        
        self.write(vals)
        
        # Update related record sync status
        self._update_record_sync_status('error', str(error_message))
        
        # Schedule retry if applicable
        if self.retry_count < self.max_retries:
            self._schedule_retry()
    
    def log_partial_success(self, success_count, failed_count, response_data=None, error_message=None):
        """Log partially successful batch operation"""
        self.ensure_one()
        
        vals = {
            'status': 'partial_success',
            'end_time': fields.Datetime.now(),
            'success_count': success_count,
            'failed_count': failed_count,
            'processed_count': success_count + failed_count,
        }
        
        if response_data:
            vals['response_data'] = json.dumps(response_data) if isinstance(response_data, dict) else str(response_data)
        
        if error_message:
            vals['error_message'] = str(error_message)
        
        self.write(vals)
    
    def log_request_data(self, request_data):
        """Log request data"""
        self.ensure_one()
        
        if isinstance(request_data, dict):
            request_data = json.dumps(request_data, indent=2)
        
        self.write({'request_data': str(request_data)})
    
    def _update_record_sync_status(self, status, error_message=None):
        """Update sync status on related record"""
        if not self.model_name or not self.record_id:
            return
        
        try:
            record = self.env[self.model_name].browse(self.record_id)
            if record.exists() and hasattr(record, 'sync_status'):
                vals = {
                    'sync_status': status,
                    'last_sync_date': fields.Datetime.now(),
                }
                
                if error_message and hasattr(record, 'sync_error_message'):
                    vals['sync_error_message'] = error_message
                elif hasattr(record, 'sync_error_message'):
                    vals['sync_error_message'] = False
                
                record.write(vals)
        except Exception as e:
            _logger.warning(f"Could not update sync status for {self.model_name}:{self.record_id}: {e}")
    
    def _schedule_retry(self):
        """Schedule retry for failed operation"""
        if self.retry_count >= self.max_retries:
            return
        
        # Calculate next retry time with exponential backoff
        import datetime
        delay_minutes = 2 ** self.retry_count  # 2, 4, 8 minutes
        next_retry = fields.Datetime.now() + datetime.timedelta(minutes=delay_minutes)
        
        self.write({
            'next_retry_time': next_retry,
            'retry_count': self.retry_count + 1,
            'status': 'pending'
        })
    
    def action_retry(self):
        """Manually retry failed operation"""
        self.ensure_one()
        
        if self.status not in ['failed', 'cancelled']:
            raise UserError(_('Only failed or cancelled operations can be retried'))
        
        if self.retry_count >= self.max_retries:
            raise UserError(_('Maximum retry count reached'))
        
        # Reset status and schedule for retry
        self.write({
            'status': 'pending',
            'retry_count': self.retry_count + 1,
            'next_retry_time': fields.Datetime.now(),
            'error_message': False,
            'error_code': False,
        })
        
        # Trigger retry based on operation type
        self._execute_retry()
    
    def _execute_retry(self):
        """Execute retry based on operation type"""
        try:
            if self.operation_type == 'property_sync' and self.model_name == 'ejar.property':
                property_record = self.env['ejar.property'].browse(self.record_id)
                if property_record.exists():
                    property_record.action_register_with_ejar()
            
            elif self.operation_type == 'contract_sync' and self.model_name == 'ejar.contract':
                contract_record = self.env['ejar.contract'].browse(self.record_id)
                if contract_record.exists():
                    contract_record.action_submit_to_ejar()
            
            elif self.operation_type == 'tenant_sync' and self.model_name == 'ejar.tenant':
                tenant_record = self.env['ejar.tenant'].browse(self.record_id)
                if tenant_record.exists():
                    tenant_record.action_register_with_ejar()
            
            elif self.operation_type == 'landlord_sync' and self.model_name == 'ejar.landlord':
                landlord_record = self.env['ejar.landlord'].browse(self.record_id)
                if landlord_record.exists():
                    landlord_record.action_register_with_ejar()
            
            elif self.operation_type == 'broker_sync' and self.model_name == 'ejar.broker':
                broker_record = self.env['ejar.broker'].browse(self.record_id)
                if broker_record.exists():
                    broker_record.action_register_with_ejar()
            
            else:
                # Generic retry - call sync method if available
                if self.model_name and self.record_id:
                    record = self.env[self.model_name].browse(self.record_id)
                    if record.exists() and hasattr(record, 'sync_with_ejar'):
                        record.sync_with_ejar()
                        
        except Exception as e:
            self.log_failure(str(e))
            raise
    
    def action_cancel(self):
        """Cancel pending operation"""
        self.ensure_one()
        
        if self.status not in ['pending', 'in_progress']:
            raise UserError(_('Only pending or in-progress operations can be cancelled'))
        
        self.write({
            'status': 'cancelled',
            'end_time': fields.Datetime.now(),
            'notes': (self.notes or '') + '\n' + _('Operation cancelled by user')
        })
    
    def action_view_record(self):
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
    
    @api.model
    def cleanup_old_logs(self, days=30):
        """Clean up old sync logs"""
        cutoff_date = fields.Datetime.now() - datetime.timedelta(days=days)
        old_logs = self.search([('create_date', '<', cutoff_date)])
        
        count = len(old_logs)
        old_logs.unlink()
        
        _logger.info(f"Cleaned up {count} old sync logs older than {days} days")
        return count
    
    @api.model
    def get_sync_statistics(self, days=7):
        """Get sync statistics for the last N days"""
        from_date = fields.Datetime.now() - datetime.timedelta(days=days)
        
        domain = [('create_date', '>=', from_date)]
        
        total_operations = self.search_count(domain)
        successful_operations = self.search_count(domain + [('status', '=', 'success')])
        failed_operations = self.search_count(domain + [('status', '=', 'failed')])
        pending_operations = self.search_count(domain + [('status', '=', 'pending')])
        
        # Get statistics by operation type
        operation_stats = {}
        for op_type in ['property_sync', 'contract_sync', 'tenant_sync', 'landlord_sync', 'broker_sync']:
            op_domain = domain + [('operation_type', '=', op_type)]
            operation_stats[op_type] = {
                'total': self.search_count(op_domain),
                'success': self.search_count(op_domain + [('status', '=', 'success')]),
                'failed': self.search_count(op_domain + [('status', '=', 'failed')]),
            }
        
        # Calculate success rate
        success_rate = (successful_operations / total_operations * 100) if total_operations > 0 else 0
        
        return {
            'period_days': days,
            'total_operations': total_operations,
            'successful_operations': successful_operations,
            'failed_operations': failed_operations,
            'pending_operations': pending_operations,
            'success_rate': round(success_rate, 2),
            'operation_stats': operation_stats,
        }
    
    @api.model
    def _cron_retry_failed_operations(self):
        """Cron job to retry failed operations"""
        pending_retries = self.search([
            ('status', '=', 'pending'),
            ('next_retry_time', '<=', fields.Datetime.now()),
            ('retry_count', '<', 'max_retries')
        ])
        
        for log in pending_retries:
            try:
                log._execute_retry()
            except Exception as e:
                _logger.error(f"Failed to retry operation {log.id}: {e}")
    
    @api.model
    def _cron_cleanup_old_logs(self):
        """Cron job to cleanup old logs"""
        # Get cleanup period from config (default 30 days)
        cleanup_days = int(self.env['ir.config_parameter'].sudo().get_param(
            'ejar_integration.sync_log_cleanup_days', '30'))
        
        self.cleanup_old_logs(cleanup_days)


class EjarSyncBatch(models.Model):
    """Batch synchronization operations"""
    _name = 'ejar.sync.batch'
    _description = 'Ejar Sync Batch'
    _order = 'create_date desc'

    name = fields.Char(string='Batch Name', required=True)
    batch_id = fields.Char(string='Batch ID', required=True, default=lambda self: self._generate_batch_id())
    
    operation_type = fields.Selection([
        ('property_sync', 'Property Sync'),
        ('contract_sync', 'Contract Sync'),
        ('tenant_sync', 'Tenant Sync'),
        ('landlord_sync', 'Landlord Sync'),
        ('broker_sync', 'Broker Sync'),
        ('full_sync', 'Full Sync'),
        ('custom', 'Custom')
    ], string='Operation Type', required=True)
    
    status = fields.Selection([
        ('draft', 'Draft'),
        ('running', 'Running'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
        ('cancelled', 'Cancelled')
    ], string='Status', default='draft')
    
    # Statistics
    total_records = fields.Integer(string='Total Records')
    processed_records = fields.Integer(string='Processed Records')
    successful_records = fields.Integer(string='Successful Records')
    failed_records = fields.Integer(string='Failed Records')
    
    # Timing
    start_time = fields.Datetime(string='Start Time')
    end_time = fields.Datetime(string='End Time')
    duration = fields.Float(string='Duration (minutes)', compute='_compute_duration')
    
    # Related logs
    sync_log_ids = fields.One2many('ejar.sync.log', 'batch_id', string='Sync Logs')
    
    # Configuration
    auto_retry = fields.Boolean(string='Auto Retry Failed', default=True)
    max_retries = fields.Integer(string='Max Retries', default=3)
    
    # Company
    company_id = fields.Many2one('res.company', string='Company', 
                                 default=lambda self: self.env.company)
    user_id = fields.Many2one('res.users', string='User', default=lambda self: self.env.user)
    
    @api.depends('start_time', 'end_time')
    def _compute_duration(self):
        """Calculate batch duration"""
        for record in self:
            if record.start_time and record.end_time:
                delta = record.end_time - record.start_time
                record.duration = delta.total_seconds() / 60  # Convert to minutes
            else:
                record.duration = 0
    
    def _generate_batch_id(self):
        """Generate unique batch ID"""
        import uuid
        return str(uuid.uuid4())
    
    def action_start_batch(self):
        """Start batch operation"""
        self.ensure_one()
        
        if self.status != 'draft':
            raise UserError(_('Only draft batches can be started'))
        
        self.write({
            'status': 'running',
            'start_time': fields.Datetime.now(),
        })
        
        # Execute batch operation based on type
        try:
            if self.operation_type == 'property_sync':
                self._sync_properties()
            elif self.operation_type == 'contract_sync':
                self._sync_contracts()
            elif self.operation_type == 'tenant_sync':
                self._sync_tenants()
            elif self.operation_type == 'landlord_sync':
                self._sync_landlords()
            elif self.operation_type == 'broker_sync':
                self._sync_brokers()
            elif self.operation_type == 'full_sync':
                self._full_sync()
            
            self._finalize_batch()
            
        except Exception as e:
            self.write({
                'status': 'failed',
                'end_time': fields.Datetime.now(),
            })
            _logger.error(f"Batch {self.batch_id} failed: {e}")
            raise
    
    def _sync_properties(self):
        """Sync all properties"""
        properties = self.env['ejar.property'].search([('ejar_status', '!=', 'registered')])
        self.total_records = len(properties)
        
        for prop in properties:
            try:
                prop.action_register_with_ejar()
                self.successful_records += 1
            except Exception as e:
                self.failed_records += 1
                _logger.error(f"Failed to sync property {prop.id}: {e}")
            
            self.processed_records += 1
    
    def _sync_contracts(self):
        """Sync all contracts"""
        contracts = self.env['ejar.contract'].search([('ejar_status', '!=', 'submitted')])
        self.total_records = len(contracts)
        
        for contract in contracts:
            try:
                contract.action_submit_to_ejar()
                self.successful_records += 1
            except Exception as e:
                self.failed_records += 1
                _logger.error(f"Failed to sync contract {contract.id}: {e}")
            
            self.processed_records += 1
    
    def _sync_tenants(self):
        """Sync all tenants"""
        tenants = self.env['ejar.tenant'].search([('ejar_status', '!=', 'registered')])
        self.total_records = len(tenants)
        
        for tenant in tenants:
            try:
                tenant.action_register_with_ejar()
                self.successful_records += 1
            except Exception as e:
                self.failed_records += 1
                _logger.error(f"Failed to sync tenant {tenant.id}: {e}")
            
            self.processed_records += 1
    
    def _sync_landlords(self):
        """Sync all landlords"""
        landlords = self.env['ejar.landlord'].search([('ejar_status', '!=', 'registered')])
        self.total_records = len(landlords)
        
        for landlord in landlords:
            try:
                landlord.action_register_with_ejar()
                self.successful_records += 1
            except Exception as e:
                self.failed_records += 1
                _logger.error(f"Failed to sync landlord {landlord.id}: {e}")
            
            self.processed_records += 1
    
    def _sync_brokers(self):
        """Sync all brokers"""
        brokers = self.env['ejar.broker'].search([('ejar_status', '!=', 'registered')])
        self.total_records = len(brokers)
        
        for broker in brokers:
            try:
                broker.action_register_with_ejar()
                self.successful_records += 1
            except Exception as e:
                self.failed_records += 1
                _logger.error(f"Failed to sync broker {broker.id}: {e}")
            
            self.processed_records += 1
    
    def _full_sync(self):
        """Perform full synchronization"""
        self._sync_properties()
        self._sync_tenants()
        self._sync_landlords()
        self._sync_brokers()
        self._sync_contracts()
    
    def _finalize_batch(self):
        """Finalize batch operation"""
        self.write({
            'status': 'completed',
            'end_time': fields.Datetime.now(),
        })
    
    def action_cancel_batch(self):
        """Cancel running batch"""
        self.ensure_one()
        
        if self.status != 'running':
            raise UserError(_('Only running batches can be cancelled'))
        
        self.write({
            'status': 'cancelled',
            'end_time': fields.Datetime.now(),
        })
    
    def action_view_logs(self):
        """View batch sync logs"""
        self.ensure_one()
        
        return {
            'name': _('Batch Sync Logs'),
            'type': 'ir.actions.act_window',
            'res_model': 'ejar.sync.log',
            'view_mode': 'tree,form',
            'domain': [('batch_id', '=', self.batch_id)],
            'context': {'default_batch_id': self.batch_id}
        }