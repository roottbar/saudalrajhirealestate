# -*- coding: utf-8 -*-

import json
import logging
from datetime import datetime, timedelta
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

from odoo import api, fields, models, _
from odoo.exceptions import ValidationError, UserError
from odoo.tools import html2plaintext

_logger = logging.getLogger(__name__)


class EjarNotificationHelpers:
    """Helper functions for Ejar notification management"""

    @staticmethod
    def send_notification(env, notification_type, recipients, title, message, priority='medium', 
                         delivery_methods=None, scheduled_date=None, context_data=None):
        """Send a notification through multiple channels"""
        if delivery_methods is None:
            delivery_methods = ['email', 'system']
        
        if context_data is None:
            context_data = {}
        
        # Create notification record
        notification = env['ejar.notification'].create({
            'title': title,
            'message': message,
            'notification_type': notification_type,
            'priority': priority,
            'delivery_methods': ','.join(delivery_methods),
            'scheduled_date': scheduled_date or fields.Datetime.now(),
            'status': 'scheduled' if scheduled_date else 'pending',
            'context_data': json.dumps(context_data),
        })
        
        # Add recipients
        for recipient in recipients:
            env['ejar.notification.recipient'].create({
                'notification_id': notification.id,
                'partner_id': recipient.get('partner_id'),
                'email': recipient.get('email'),
                'phone': recipient.get('phone'),
                'delivery_status': 'pending',
            })
        
        # Send immediately if not scheduled
        if not scheduled_date:
            return EjarNotificationHelpers.process_notification(notification)
        
        return notification

    @staticmethod
    def process_notification(notification):
        """Process a single notification"""
        try:
            notification.write({'status': 'processing'})
            
            delivery_methods = notification.delivery_methods.split(',')
            results = {
                'success': 0,
                'failed': 0,
                'errors': []
            }
            
            for recipient in notification.recipient_ids:
                for method in delivery_methods:
                    try:
                        if method == 'email':
                            success = EjarNotificationHelpers._send_email(notification, recipient)
                        elif method == 'sms':
                            success = EjarNotificationHelpers._send_sms(notification, recipient)
                        elif method == 'push':
                            success = EjarNotificationHelpers._send_push_notification(notification, recipient)
                        elif method == 'system':
                            success = EjarNotificationHelpers._create_system_notification(notification, recipient)
                        else:
                            success = False
                            results['errors'].append(f"Unknown delivery method: {method}")
                        
                        if success:
                            results['success'] += 1
                        else:
                            results['failed'] += 1
                    
                    except Exception as e:
                        results['failed'] += 1
                        results['errors'].append(f"Error sending {method} to {recipient.email or recipient.phone}: {str(e)}")
            
            # Update notification status
            if results['failed'] == 0:
                notification.write({'status': 'sent', 'sent_date': fields.Datetime.now()})
            elif results['success'] == 0:
                notification.write({'status': 'failed'})
            else:
                notification.write({'status': 'partial', 'sent_date': fields.Datetime.now()})
            
            return results
            
        except Exception as e:
            notification.write({'status': 'failed', 'error_message': str(e)})
            _logger.error("Failed to process notification %s: %s", notification.id, str(e))
            return {'success': 0, 'failed': 1, 'errors': [str(e)]}

    @staticmethod
    def _send_email(notification, recipient):
        """Send email notification"""
        try:
            email = recipient.email or (recipient.partner_id and recipient.partner_id.email)
            if not email:
                return False
            
            # Prepare email content
            subject = notification.title
            body_html = EjarNotificationHelpers._prepare_email_template(notification, recipient)
            body_text = html2plaintext(body_html)
            
            # Send email using Odoo's mail system
            mail_values = {
                'subject': subject,
                'body_html': body_html,
                'email_to': email,
                'email_from': notification.env.user.company_id.email or 'noreply@example.com',
                'auto_delete': True,
            }
            
            mail = notification.env['mail.mail'].create(mail_values)
            mail.send()
            
            # Update recipient status
            recipient.write({
                'delivery_status': 'sent',
                'delivery_date': fields.Datetime.now(),
            })
            
            return True
            
        except Exception as e:
            recipient.write({
                'delivery_status': 'failed',
                'error_message': str(e),
            })
            _logger.error("Failed to send email to %s: %s", email, str(e))
            return False

    @staticmethod
    def _send_sms(notification, recipient):
        """Send SMS notification"""
        try:
            phone = recipient.phone or (recipient.partner_id and recipient.partner_id.mobile)
            if not phone:
                return False
            
            # Format phone number for Saudi Arabia
            from .ejar_helpers import EjarHelpers
            formatted_phone = EjarHelpers.format_saudi_phone(phone)
            if not formatted_phone:
                return False
            
            # Prepare SMS content
            message = EjarNotificationHelpers._prepare_sms_template(notification, recipient)
            
            # Send SMS using configured SMS gateway
            sms_gateway = notification.env['ir.config_parameter'].sudo().get_param('ejar.sms_gateway')
            
            if sms_gateway == 'twilio':
                success = EjarNotificationHelpers._send_twilio_sms(formatted_phone, message, notification.env)
            elif sms_gateway == 'local':
                success = EjarNotificationHelpers._send_local_sms(formatted_phone, message, notification.env)
            else:
                _logger.warning("No SMS gateway configured")
                return False
            
            if success:
                recipient.write({
                    'delivery_status': 'sent',
                    'delivery_date': fields.Datetime.now(),
                })
            else:
                recipient.write({'delivery_status': 'failed'})
            
            return success
            
        except Exception as e:
            recipient.write({
                'delivery_status': 'failed',
                'error_message': str(e),
            })
            _logger.error("Failed to send SMS to %s: %s", phone, str(e))
            return False

    @staticmethod
    def _send_push_notification(notification, recipient):
        """Send push notification"""
        try:
            if not recipient.partner_id:
                return False
            
            # Create push notification record
            push_notification = notification.env['ejar.push.notification'].create({
                'partner_id': recipient.partner_id.id,
                'title': notification.title,
                'message': notification.message,
                'notification_type': notification.notification_type,
                'priority': notification.priority,
                'status': 'pending',
            })
            
            # Send through configured push service
            push_service = notification.env['ir.config_parameter'].sudo().get_param('ejar.push_service')
            
            if push_service == 'firebase':
                success = EjarNotificationHelpers._send_firebase_push(push_notification)
            else:
                _logger.warning("No push notification service configured")
                return False
            
            if success:
                recipient.write({
                    'delivery_status': 'sent',
                    'delivery_date': fields.Datetime.now(),
                })
                push_notification.write({'status': 'sent'})
            else:
                recipient.write({'delivery_status': 'failed'})
                push_notification.write({'status': 'failed'})
            
            return success
            
        except Exception as e:
            recipient.write({
                'delivery_status': 'failed',
                'error_message': str(e),
            })
            _logger.error("Failed to send push notification: %s", str(e))
            return False

    @staticmethod
    def _create_system_notification(notification, recipient):
        """Create system notification"""
        try:
            if not recipient.partner_id:
                return False
            
            # Create activity or message
            notification.env['mail.activity'].create({
                'activity_type_id': notification.env.ref('mail.mail_activity_data_todo').id,
                'summary': notification.title,
                'note': notification.message,
                'user_id': recipient.partner_id.user_ids[0].id if recipient.partner_id.user_ids else notification.env.user.id,
                'res_model': 'res.partner',
                'res_id': recipient.partner_id.id,
                'date_deadline': fields.Date.today(),
            })
            
            recipient.write({
                'delivery_status': 'sent',
                'delivery_date': fields.Datetime.now(),
            })
            
            return True
            
        except Exception as e:
            recipient.write({
                'delivery_status': 'failed',
                'error_message': str(e),
            })
            _logger.error("Failed to create system notification: %s", str(e))
            return False

    @staticmethod
    def _prepare_email_template(notification, recipient):
        """Prepare email template"""
        partner_name = recipient.partner_id.name if recipient.partner_id else _("Valued Customer")
        
        template = f"""
        <html>
        <head>
            <style>
                body {{ font-family: Arial, sans-serif; margin: 0; padding: 20px; background-color: #f5f5f5; }}
                .container {{ max-width: 600px; margin: 0 auto; background-color: white; padding: 30px; border-radius: 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }}
                .header {{ text-align: center; margin-bottom: 30px; }}
                .logo {{ max-width: 200px; height: auto; }}
                .title {{ color: #2c3e50; font-size: 24px; margin: 20px 0; }}
                .message {{ color: #34495e; font-size: 16px; line-height: 1.6; margin: 20px 0; }}
                .footer {{ text-align: center; margin-top: 30px; padding-top: 20px; border-top: 1px solid #eee; color: #7f8c8d; font-size: 14px; }}
                .priority-high {{ border-left: 4px solid #e74c3c; padding-left: 15px; }}
                .priority-medium {{ border-left: 4px solid #f39c12; padding-left: 15px; }}
                .priority-low {{ border-left: 4px solid #27ae60; padding-left: 15px; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1 class="title">إيجار - منصة الإيجار الإلكترونية</h1>
                </div>
                
                <div class="message priority-{notification.priority}">
                    <p>عزيزي/عزيزتي {partner_name}،</p>
                    <p>{notification.message}</p>
                </div>
                
                <div class="footer">
                    <p>هذه رسالة تلقائية من منصة إيجار</p>
                    <p>لا تتردد في التواصل معنا إذا كان لديك أي استفسارات</p>
                </div>
            </div>
        </body>
        </html>
        """
        
        return template

    @staticmethod
    def _prepare_sms_template(notification, recipient):
        """Prepare SMS template"""
        partner_name = recipient.partner_id.name if recipient.partner_id else _("Valued Customer")
        
        # Keep SMS short and concise
        message = f"إيجار: {notification.title}\n{notification.message[:100]}..."
        if len(notification.message) <= 100:
            message = f"إيجار: {notification.title}\n{notification.message}"
        
        return message

    @staticmethod
    def _send_twilio_sms(phone, message, env):
        """Send SMS using Twilio"""
        try:
            # Get Twilio configuration
            account_sid = env['ir.config_parameter'].sudo().get_param('ejar.twilio_account_sid')
            auth_token = env['ir.config_parameter'].sudo().get_param('ejar.twilio_auth_token')
            from_number = env['ir.config_parameter'].sudo().get_param('ejar.twilio_from_number')
            
            if not all([account_sid, auth_token, from_number]):
                _logger.error("Twilio configuration incomplete")
                return False
            
            # Import Twilio client (requires twilio package)
            try:
                from twilio.rest import Client
                client = Client(account_sid, auth_token)
                
                message = client.messages.create(
                    body=message,
                    from_=from_number,
                    to=phone
                )
                
                _logger.info("SMS sent successfully via Twilio: %s", message.sid)
                return True
                
            except ImportError:
                _logger.error("Twilio package not installed")
                return False
            
        except Exception as e:
            _logger.error("Failed to send SMS via Twilio: %s", str(e))
            return False

    @staticmethod
    def _send_local_sms(phone, message, env):
        """Send SMS using local SMS gateway"""
        try:
            # Get local SMS gateway configuration
            gateway_url = env['ir.config_parameter'].sudo().get_param('ejar.sms_gateway_url')
            api_key = env['ir.config_parameter'].sudo().get_param('ejar.sms_api_key')
            
            if not all([gateway_url, api_key]):
                _logger.error("Local SMS gateway configuration incomplete")
                return False
            
            import requests
            
            payload = {
                'phone': phone,
                'message': message,
                'api_key': api_key,
            }
            
            response = requests.post(gateway_url, json=payload, timeout=30)
            
            if response.status_code == 200:
                _logger.info("SMS sent successfully via local gateway")
                return True
            else:
                _logger.error("SMS gateway returned error: %s", response.text)
                return False
            
        except Exception as e:
            _logger.error("Failed to send SMS via local gateway: %s", str(e))
            return False

    @staticmethod
    def _send_firebase_push(push_notification):
        """Send push notification using Firebase"""
        try:
            # Get Firebase configuration
            env = push_notification.env
            server_key = env['ir.config_parameter'].sudo().get_param('ejar.firebase_server_key')
            
            if not server_key:
                _logger.error("Firebase server key not configured")
                return False
            
            # Get user's device tokens
            device_tokens = env['ejar.device.token'].search([
                ('partner_id', '=', push_notification.partner_id.id),
                ('active', '=', True)
            ]).mapped('token')
            
            if not device_tokens:
                _logger.warning("No device tokens found for partner %s", push_notification.partner_id.name)
                return False
            
            import requests
            
            headers = {
                'Authorization': f'key={server_key}',
                'Content-Type': 'application/json',
            }
            
            payload = {
                'registration_ids': device_tokens,
                'notification': {
                    'title': push_notification.title,
                    'body': push_notification.message,
                    'icon': 'ic_notification',
                    'sound': 'default',
                },
                'data': {
                    'type': push_notification.notification_type,
                    'priority': push_notification.priority,
                }
            }
            
            response = requests.post(
                'https://fcm.googleapis.com/fcm/send',
                headers=headers,
                json=payload,
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                if result.get('success', 0) > 0:
                    _logger.info("Push notification sent successfully")
                    return True
                else:
                    _logger.error("Push notification failed: %s", result)
                    return False
            else:
                _logger.error("Firebase returned error: %s", response.text)
                return False
            
        except Exception as e:
            _logger.error("Failed to send push notification: %s", str(e))
            return False

    @staticmethod
    def process_scheduled_notifications(env, limit=100):
        """Process scheduled notifications"""
        now = fields.Datetime.now()
        
        scheduled_notifications = env['ejar.notification'].search([
            ('status', '=', 'scheduled'),
            ('scheduled_date', '<=', now)
        ], limit=limit, order='scheduled_date asc')
        
        results = {
            'processed': 0,
            'success': 0,
            'failed': 0,
            'errors': []
        }
        
        for notification in scheduled_notifications:
            try:
                result = EjarNotificationHelpers.process_notification(notification)
                results['processed'] += 1
                
                if result['failed'] == 0:
                    results['success'] += 1
                else:
                    results['failed'] += 1
                    results['errors'].extend(result['errors'])
                    
            except Exception as e:
                results['failed'] += 1
                results['errors'].append(f"Error processing notification {notification.id}: {str(e)}")
        
        return results

    @staticmethod
    def create_contract_notification(env, contract, notification_type, **kwargs):
        """Create contract-related notification"""
        recipients = []
        
        # Add tenant
        if contract.tenant_id:
            recipients.append({
                'partner_id': contract.tenant_id.partner_id.id if contract.tenant_id.partner_id else None,
                'email': contract.tenant_id.email,
                'phone': contract.tenant_id.phone,
            })
        
        # Add landlord
        if contract.landlord_id:
            recipients.append({
                'partner_id': contract.landlord_id.partner_id.id if contract.landlord_id.partner_id else None,
                'email': contract.landlord_id.email,
                'phone': contract.landlord_id.phone,
            })
        
        # Add broker if exists
        if contract.broker_id:
            recipients.append({
                'partner_id': contract.broker_id.partner_id.id if contract.broker_id.partner_id else None,
                'email': contract.broker_id.email,
                'phone': contract.broker_id.phone,
            })
        
        # Prepare notification content based on type
        templates = {
            'contract_created': {
                'title': _("New Contract Created"),
                'message': _("A new rental contract has been created for property: %s") % contract.property_id.name,
            },
            'contract_expiring': {
                'title': _("Contract Expiring Soon"),
                'message': _("Your rental contract for property %s will expire on %s") % (
                    contract.property_id.name, contract.end_date
                ),
            },
            'payment_due': {
                'title': _("Payment Due"),
                'message': _("Payment of %s SAR is due for your rental contract") % contract.monthly_rent,
            },
            'payment_overdue': {
                'title': _("Payment Overdue"),
                'message': _("Your payment of %s SAR is overdue. Please make payment immediately.") % contract.monthly_rent,
            },
        }
        
        template = templates.get(notification_type, {
            'title': _("Contract Notification"),
            'message': _("You have a new notification regarding your rental contract"),
        })
        
        context_data = {
            'contract_id': contract.id,
            'property_name': contract.property_id.name,
            'monthly_rent': contract.monthly_rent,
            'start_date': str(contract.start_date),
            'end_date': str(contract.end_date),
        }
        
        return EjarNotificationHelpers.send_notification(
            env=env,
            notification_type='contract',
            recipients=recipients,
            title=template['title'],
            message=template['message'],
            priority=kwargs.get('priority', 'medium'),
            delivery_methods=kwargs.get('delivery_methods', ['email', 'sms', 'system']),
            scheduled_date=kwargs.get('scheduled_date'),
            context_data=context_data,
        )

    @staticmethod
    def create_payment_notification(env, payment, notification_type, **kwargs):
        """Create payment-related notification"""
        recipients = []
        
        # Add relevant parties based on payment type
        if payment.contract_id:
            if payment.contract_id.tenant_id:
                recipients.append({
                    'partner_id': payment.contract_id.tenant_id.partner_id.id if payment.contract_id.tenant_id.partner_id else None,
                    'email': payment.contract_id.tenant_id.email,
                    'phone': payment.contract_id.tenant_id.phone,
                })
            
            if payment.contract_id.landlord_id:
                recipients.append({
                    'partner_id': payment.contract_id.landlord_id.partner_id.id if payment.contract_id.landlord_id.partner_id else None,
                    'email': payment.contract_id.landlord_id.email,
                    'phone': payment.contract_id.landlord_id.phone,
                })
        
        templates = {
            'payment_received': {
                'title': _("Payment Received"),
                'message': _("Payment of %s SAR has been received successfully") % payment.amount,
            },
            'payment_failed': {
                'title': _("Payment Failed"),
                'message': _("Payment of %s SAR has failed. Please try again.") % payment.amount,
            },
        }
        
        template = templates.get(notification_type, {
            'title': _("Payment Notification"),
            'message': _("You have a new payment notification"),
        })
        
        context_data = {
            'payment_id': payment.id,
            'amount': payment.amount,
            'payment_date': str(payment.payment_date),
            'payment_method': payment.payment_method,
        }
        
        return EjarNotificationHelpers.send_notification(
            env=env,
            notification_type='payment',
            recipients=recipients,
            title=template['title'],
            message=template['message'],
            priority=kwargs.get('priority', 'medium'),
            delivery_methods=kwargs.get('delivery_methods', ['email', 'sms', 'system']),
            context_data=context_data,
        )