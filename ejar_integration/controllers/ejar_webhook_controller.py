# -*- coding: utf-8 -*-

import json
import logging
import hmac
import hashlib
from datetime import datetime

from odoo import http, fields, _
from odoo.http import request, Response
from odoo.exceptions import ValidationError, UserError

_logger = logging.getLogger(__name__)


class EjarWebhookController(http.Controller):
    """Controller for handling Ejar webhook notifications"""

    def _verify_webhook_signature(self, payload, signature, secret):
        """Verify webhook signature for security"""
        if not signature or not secret:
            return False
        
        # Remove 'sha256=' prefix if present
        if signature.startswith('sha256='):
            signature = signature[7:]
        
        # Calculate expected signature
        expected_signature = hmac.new(
            secret.encode('utf-8'),
            payload,
            hashlib.sha256
        ).hexdigest()
        
        return hmac.compare_digest(signature, expected_signature)
    
    def _create_webhook_response(self, success=True, message=None, code=200):
        """Create standardized webhook response"""
        response_data = {
            'success': success,
            'message': message or ('Webhook processed successfully' if success else 'Webhook processing failed'),
            'timestamp': datetime.now().isoformat()
        }
        
        return Response(
            json.dumps(response_data),
            content_type='application/json',
            status=code
        )
    
    def _log_webhook_event(self, event_type, payload, status='received', error_message=None):
        """Log webhook event for tracking"""
        try:
            request.env['ejar.sync.log'].sudo().create({
                'operation_type': 'webhook',
                'direction': 'inbound',
                'status': status,
                'webhook_event_type': event_type,
                'webhook_payload': json.dumps(payload, default=str),
                'error_message': error_message,
                'company_id': request.env.company.id,
            })
        except Exception as e:
            _logger.error(f"Failed to log webhook event: {e}")

    @http.route('/webhook/ejar/notifications', type='http', auth='none', methods=['POST'], csrf=False)
    def handle_ejar_webhook(self, **kwargs):
        """Main webhook endpoint for Ejar notifications"""
        try:
            # Get raw payload
            payload = request.httprequest.get_data()
            
            # Parse JSON data
            try:
                data = json.loads(payload.decode('utf-8'))
            except (ValueError, UnicodeDecodeError) as e:
                _logger.error(f"Invalid JSON in webhook payload: {e}")
                return self._create_webhook_response(False, 'Invalid JSON payload', 400)
            
            # Get headers
            signature = request.httprequest.headers.get('X-Ejar-Signature')
            event_type = request.httprequest.headers.get('X-Ejar-Event')
            
            if not event_type:
                _logger.error("Missing X-Ejar-Event header")
                return self._create_webhook_response(False, 'Missing event type header', 400)
            
            # Get webhook secret from connector
            connector = request.env['ejar.api.connector'].sudo().get_active_connector()
            if not connector:
                _logger.error("No active Ejar connector found")
                return self._create_webhook_response(False, 'No active connector', 500)
            
            # Verify signature if webhook secret is configured
            if connector.webhook_secret:
                if not self._verify_webhook_signature(payload, signature, connector.webhook_secret):
                    _logger.error("Invalid webhook signature")
                    self._log_webhook_event(event_type, data, 'failed', 'Invalid signature')
                    return self._create_webhook_response(False, 'Invalid signature', 401)
            
            # Log webhook event
            self._log_webhook_event(event_type, data, 'processing')
            
            # Process webhook based on event type
            result = self._process_webhook_event(event_type, data)
            
            if result.get('success'):
                self._log_webhook_event(event_type, data, 'success')
                return self._create_webhook_response(True, result.get('message'))
            else:
                self._log_webhook_event(event_type, data, 'failed', result.get('error'))
                return self._create_webhook_response(False, result.get('error'), 500)
                
        except Exception as e:
            _logger.error(f"Webhook processing error: {e}")
            self._log_webhook_event(event_type if 'event_type' in locals() else 'unknown', 
                                  data if 'data' in locals() else {}, 'failed', str(e))
            return self._create_webhook_response(False, str(e), 500)
    
    def _process_webhook_event(self, event_type, data):
        """Process webhook event based on type"""
        try:
            # Route to specific handler based on event type
            if event_type == 'contract.created':
                return self._handle_contract_created(data)
            elif event_type == 'contract.updated':
                return self._handle_contract_updated(data)
            elif event_type == 'contract.terminated':
                return self._handle_contract_terminated(data)
            elif event_type == 'property.updated':
                return self._handle_property_updated(data)
            elif event_type == 'tenant.verified':
                return self._handle_tenant_verified(data)
            elif event_type == 'tenant.updated':
                return self._handle_tenant_updated(data)
            elif event_type == 'landlord.verified':
                return self._handle_landlord_verified(data)
            elif event_type == 'landlord.updated':
                return self._handle_landlord_updated(data)
            elif event_type == 'payment.received':
                return self._handle_payment_received(data)
            elif event_type == 'payment.failed':
                return self._handle_payment_failed(data)
            elif event_type == 'compliance.violation':
                return self._handle_compliance_violation(data)
            elif event_type == 'document.uploaded':
                return self._handle_document_uploaded(data)
            elif event_type == 'notification.sent':
                return self._handle_notification_sent(data)
            else:
                _logger.warning(f"Unknown webhook event type: {event_type}")
                return {'success': True, 'message': f'Unknown event type: {event_type}'}
                
        except Exception as e:
            _logger.error(f"Error processing webhook event {event_type}: {e}")
            return {'success': False, 'error': str(e)}
    
    def _handle_contract_created(self, data):
        """Handle contract created webhook"""
        try:
            ejar_contract_id = data.get('contract_id')
            if not ejar_contract_id:
                return {'success': False, 'error': 'Missing contract_id in webhook data'}
            
            # Check if contract already exists
            existing_contract = request.env['ejar.contract'].sudo().search([
                ('ejar_contract_id', '=', ejar_contract_id)
            ], limit=1)
            
            if existing_contract:
                # Update existing contract
                existing_contract.write({
                    'ejar_sync_status': 'synced',
                    'last_ejar_sync': fields.Datetime.now(),
                })
                return {'success': True, 'message': f'Contract {ejar_contract_id} updated'}
            else:
                # Create new contract from Ejar data
                contract_data = self._prepare_contract_data_from_webhook(data)
                if contract_data:
                    new_contract = request.env['ejar.contract'].sudo().create(contract_data)
                    return {'success': True, 'message': f'Contract {ejar_contract_id} created with ID {new_contract.id}'}
                else:
                    return {'success': False, 'error': 'Failed to prepare contract data'}
                    
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def _handle_contract_updated(self, data):
        """Handle contract updated webhook"""
        try:
            ejar_contract_id = data.get('contract_id')
            if not ejar_contract_id:
                return {'success': False, 'error': 'Missing contract_id in webhook data'}
            
            # Find existing contract
            contract = request.env['ejar.contract'].sudo().search([
                ('ejar_contract_id', '=', ejar_contract_id)
            ], limit=1)
            
            if not contract:
                return {'success': False, 'error': f'Contract {ejar_contract_id} not found'}
            
            # Update contract with new data
            update_data = self._prepare_contract_update_data_from_webhook(data)
            if update_data:
                contract.write(update_data)
                return {'success': True, 'message': f'Contract {ejar_contract_id} updated'}
            else:
                return {'success': True, 'message': 'No updates needed'}
                
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def _handle_contract_terminated(self, data):
        """Handle contract terminated webhook"""
        try:
            ejar_contract_id = data.get('contract_id')
            if not ejar_contract_id:
                return {'success': False, 'error': 'Missing contract_id in webhook data'}
            
            # Find existing contract
            contract = request.env['ejar.contract'].sudo().search([
                ('ejar_contract_id', '=', ejar_contract_id)
            ], limit=1)
            
            if not contract:
                return {'success': False, 'error': f'Contract {ejar_contract_id} not found'}
            
            # Update contract status
            contract.write({
                'status': 'terminated',
                'termination_date': data.get('termination_date', fields.Date.today()),
                'termination_reason': data.get('termination_reason'),
                'ejar_sync_status': 'synced',
                'last_ejar_sync': fields.Datetime.now(),
            })
            
            # Update property status to available
            if contract.property_id:
                contract.property_id.write({'status': 'available'})
            
            return {'success': True, 'message': f'Contract {ejar_contract_id} terminated'}
                
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def _handle_property_updated(self, data):
        """Handle property updated webhook"""
        try:
            ejar_property_id = data.get('property_id')
            if not ejar_property_id:
                return {'success': False, 'error': 'Missing property_id in webhook data'}
            
            # Find existing property
            property_rec = request.env['ejar.property'].sudo().search([
                ('ejar_property_id', '=', ejar_property_id)
            ], limit=1)
            
            if not property_rec:
                return {'success': False, 'error': f'Property {ejar_property_id} not found'}
            
            # Update property with new data
            update_data = self._prepare_property_update_data_from_webhook(data)
            if update_data:
                property_rec.write(update_data)
                return {'success': True, 'message': f'Property {ejar_property_id} updated'}
            else:
                return {'success': True, 'message': 'No updates needed'}
                
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def _handle_tenant_verified(self, data):
        """Handle tenant verified webhook"""
        try:
            ejar_tenant_id = data.get('tenant_id')
            if not ejar_tenant_id:
                return {'success': False, 'error': 'Missing tenant_id in webhook data'}
            
            # Find existing tenant
            tenant = request.env['ejar.tenant'].sudo().search([
                ('ejar_tenant_id', '=', ejar_tenant_id)
            ], limit=1)
            
            if not tenant:
                return {'success': False, 'error': f'Tenant {ejar_tenant_id} not found'}
            
            # Update tenant verification status
            tenant.write({
                'verification_status': 'verified',
                'verification_date': data.get('verification_date', fields.Datetime.now()),
                'ejar_sync_status': 'synced',
                'last_ejar_sync': fields.Datetime.now(),
            })
            
            return {'success': True, 'message': f'Tenant {ejar_tenant_id} verified'}
                
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def _handle_tenant_updated(self, data):
        """Handle tenant updated webhook"""
        try:
            ejar_tenant_id = data.get('tenant_id')
            if not ejar_tenant_id:
                return {'success': False, 'error': 'Missing tenant_id in webhook data'}
            
            # Find existing tenant
            tenant = request.env['ejar.tenant'].sudo().search([
                ('ejar_tenant_id', '=', ejar_tenant_id)
            ], limit=1)
            
            if not tenant:
                return {'success': False, 'error': f'Tenant {ejar_tenant_id} not found'}
            
            # Update tenant with new data
            update_data = self._prepare_tenant_update_data_from_webhook(data)
            if update_data:
                tenant.write(update_data)
                return {'success': True, 'message': f'Tenant {ejar_tenant_id} updated'}
            else:
                return {'success': True, 'message': 'No updates needed'}
                
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def _handle_landlord_verified(self, data):
        """Handle landlord verified webhook"""
        try:
            ejar_landlord_id = data.get('landlord_id')
            if not ejar_landlord_id:
                return {'success': False, 'error': 'Missing landlord_id in webhook data'}
            
            # Find existing landlord
            landlord = request.env['ejar.landlord'].sudo().search([
                ('ejar_landlord_id', '=', ejar_landlord_id)
            ], limit=1)
            
            if not landlord:
                return {'success': False, 'error': f'Landlord {ejar_landlord_id} not found'}
            
            # Update landlord verification status
            landlord.write({
                'verification_status': 'verified',
                'verification_date': data.get('verification_date', fields.Datetime.now()),
                'ejar_sync_status': 'synced',
                'last_ejar_sync': fields.Datetime.now(),
            })
            
            return {'success': True, 'message': f'Landlord {ejar_landlord_id} verified'}
                
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def _handle_landlord_updated(self, data):
        """Handle landlord updated webhook"""
        try:
            ejar_landlord_id = data.get('landlord_id')
            if not ejar_landlord_id:
                return {'success': False, 'error': 'Missing landlord_id in webhook data'}
            
            # Find existing landlord
            landlord = request.env['ejar.landlord'].sudo().search([
                ('ejar_landlord_id', '=', ejar_landlord_id)
            ], limit=1)
            
            if not landlord:
                return {'success': False, 'error': f'Landlord {ejar_landlord_id} not found'}
            
            # Update landlord with new data
            update_data = self._prepare_landlord_update_data_from_webhook(data)
            if update_data:
                landlord.write(update_data)
                return {'success': True, 'message': f'Landlord {ejar_landlord_id} updated'}
            else:
                return {'success': True, 'message': 'No updates needed'}
                
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def _handle_payment_received(self, data):
        """Handle payment received webhook"""
        try:
            payment_id = data.get('payment_id')
            contract_id = data.get('contract_id')
            
            if not payment_id or not contract_id:
                return {'success': False, 'error': 'Missing payment_id or contract_id in webhook data'}
            
            # Find contract
            contract = request.env['ejar.contract'].sudo().search([
                ('ejar_contract_id', '=', contract_id)
            ], limit=1)
            
            if not contract:
                return {'success': False, 'error': f'Contract {contract_id} not found'}
            
            # Create payment record
            payment_data = {
                'ejar_payment_id': payment_id,
                'contract_id': contract.id,
                'amount': data.get('amount', 0),
                'payment_date': data.get('payment_date', fields.Date.today()),
                'payment_method': data.get('payment_method', 'bank_transfer'),
                'status': 'received',
                'reference': data.get('reference'),
                'notes': data.get('notes'),
            }
            
            payment = request.env['ejar.payment'].sudo().create(payment_data)
            
            return {'success': True, 'message': f'Payment {payment_id} recorded with ID {payment.id}'}
                
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def _handle_payment_failed(self, data):
        """Handle payment failed webhook"""
        try:
            payment_id = data.get('payment_id')
            
            if not payment_id:
                return {'success': False, 'error': 'Missing payment_id in webhook data'}
            
            # Find existing payment
            payment = request.env['ejar.payment'].sudo().search([
                ('ejar_payment_id', '=', payment_id)
            ], limit=1)
            
            if payment:
                # Update payment status
                payment.write({
                    'status': 'failed',
                    'failure_reason': data.get('failure_reason'),
                    'notes': data.get('notes'),
                })
            
            return {'success': True, 'message': f'Payment {payment_id} marked as failed'}
                
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def _handle_compliance_violation(self, data):
        """Handle compliance violation webhook"""
        try:
            violation_id = data.get('violation_id')
            rule_code = data.get('rule_code')
            
            if not violation_id or not rule_code:
                return {'success': False, 'error': 'Missing violation_id or rule_code in webhook data'}
            
            # Find compliance rule
            rule = request.env['ejar.compliance.rule'].sudo().search([
                ('ejar_rule_code', '=', rule_code)
            ], limit=1)
            
            if not rule:
                return {'success': False, 'error': f'Compliance rule {rule_code} not found'}
            
            # Create compliance violation record
            violation_data = {
                'ejar_violation_id': violation_id,
                'compliance_type': rule.compliance_type,
                'rule_id': rule.id,
                'status': 'violation',
                'severity': data.get('severity', rule.severity),
                'violation_date': data.get('violation_date', fields.Datetime.now()),
                'description': data.get('description'),
                'related_model': data.get('related_model'),
                'related_id': data.get('related_id'),
            }
            
            violation = request.env['ejar.compliance'].sudo().create(violation_data)
            
            return {'success': True, 'message': f'Compliance violation {violation_id} recorded with ID {violation.id}'}
                
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def _handle_document_uploaded(self, data):
        """Handle document uploaded webhook"""
        try:
            document_id = data.get('document_id')
            
            if not document_id:
                return {'success': False, 'error': 'Missing document_id in webhook data'}
            
            # Create document record
            document_data = {
                'ejar_document_id': document_id,
                'name': data.get('name', 'Ejar Document'),
                'document_type': data.get('document_type'),
                'related_model': data.get('related_model'),
                'related_id': data.get('related_id'),
                'file_url': data.get('file_url'),
                'file_size': data.get('file_size'),
                'mime_type': data.get('mime_type'),
                'upload_date': data.get('upload_date', fields.Datetime.now()),
                'status': 'uploaded',
            }
            
            document = request.env['ejar.document'].sudo().create(document_data)
            
            return {'success': True, 'message': f'Document {document_id} recorded with ID {document.id}'}
                
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def _handle_notification_sent(self, data):
        """Handle notification sent webhook"""
        try:
            notification_id = data.get('notification_id')
            
            if not notification_id:
                return {'success': False, 'error': 'Missing notification_id in webhook data'}
            
            # Find existing notification
            notification = request.env['ejar.notification'].sudo().search([
                ('ejar_notification_id', '=', notification_id)
            ], limit=1)
            
            if notification:
                # Update notification status
                notification.write({
                    'ejar_status': 'sent',
                    'sent_date': data.get('sent_date', fields.Datetime.now()),
                    'delivery_status': data.get('delivery_status', 'delivered'),
                })
            
            return {'success': True, 'message': f'Notification {notification_id} status updated'}
                
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    # Helper methods for preparing data from webhook
    
    def _prepare_contract_data_from_webhook(self, data):
        """Prepare contract data from webhook payload"""
        try:
            # This would need to be implemented based on actual Ejar webhook structure
            return {
                'ejar_contract_id': data.get('contract_id'),
                'contract_number': data.get('contract_number'),
                'status': data.get('status', 'active'),
                'start_date': data.get('start_date'),
                'end_date': data.get('end_date'),
                'monthly_rent': data.get('monthly_rent', 0),
                'security_deposit': data.get('security_deposit', 0),
                'ejar_sync_status': 'synced',
                'last_ejar_sync': fields.Datetime.now(),
            }
        except Exception as e:
            _logger.error(f"Error preparing contract data from webhook: {e}")
            return None
    
    def _prepare_contract_update_data_from_webhook(self, data):
        """Prepare contract update data from webhook payload"""
        try:
            update_data = {
                'ejar_sync_status': 'synced',
                'last_ejar_sync': fields.Datetime.now(),
            }
            
            # Add fields that might be updated
            if 'status' in data:
                update_data['status'] = data['status']
            if 'monthly_rent' in data:
                update_data['monthly_rent'] = data['monthly_rent']
            if 'end_date' in data:
                update_data['end_date'] = data['end_date']
            
            return update_data
        except Exception as e:
            _logger.error(f"Error preparing contract update data from webhook: {e}")
            return None
    
    def _prepare_property_update_data_from_webhook(self, data):
        """Prepare property update data from webhook payload"""
        try:
            update_data = {
                'ejar_sync_status': 'synced',
                'last_ejar_sync': fields.Datetime.now(),
            }
            
            # Add fields that might be updated
            if 'status' in data:
                update_data['status'] = data['status']
            if 'monthly_rent' in data:
                update_data['monthly_rent'] = data['monthly_rent']
            if 'description' in data:
                update_data['description'] = data['description']
            
            return update_data
        except Exception as e:
            _logger.error(f"Error preparing property update data from webhook: {e}")
            return None
    
    def _prepare_tenant_update_data_from_webhook(self, data):
        """Prepare tenant update data from webhook payload"""
        try:
            update_data = {
                'ejar_sync_status': 'synced',
                'last_ejar_sync': fields.Datetime.now(),
            }
            
            # Add fields that might be updated
            if 'phone' in data:
                update_data['phone'] = data['phone']
            if 'email' in data:
                update_data['email'] = data['email']
            if 'address' in data:
                update_data['address'] = data['address']
            
            return update_data
        except Exception as e:
            _logger.error(f"Error preparing tenant update data from webhook: {e}")
            return None
    
    def _prepare_landlord_update_data_from_webhook(self, data):
        """Prepare landlord update data from webhook payload"""
        try:
            update_data = {
                'ejar_sync_status': 'synced',
                'last_ejar_sync': fields.Datetime.now(),
            }
            
            # Add fields that might be updated
            if 'phone' in data:
                update_data['phone'] = data['phone']
            if 'email' in data:
                update_data['email'] = data['email']
            if 'address' in data:
                update_data['address'] = data['address']
            
            return update_data
        except Exception as e:
            _logger.error(f"Error preparing landlord update data from webhook: {e}")
            return None