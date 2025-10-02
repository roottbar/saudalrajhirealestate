# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError, UserError
import logging

_logger = logging.getLogger(__name__)


class EjarNotification(models.Model):
    """Ejar platform notification management"""
    _name = 'ejar.notification'
    _description = 'Ejar Notification'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'create_date desc'
    _rec_name = 'title'

    # Basic Information
    title = fields.Char(string='Title', required=True, tracking=True)
    message = fields.Text(string='Message', required=True)
    notification_type = fields.Selection([
        ('contract_created', 'Contract Created'),
        ('contract_approved', 'Contract Approved'),
        ('contract_rejected', 'Contract Rejected'),
        ('contract_expired', 'Contract Expired'),
        ('contract_terminated', 'Contract Terminated'),
        ('payment_due', 'Payment Due'),
        ('payment_overdue', 'Payment Overdue'),
        ('payment_received', 'Payment Received'),
        ('property_registered', 'Property Registered'),
        ('tenant_registered', 'Tenant Registered'),
        ('landlord_registered', 'Landlord Registered'),
        ('broker_registered', 'Broker Registered'),
        ('compliance_alert', 'Compliance Alert'),
        ('system_update', 'System Update'),
        ('maintenance_required', 'Maintenance Required'),
        ('document_expiry', 'Document Expiry'),
        ('other', 'Other')
    ], string='Type', required=True, default='other', tracking=True)
    
    # Priority and Status
    priority = fields.Selection([
        ('low', 'Low'),
        ('medium', 'Medium'),
        ('high', 'High'),
        ('urgent', 'Urgent')
    ], string='Priority', default='medium', tracking=True)
    
    status = fields.Selection([
        ('draft', 'Draft'),
        ('sent', 'Sent'),
        ('delivered', 'Delivered'),
        ('read', 'Read'),
        ('failed', 'Failed')
    ], string='Status', default='draft', tracking=True)
    
    # Recipients
    recipient_type = fields.Selection([
        ('tenant', 'Tenant'),
        ('landlord', 'Landlord'),
        ('broker', 'Broker'),
        ('all', 'All Users'),
        ('custom', 'Custom Recipients')
    ], string='Recipient Type', required=True, default='custom')
    
    tenant_ids = fields.Many2many('ejar.tenant', string='Tenant Recipients')
    landlord_ids = fields.Many2many('ejar.landlord', string='Landlord Recipients')
    broker_ids = fields.Many2many('ejar.broker', string='Broker Recipients')
    user_ids = fields.Many2many('res.users', string='User Recipients')
    
    # Related Records
    contract_id = fields.Many2one('ejar.contract', string='Related Contract')
    property_id = fields.Many2one('ejar.property', string='Related Property')
    tenant_id = fields.Many2one('ejar.tenant', string='Related Tenant')
    landlord_id = fields.Many2one('ejar.landlord', string='Related Landlord')
    broker_id = fields.Many2one('ejar.broker', string='Related Broker')
    
    # Delivery Information
    delivery_method = fields.Selection([
        ('email', 'Email'),
        ('sms', 'SMS'),
        ('push', 'Push Notification'),
        ('system', 'System Notification'),
        ('all', 'All Methods')
    ], string='Delivery Method', default='system', required=True)
    
    # Scheduling
    scheduled_date = fields.Datetime(string='Scheduled Date')
    sent_date = fields.Datetime(string='Sent Date', readonly=True)
    delivered_date = fields.Datetime(string='Delivered Date', readonly=True)
    read_date = fields.Datetime(string='Read Date', readonly=True)
    
    # Email Specific
    email_subject = fields.Char(string='Email Subject')
    email_template_id = fields.Many2one('mail.template', string='Email Template')
    
    # SMS Specific
    sms_message = fields.Text(string='SMS Message')
    
    # Ejar Integration
    ejar_notification_id = fields.Char(string='Ejar Notification ID', readonly=True)
    ejar_status = fields.Selection([
        ('not_sent', 'Not Sent to Ejar'),
        ('pending', 'Pending'),
        ('sent', 'Sent to Ejar'),
        ('delivered', 'Delivered by Ejar'),
        ('failed', 'Failed')
    ], string='Ejar Status', default='not_sent')
    
    # Tracking
    read_count = fields.Integer(string='Read Count', default=0)
    click_count = fields.Integer(string='Click Count', default=0)
    
    # Attachments
    attachment_ids = fields.Many2many('ir.attachment', string='Attachments')
    
    # Company
    company_id = fields.Many2one('res.company', string='Company', 
                                 default=lambda self: self.env.company)
    
    # Auto Actions
    auto_resend = fields.Boolean(string='Auto Resend if Failed')
    max_retry_count = fields.Integer(string='Max Retry Count', default=3)
    retry_count = fields.Integer(string='Current Retry Count', default=0)
    
    @api.onchange('notification_type')
    def _onchange_notification_type(self):
        """Set default values based on notification type"""
        if self.notification_type:
            templates = {
                'contract_created': {
                    'title': _('New Contract Created'),
                    'priority': 'medium',
                    'delivery_method': 'email'
                },
                'contract_approved': {
                    'title': _('Contract Approved'),
                    'priority': 'high',
                    'delivery_method': 'all'
                },
                'contract_rejected': {
                    'title': _('Contract Rejected'),
                    'priority': 'high',
                    'delivery_method': 'all'
                },
                'payment_due': {
                    'title': _('Payment Due Reminder'),
                    'priority': 'medium',
                    'delivery_method': 'sms'
                },
                'payment_overdue': {
                    'title': _('Payment Overdue Alert'),
                    'priority': 'urgent',
                    'delivery_method': 'all'
                },
                'compliance_alert': {
                    'title': _('Compliance Alert'),
                    'priority': 'urgent',
                    'delivery_method': 'system'
                }
            }
            
            template = templates.get(self.notification_type, {})
            for field, value in template.items():
                setattr(self, field, value)
    
    @api.onchange('recipient_type')
    def _onchange_recipient_type(self):
        """Clear recipients based on type"""
        if self.recipient_type != 'tenant':
            self.tenant_ids = [(5, 0, 0)]
        if self.recipient_type != 'landlord':
            self.landlord_ids = [(5, 0, 0)]
        if self.recipient_type != 'broker':
            self.broker_ids = [(5, 0, 0)]
        if self.recipient_type != 'custom':
            self.user_ids = [(5, 0, 0)]
    
    def action_send_notification(self):
        """Send notification to recipients"""
        self.ensure_one()
        
        if self.status != 'draft':
            raise UserError(_('Only draft notifications can be sent'))
        
        if not self._get_recipients():
            raise UserError(_('No recipients found for this notification'))
        
        try:
            # Send based on delivery method
            if self.delivery_method in ['email', 'all']:
                self._send_email_notification()
            
            if self.delivery_method in ['sms', 'all']:
                self._send_sms_notification()
            
            if self.delivery_method in ['push', 'all']:
                self._send_push_notification()
            
            if self.delivery_method in ['system', 'all']:
                self._send_system_notification()
            
            # Send to Ejar platform if applicable
            if self._should_send_to_ejar():
                self._send_to_ejar()
            
            self.write({
                'status': 'sent',
                'sent_date': fields.Datetime.now()
            })
            
            self.message_post(
                body=_('Notification sent successfully to %d recipients') % len(self._get_recipients()),
                message_type='notification'
            )
            
            return {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'title': _('Success'),
                    'message': _('Notification sent successfully!'),
                    'type': 'success',
                }
            }
            
        except Exception as e:
            self.write({
                'status': 'failed',
                'retry_count': self.retry_count + 1
            })
            _logger.error(f"Failed to send notification {self.id}: {e}")
            raise UserError(_('Failed to send notification: %s') % str(e))
    
    def _get_recipients(self):
        """Get all recipients based on type"""
        recipients = []
        
        if self.recipient_type == 'tenant':
            recipients.extend(self.tenant_ids)
        elif self.recipient_type == 'landlord':
            recipients.extend(self.landlord_ids)
        elif self.recipient_type == 'broker':
            recipients.extend(self.broker_ids)
        elif self.recipient_type == 'custom':
            recipients.extend(self.user_ids)
        elif self.recipient_type == 'all':
            recipients.extend(self.env['res.users'].search([]))
        
        # Add specific recipients
        if self.tenant_ids:
            recipients.extend(self.tenant_ids)
        if self.landlord_ids:
            recipients.extend(self.landlord_ids)
        if self.broker_ids:
            recipients.extend(self.broker_ids)
        if self.user_ids:
            recipients.extend(self.user_ids)
        
        return list(set(recipients))
    
    def _send_email_notification(self):
        """Send email notification"""
        recipients = self._get_recipients()
        
        # Get email addresses
        email_list = []
        for recipient in recipients:
            if hasattr(recipient, 'email') and recipient.email:
                email_list.append(recipient.email)
            elif hasattr(recipient, 'partner_id') and recipient.partner_id.email:
                email_list.append(recipient.partner_id.email)
        
        if not email_list:
            return
        
        # Use template if available
        if self.email_template_id:
            for email in email_list:
                self.email_template_id.send_mail(
                    self.id,
                    email_values={'email_to': email},
                    force_send=True
                )
        else:
            # Send simple email
            mail_values = {
                'subject': self.email_subject or self.title,
                'body_html': self.message,
                'email_to': ','.join(email_list),
                'auto_delete': True,
            }
            
            if self.attachment_ids:
                mail_values['attachment_ids'] = [(6, 0, self.attachment_ids.ids)]
            
            mail = self.env['mail.mail'].create(mail_values)
            mail.send()
    
    def _send_sms_notification(self):
        """Send SMS notification"""
        recipients = self._get_recipients()
        
        # Get phone numbers
        phone_list = []
        for recipient in recipients:
            phone = None
            if hasattr(recipient, 'mobile') and recipient.mobile:
                phone = recipient.mobile
            elif hasattr(recipient, 'phone') and recipient.phone:
                phone = recipient.phone
            elif hasattr(recipient, 'partner_id'):
                if recipient.partner_id.mobile:
                    phone = recipient.partner_id.mobile
                elif recipient.partner_id.phone:
                    phone = recipient.partner_id.phone
            
            if phone:
                phone_list.append(phone)
        
        if not phone_list:
            return
        
        # Send SMS using SMS gateway
        sms_message = self.sms_message or self.message
        
        for phone in phone_list:
            try:
                # Use Odoo SMS service or external SMS gateway
                self.env['sms.sms'].create({
                    'number': phone,
                    'body': sms_message,
                }).send()
            except Exception as e:
                _logger.warning(f"Failed to send SMS to {phone}: {e}")
    
    def _send_push_notification(self):
        """Send push notification"""
        # Implementation depends on push notification service
        # This is a placeholder for push notification logic
        pass
    
    def _send_system_notification(self):
        """Send system notification"""
        recipients = self._get_recipients()
        
        for recipient in recipients:
            # Create activity or message
            if hasattr(recipient, 'message_post'):
                recipient.message_post(
                    body=self.message,
                    subject=self.title,
                    message_type='notification'
                )
            elif hasattr(recipient, 'partner_id'):
                recipient.partner_id.message_post(
                    body=self.message,
                    subject=self.title,
                    message_type='notification'
                )
    
    def _should_send_to_ejar(self):
        """Check if notification should be sent to Ejar platform"""
        ejar_types = [
            'contract_created', 'contract_approved', 'contract_rejected',
            'contract_expired', 'contract_terminated', 'payment_due',
            'payment_overdue', 'compliance_alert'
        ]
        return self.notification_type in ejar_types
    
    def _send_to_ejar(self):
        """Send notification to Ejar platform"""
        try:
            # Prepare notification data for Ejar API
            notification_data = {
                'title': self.title,
                'message': self.message,
                'type': self.notification_type,
                'priority': self.priority,
                'recipients': self._prepare_ejar_recipients(),
                'related_contract': self.contract_id.ejar_contract_id if self.contract_id else None,
                'related_property': self.property_id.ejar_property_id if self.property_id else None,
            }
            
            # Send to Ejar API
            api_connector = self.env['ejar.api.connector']
            response = api_connector.send_notification(notification_data)
            
            if response.get('success'):
                self.write({
                    'ejar_notification_id': response.get('notification_id'),
                    'ejar_status': 'sent'
                })
            else:
                self.write({'ejar_status': 'failed'})
                
        except Exception as e:
            self.write({'ejar_status': 'failed'})
            _logger.error(f"Failed to send notification to Ejar: {e}")
    
    def _prepare_ejar_recipients(self):
        """Prepare recipient data for Ejar API"""
        recipients = []
        
        for tenant in self.tenant_ids:
            if tenant.ejar_tenant_id:
                recipients.append({
                    'type': 'tenant',
                    'ejar_id': tenant.ejar_tenant_id
                })
        
        for landlord in self.landlord_ids:
            if landlord.ejar_landlord_id:
                recipients.append({
                    'type': 'landlord',
                    'ejar_id': landlord.ejar_landlord_id
                })
        
        for broker in self.broker_ids:
            if broker.ejar_broker_id:
                recipients.append({
                    'type': 'broker',
                    'ejar_id': broker.ejar_broker_id
                })
        
        return recipients
    
    def action_mark_as_read(self):
        """Mark notification as read"""
        self.ensure_one()
        
        if self.status == 'sent':
            self.write({
                'status': 'read',
                'read_date': fields.Datetime.now(),
                'read_count': self.read_count + 1
            })
    
    def action_retry_send(self):
        """Retry sending failed notification"""
        self.ensure_one()
        
        if self.status != 'failed':
            raise UserError(_('Only failed notifications can be retried'))
        
        if self.retry_count >= self.max_retry_count:
            raise UserError(_('Maximum retry count reached'))
        
        self.write({'status': 'draft'})
        return self.action_send_notification()
    
    @api.model
    def create_contract_notification(self, contract, notification_type, recipients=None):
        """Create contract-related notification"""
        titles = {
            'contract_created': _('New Contract Created'),
            'contract_approved': _('Contract Approved'),
            'contract_rejected': _('Contract Rejected'),
            'contract_expired': _('Contract Expired'),
            'contract_terminated': _('Contract Terminated'),
        }
        
        messages = {
            'contract_created': _('A new rental contract has been created for property: %s') % contract.property_id.name,
            'contract_approved': _('Your rental contract for property %s has been approved') % contract.property_id.name,
            'contract_rejected': _('Your rental contract for property %s has been rejected') % contract.property_id.name,
            'contract_expired': _('Your rental contract for property %s has expired') % contract.property_id.name,
            'contract_terminated': _('Your rental contract for property %s has been terminated') % contract.property_id.name,
        }
        
        notification_vals = {
            'title': titles.get(notification_type, _('Contract Notification')),
            'message': messages.get(notification_type, _('Contract status updated')),
            'notification_type': notification_type,
            'contract_id': contract.id,
            'property_id': contract.property_id.id,
            'tenant_id': contract.tenant_id.id if contract.tenant_id else False,
            'landlord_id': contract.landlord_id.id if contract.landlord_id else False,
            'broker_id': contract.broker_id.id if contract.broker_id else False,
        }
        
        # Set recipients
        if recipients:
            if 'tenant' in recipients and contract.tenant_id:
                notification_vals['tenant_ids'] = [(4, contract.tenant_id.id)]
            if 'landlord' in recipients and contract.landlord_id:
                notification_vals['landlord_ids'] = [(4, contract.landlord_id.id)]
            if 'broker' in recipients and contract.broker_id:
                notification_vals['broker_ids'] = [(4, contract.broker_id.id)]
        
        notification = self.create(notification_vals)
        
        # Auto-send if configured
        if self.env.company.ejar_auto_send_notifications:
            notification.action_send_notification()
        
        return notification
    
    @api.model
    def create_payment_notification(self, contract, notification_type, amount=0):
        """Create payment-related notification"""
        titles = {
            'payment_due': _('Payment Due Reminder'),
            'payment_overdue': _('Payment Overdue Alert'),
            'payment_received': _('Payment Received Confirmation'),
        }
        
        messages = {
            'payment_due': _('Payment of %s SAR is due for your rental contract') % amount,
            'payment_overdue': _('Payment of %s SAR is overdue for your rental contract') % amount,
            'payment_received': _('Payment of %s SAR has been received for your rental contract') % amount,
        }
        
        notification_vals = {
            'title': titles.get(notification_type, _('Payment Notification')),
            'message': messages.get(notification_type, _('Payment status updated')),
            'notification_type': notification_type,
            'contract_id': contract.id,
            'property_id': contract.property_id.id,
            'tenant_id': contract.tenant_id.id if contract.tenant_id else False,
            'landlord_id': contract.landlord_id.id if contract.landlord_id else False,
            'priority': 'high' if notification_type == 'payment_overdue' else 'medium',
        }
        
        notification = self.create(notification_vals)
        
        # Auto-send if configured
        if self.env.company.ejar_auto_send_notifications:
            notification.action_send_notification()
        
        return notification
    
    @api.model
    def _cron_send_scheduled_notifications(self):
        """Cron job to send scheduled notifications"""
        scheduled_notifications = self.search([
            ('status', '=', 'draft'),
            ('scheduled_date', '<=', fields.Datetime.now())
        ])
        
        for notification in scheduled_notifications:
            try:
                notification.action_send_notification()
            except Exception as e:
                _logger.error(f"Failed to send scheduled notification {notification.id}: {e}")
    
    @api.model
    def _cron_retry_failed_notifications(self):
        """Cron job to retry failed notifications"""
        failed_notifications = self.search([
            ('status', '=', 'failed'),
            ('auto_resend', '=', True),
            ('retry_count', '<', 'max_retry_count')
        ])
        
        for notification in failed_notifications:
            try:
                notification.action_retry_send()
            except Exception as e:
                _logger.error(f"Failed to retry notification {notification.id}: {e}")


class EjarNotificationTemplate(models.Model):
    """Notification templates for common scenarios"""
    _name = 'ejar.notification.template'
    _description = 'Notification Template'
    _order = 'name'

    name = fields.Char(string='Template Name', required=True)
    notification_type = fields.Selection([
        ('contract_created', 'Contract Created'),
        ('contract_approved', 'Contract Approved'),
        ('contract_rejected', 'Contract Rejected'),
        ('contract_expired', 'Contract Expired'),
        ('contract_terminated', 'Contract Terminated'),
        ('payment_due', 'Payment Due'),
        ('payment_overdue', 'Payment Overdue'),
        ('payment_received', 'Payment Received'),
        ('property_registered', 'Property Registered'),
        ('tenant_registered', 'Tenant Registered'),
        ('landlord_registered', 'Landlord Registered'),
        ('broker_registered', 'Broker Registered'),
        ('compliance_alert', 'Compliance Alert'),
        ('system_update', 'System Update'),
        ('maintenance_required', 'Maintenance Required'),
        ('document_expiry', 'Document Expiry'),
        ('other', 'Other')
    ], string='Type', required=True)
    
    title_template = fields.Char(string='Title Template', required=True)
    message_template = fields.Text(string='Message Template', required=True)
    email_subject_template = fields.Char(string='Email Subject Template')
    sms_template = fields.Text(string='SMS Template')
    
    priority = fields.Selection([
        ('low', 'Low'),
        ('medium', 'Medium'),
        ('high', 'High'),
        ('urgent', 'Urgent')
    ], string='Default Priority', default='medium')
    
    delivery_method = fields.Selection([
        ('email', 'Email'),
        ('sms', 'SMS'),
        ('push', 'Push Notification'),
        ('system', 'System Notification'),
        ('all', 'All Methods')
    ], string='Default Delivery Method', default='system')
    
    active = fields.Boolean(string='Active', default=True)
    
    def generate_notification(self, context_data):
        """Generate notification from template"""
        title = self._render_template(self.title_template, context_data)
        message = self._render_template(self.message_template, context_data)
        email_subject = self._render_template(self.email_subject_template, context_data) if self.email_subject_template else title
        sms_message = self._render_template(self.sms_template, context_data) if self.sms_template else message
        
        return {
            'title': title,
            'message': message,
            'email_subject': email_subject,
            'sms_message': sms_message,
            'notification_type': self.notification_type,
            'priority': self.priority,
            'delivery_method': self.delivery_method,
        }
    
    def _render_template(self, template, context_data):
        """Render template with context data"""
        if not template:
            return ''
        
        try:
            # Simple template rendering - can be enhanced with Jinja2
            rendered = template
            for key, value in context_data.items():
                placeholder = '${%s}' % key
                rendered = rendered.replace(placeholder, str(value or ''))
            return rendered
        except Exception as e:
            _logger.error(f"Failed to render template: {e}")
            return template