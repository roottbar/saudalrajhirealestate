# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError, UserError
import requests
import json
import jwt
import base64
from datetime import datetime, timedelta
import logging
import hashlib
import hmac

_logger = logging.getLogger(__name__)


class EjarApiConnector(models.Model):
    """Ejar platform API connector"""
    _name = 'ejar.api.connector'
    _description = 'Ejar API Connector'
    _rec_name = 'name'

    name = fields.Char(string='Connector Name', required=True, default='Ejar API Connector')
    
    # API Configuration
    base_url = fields.Char(string='Base URL', required=True, 
                          default='https://api.ejar.sa/v1')
    api_key = fields.Char(string='API Key', required=True)
    api_secret = fields.Char(string='API Secret', required=True)
    client_id = fields.Char(string='Client ID')
    client_secret = fields.Char(string='Client Secret')
    
    # Authentication
    access_token = fields.Text(string='Access Token')
    refresh_token = fields.Text(string='Refresh Token')
    token_expires_at = fields.Datetime(string='Token Expires At')
    
    # Connection Status
    connection_status = fields.Selection([
        ('disconnected', 'Disconnected'),
        ('connected', 'Connected'),
        ('error', 'Error'),
        ('expired', 'Token Expired')
    ], string='Connection Status', default='disconnected', readonly=True)
    
    last_connection_test = fields.Datetime(string='Last Connection Test')
    connection_error = fields.Text(string='Connection Error')
    
    # Request Configuration
    timeout = fields.Integer(string='Request Timeout (seconds)', default=30)
    max_retries = fields.Integer(string='Max Retries', default=3)
    retry_delay = fields.Integer(string='Retry Delay (seconds)', default=5)
    
    # Rate Limiting
    rate_limit_enabled = fields.Boolean(string='Rate Limit Enabled', default=True)
    requests_per_minute = fields.Integer(string='Requests Per Minute', default=60)
    requests_per_hour = fields.Integer(string='Requests Per Hour', default=1000)
    
    # Logging
    log_requests = fields.Boolean(string='Log Requests', default=True)
    log_responses = fields.Boolean(string='Log Responses', default=False)
    
    # Environment
    environment = fields.Selection([
        ('sandbox', 'Sandbox'),
        ('production', 'Production')
    ], string='Environment', default='sandbox', required=True)
    
    # Company
    company_id = fields.Many2one('res.company', string='Company', 
                                 default=lambda self: self.env.company)
    
    # Active
    active = fields.Boolean(string='Active', default=True)
    
    @api.constrains('base_url')
    def _check_base_url(self):
        """Validate base URL format"""
        for record in self:
            if record.base_url and not record.base_url.startswith(('http://', 'https://')):
                raise ValidationError(_('Base URL must start with http:// or https://'))
    
    @api.model
    def get_active_connector(self):
        """Get active API connector"""
        connector = self.search([
            ('active', '=', True),
            ('company_id', '=', self.env.company.id)
        ], limit=1)
        
        if not connector:
            raise UserError(_('No active Ejar API connector found. Please configure the API connection.'))
        
        return connector
    
    def test_connection(self):
        """Test API connection"""
        self.ensure_one()
        
        try:
            # Test authentication
            self._authenticate()
            
            # Test a simple API call
            response = self._make_request('GET', '/health')
            
            if response.get('status') == 'ok':
                self.write({
                    'connection_status': 'connected',
                    'last_connection_test': fields.Datetime.now(),
                    'connection_error': False,
                })
                
                return {
                    'type': 'ir.actions.client',
                    'tag': 'display_notification',
                    'params': {
                        'title': _('Connection Successful'),
                        'message': _('Successfully connected to Ejar API'),
                        'type': 'success',
                    }
                }
            else:
                raise Exception('Health check failed')
                
        except Exception as e:
            error_msg = str(e)
            self.write({
                'connection_status': 'error',
                'last_connection_test': fields.Datetime.now(),
                'connection_error': error_msg,
            })
            
            raise UserError(_('Connection failed: %s') % error_msg)
    
    def _authenticate(self):
        """Authenticate with Ejar API"""
        if self._is_token_valid():
            return self.access_token
        
        try:
            # Prepare authentication request
            auth_url = f"{self.base_url}/auth/token"
            
            headers = {
                'Content-Type': 'application/json',
                'Accept': 'application/json',
            }
            
            data = {
                'client_id': self.client_id,
                'client_secret': self.client_secret,
                'api_key': self.api_key,
                'grant_type': 'client_credentials'
            }
            
            # Add API signature if required
            if self.api_secret:
                signature = self._generate_signature(data)
                headers['X-API-Signature'] = signature
            
            response = requests.post(
                auth_url,
                headers=headers,
                json=data,
                timeout=self.timeout
            )
            
            if response.status_code == 200:
                token_data = response.json()
                
                # Calculate token expiry
                expires_in = token_data.get('expires_in', 3600)  # Default 1 hour
                expires_at = datetime.now() + timedelta(seconds=expires_in)
                
                # Store tokens
                self.write({
                    'access_token': token_data.get('access_token'),
                    'refresh_token': token_data.get('refresh_token'),
                    'token_expires_at': expires_at,
                    'connection_status': 'connected',
                })
                
                return self.access_token
            else:
                error_msg = f"Authentication failed: {response.status_code} - {response.text}"
                _logger.error(error_msg)
                raise Exception(error_msg)
                
        except requests.exceptions.RequestException as e:
            error_msg = f"Authentication request failed: {str(e)}"
            _logger.error(error_msg)
            raise Exception(error_msg)
    
    def _is_token_valid(self):
        """Check if current token is valid"""
        if not self.access_token or not self.token_expires_at:
            return False
        
        # Add 5 minute buffer before expiry
        buffer_time = timedelta(minutes=5)
        return datetime.now() + buffer_time < self.token_expires_at
    
    def _refresh_access_token(self):
        """Refresh access token using refresh token"""
        if not self.refresh_token:
            return self._authenticate()
        
        try:
            refresh_url = f"{self.base_url}/auth/refresh"
            
            headers = {
                'Content-Type': 'application/json',
                'Accept': 'application/json',
                'Authorization': f'Bearer {self.refresh_token}'
            }
            
            data = {
                'refresh_token': self.refresh_token,
                'grant_type': 'refresh_token'
            }
            
            response = requests.post(
                refresh_url,
                headers=headers,
                json=data,
                timeout=self.timeout
            )
            
            if response.status_code == 200:
                token_data = response.json()
                
                expires_in = token_data.get('expires_in', 3600)
                expires_at = datetime.now() + timedelta(seconds=expires_in)
                
                self.write({
                    'access_token': token_data.get('access_token'),
                    'refresh_token': token_data.get('refresh_token', self.refresh_token),
                    'token_expires_at': expires_at,
                })
                
                return self.access_token
            else:
                # Refresh failed, re-authenticate
                return self._authenticate()
                
        except Exception as e:
            _logger.warning(f"Token refresh failed: {e}")
            return self._authenticate()
    
    def _generate_signature(self, data):
        """Generate API signature for request authentication"""
        if not self.api_secret:
            return None
        
        # Create signature string
        if isinstance(data, dict):
            signature_string = json.dumps(data, sort_keys=True, separators=(',', ':'))
        else:
            signature_string = str(data)
        
        # Generate HMAC signature
        signature = hmac.new(
            self.api_secret.encode('utf-8'),
            signature_string.encode('utf-8'),
            hashlib.sha256
        ).hexdigest()
        
        return signature
    
    def _make_request(self, method, endpoint, data=None, params=None, headers=None):
        """Make API request to Ejar platform"""
        # Ensure authentication
        if not self._is_token_valid():
            self._authenticate()
        
        # Prepare URL
        url = f"{self.base_url.rstrip('/')}/{endpoint.lstrip('/')}"
        
        # Prepare headers
        request_headers = {
            'Content-Type': 'application/json',
            'Accept': 'application/json',
            'Authorization': f'Bearer {self.access_token}',
            'X-API-Key': self.api_key,
        }
        
        if headers:
            request_headers.update(headers)
        
        # Add signature if data is provided
        if data and self.api_secret:
            signature = self._generate_signature(data)
            request_headers['X-API-Signature'] = signature
        
        # Log request if enabled
        if self.log_requests:
            _logger.info(f"Ejar API Request: {method} {url}")
            if data:
                _logger.debug(f"Request Data: {json.dumps(data, indent=2)}")
        
        # Make request with retries
        last_exception = None
        for attempt in range(self.max_retries + 1):
            try:
                response = requests.request(
                    method=method,
                    url=url,
                    json=data,
                    params=params,
                    headers=request_headers,
                    timeout=self.timeout
                )
                
                # Log response if enabled
                if self.log_responses:
                    _logger.info(f"Ejar API Response: {response.status_code}")
                    _logger.debug(f"Response Data: {response.text}")
                
                # Handle response
                if response.status_code == 401:
                    # Token expired, refresh and retry
                    if attempt < self.max_retries:
                        self._refresh_access_token()
                        request_headers['Authorization'] = f'Bearer {self.access_token}'
                        continue
                    else:
                        raise Exception('Authentication failed after retries')
                
                elif response.status_code in [200, 201, 202]:
                    # Success
                    try:
                        return response.json()
                    except json.JSONDecodeError:
                        return {'status': 'success', 'data': response.text}
                
                elif response.status_code in [429, 500, 502, 503, 504]:
                    # Rate limit or server error, retry
                    if attempt < self.max_retries:
                        import time
                        time.sleep(self.retry_delay * (attempt + 1))
                        continue
                    else:
                        raise Exception(f'Server error: {response.status_code} - {response.text}')
                
                else:
                    # Client error, don't retry
                    error_msg = f'API error: {response.status_code} - {response.text}'
                    raise Exception(error_msg)
                
            except requests.exceptions.RequestException as e:
                last_exception = e
                if attempt < self.max_retries:
                    import time
                    time.sleep(self.retry_delay * (attempt + 1))
                    continue
                else:
                    raise Exception(f'Request failed: {str(e)}')
        
        # If we get here, all retries failed
        if last_exception:
            raise Exception(f'Request failed after {self.max_retries} retries: {str(last_exception)}')
    
    # Property Management APIs
    def register_property(self, property_data):
        """Register property with Ejar"""
        return self._make_request('POST', '/properties', data=property_data)
    
    def update_property(self, ejar_property_id, property_data):
        """Update property in Ejar"""
        return self._make_request('PUT', f'/properties/{ejar_property_id}', data=property_data)
    
    def get_property(self, ejar_property_id):
        """Get property from Ejar"""
        return self._make_request('GET', f'/properties/{ejar_property_id}')
    
    def get_property_status(self, ejar_property_id):
        """Get property status from Ejar"""
        return self._make_request('GET', f'/properties/{ejar_property_id}/status')
    
    # Contract Management APIs
    def submit_contract(self, contract_data):
        """Submit contract to Ejar"""
        return self._make_request('POST', '/contracts', data=contract_data)
    
    def update_contract(self, ejar_contract_id, contract_data):
        """Update contract in Ejar"""
        return self._make_request('PUT', f'/contracts/{ejar_contract_id}', data=contract_data)
    
    def get_contract(self, ejar_contract_id):
        """Get contract from Ejar"""
        return self._make_request('GET', f'/contracts/{ejar_contract_id}')
    
    def get_contract_status(self, ejar_contract_id):
        """Get contract status from Ejar"""
        return self._make_request('GET', f'/contracts/{ejar_contract_id}/status')
    
    def activate_contract(self, ejar_contract_id):
        """Activate contract in Ejar"""
        return self._make_request('POST', f'/contracts/{ejar_contract_id}/activate')
    
    def terminate_contract(self, ejar_contract_id, termination_data):
        """Terminate contract in Ejar"""
        return self._make_request('POST', f'/contracts/{ejar_contract_id}/terminate', data=termination_data)
    
    # Tenant Management APIs
    def register_tenant(self, tenant_data):
        """Register tenant with Ejar"""
        return self._make_request('POST', '/tenants', data=tenant_data)
    
    def update_tenant(self, ejar_tenant_id, tenant_data):
        """Update tenant in Ejar"""
        return self._make_request('PUT', f'/tenants/{ejar_tenant_id}', data=tenant_data)
    
    def get_tenant(self, ejar_tenant_id):
        """Get tenant from Ejar"""
        return self._make_request('GET', f'/tenants/{ejar_tenant_id}')
    
    def verify_tenant(self, ejar_tenant_id):
        """Verify tenant in Ejar"""
        return self._make_request('POST', f'/tenants/{ejar_tenant_id}/verify')
    
    # Landlord Management APIs
    def register_landlord(self, landlord_data):
        """Register landlord with Ejar"""
        return self._make_request('POST', '/landlords', data=landlord_data)
    
    def update_landlord(self, ejar_landlord_id, landlord_data):
        """Update landlord in Ejar"""
        return self._make_request('PUT', f'/landlords/{ejar_landlord_id}', data=landlord_data)
    
    def get_landlord(self, ejar_landlord_id):
        """Get landlord from Ejar"""
        return self._make_request('GET', f'/landlords/{ejar_landlord_id}')
    
    def verify_landlord(self, ejar_landlord_id):
        """Verify landlord in Ejar"""
        return self._make_request('POST', f'/landlords/{ejar_landlord_id}/verify')
    
    # Broker Management APIs
    def register_broker(self, broker_data):
        """Register broker with Ejar"""
        return self._make_request('POST', '/brokers', data=broker_data)
    
    def update_broker(self, ejar_broker_id, broker_data):
        """Update broker in Ejar"""
        return self._make_request('PUT', f'/brokers/{ejar_broker_id}', data=broker_data)
    
    def get_broker(self, ejar_broker_id):
        """Get broker from Ejar"""
        return self._make_request('GET', f'/brokers/{ejar_broker_id}')
    
    def verify_broker(self, ejar_broker_id):
        """Verify broker in Ejar"""
        return self._make_request('POST', f'/brokers/{ejar_broker_id}/verify')
    
    # Payment APIs
    def submit_payment(self, payment_data):
        """Submit payment to Ejar"""
        return self._make_request('POST', '/payments', data=payment_data)
    
    def get_payment_status(self, payment_id):
        """Get payment status from Ejar"""
        return self._make_request('GET', f'/payments/{payment_id}/status')
    
    # Document APIs
    def upload_document(self, document_data, file_content):
        """Upload document to Ejar"""
        # For file uploads, we need to use multipart/form-data
        files = {'file': file_content}
        
        # Make request without JSON content type for file upload
        url = f"{self.base_url.rstrip('/')}/documents"
        
        headers = {
            'Authorization': f'Bearer {self.access_token}',
            'X-API-Key': self.api_key,
        }
        
        response = requests.post(
            url,
            headers=headers,
            data=document_data,
            files=files,
            timeout=self.timeout
        )
        
        if response.status_code in [200, 201]:
            return response.json()
        else:
            raise Exception(f'Document upload failed: {response.status_code} - {response.text}')
    
    def get_document(self, document_id):
        """Get document from Ejar"""
        return self._make_request('GET', f'/documents/{document_id}')
    
    # Notification APIs
    def send_notification(self, notification_data):
        """Send notification via Ejar"""
        return self._make_request('POST', '/notifications', data=notification_data)
    
    def get_notifications(self, params=None):
        """Get notifications from Ejar"""
        return self._make_request('GET', '/notifications', params=params)
    
    # Webhook APIs
    def register_webhook(self, webhook_data):
        """Register webhook with Ejar"""
        return self._make_request('POST', '/webhooks', data=webhook_data)
    
    def update_webhook(self, webhook_id, webhook_data):
        """Update webhook in Ejar"""
        return self._make_request('PUT', f'/webhooks/{webhook_id}', data=webhook_data)
    
    def delete_webhook(self, webhook_id):
        """Delete webhook from Ejar"""
        return self._make_request('DELETE', f'/webhooks/{webhook_id}')
    
    # Utility APIs
    def get_cities(self):
        """Get list of cities from Ejar"""
        return self._make_request('GET', '/utilities/cities')
    
    def get_districts(self, city_id):
        """Get list of districts for a city from Ejar"""
        return self._make_request('GET', f'/utilities/cities/{city_id}/districts')
    
    def get_property_types(self):
        """Get list of property types from Ejar"""
        return self._make_request('GET', '/utilities/property-types')
    
    def get_contract_types(self):
        """Get list of contract types from Ejar"""
        return self._make_request('GET', '/utilities/contract-types')
    
    # Rate Limiting
    def _check_rate_limit(self):
        """Check if request is within rate limits"""
        if not self.rate_limit_enabled:
            return True
        
        # Implementation would depend on how you want to track rate limits
        # This is a simplified version
        return True
    
    @api.model
    def _cron_refresh_tokens(self):
        """Cron job to refresh expiring tokens"""
        # Find connectors with tokens expiring in the next hour
        expiring_soon = datetime.now() + timedelta(hours=1)
        
        connectors = self.search([
            ('active', '=', True),
            ('token_expires_at', '<=', expiring_soon),
            ('token_expires_at', '>', datetime.now())
        ])
        
        for connector in connectors:
            try:
                connector._refresh_access_token()
                _logger.info(f"Refreshed token for connector {connector.name}")
            except Exception as e:
                _logger.error(f"Failed to refresh token for connector {connector.name}: {e}")
                connector.write({
                    'connection_status': 'expired',
                    'connection_error': str(e)
                })
    
    def action_clear_tokens(self):
        """Clear stored tokens"""
        self.ensure_one()
        
        self.write({
            'access_token': False,
            'refresh_token': False,
            'token_expires_at': False,
            'connection_status': 'disconnected',
        })
        
        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': _('Tokens Cleared'),
                'message': _('API tokens have been cleared'),
                'type': 'success',
            }
        }