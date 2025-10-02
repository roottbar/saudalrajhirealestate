# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError, UserError
import requests
import json
import logging

_logger = logging.getLogger(__name__)


class EjarConfig(models.Model):
    """Configuration settings for Ejar platform integration"""
    _name = 'ejar.config'
    _description = 'Ejar Platform Configuration'
    _rec_name = 'name'

    name = fields.Char(string='Configuration Name', required=True, default='Ejar Integration')
    
    # API Configuration
    api_base_url = fields.Char(
        string='API Base URL',
        required=True,
        default='https://api.ejar.sa/v1/',
        help='Base URL for Ejar API endpoints'
    )
    api_key = fields.Char(string='API Key', required=True, help='API key provided by Ejar platform')
    api_secret = fields.Char(string='API Secret', required=True, help='API secret for authentication')
    client_id = fields.Char(string='Client ID', required=True, help='Client ID for OAuth authentication')
    client_secret = fields.Char(string='Client Secret', required=True, help='Client Secret for OAuth')
    
    # Authentication
    access_token = fields.Text(string='Access Token', readonly=True, help='Current access token')
    refresh_token = fields.Text(string='Refresh Token', readonly=True, help='Refresh token for renewing access')
    token_expires_at = fields.Datetime(string='Token Expires At', readonly=True)
    
    # Environment Settings
    environment = fields.Selection([
        ('sandbox', 'Sandbox'),
        ('production', 'Production')
    ], string='Environment', default='sandbox', required=True)
    
    # Sync Settings
    auto_sync_enabled = fields.Boolean(string='Enable Auto Sync', default=True)
    sync_interval = fields.Integer(string='Sync Interval (minutes)', default=60)
    last_sync_date = fields.Datetime(string='Last Sync Date', readonly=True)
    
    # Notification Settings
    enable_notifications = fields.Boolean(string='Enable Notifications', default=True)
    notification_email = fields.Char(string='Notification Email')
    webhook_url = fields.Char(string='Webhook URL', help='URL for receiving Ejar webhooks')
    
    # Company Information
    company_id = fields.Many2one('res.company', string='Company', required=True, default=lambda self: self.env.company)
    broker_license_number = fields.Char(string='Broker License Number', required=True)
    commercial_registration = fields.Char(string='Commercial Registration Number', required=True)
    
    # Status
    is_active = fields.Boolean(string='Active', default=True)
    connection_status = fields.Selection([
        ('not_connected', 'Not Connected'),
        ('connected', 'Connected'),
        ('error', 'Connection Error')
    ], string='Connection Status', default='not_connected', readonly=True)
    last_error_message = fields.Text(string='Last Error Message', readonly=True)
    
    # Compliance Settings
    auto_register_contracts = fields.Boolean(string='Auto Register Contracts', default=True)
    require_ejar_approval = fields.Boolean(string='Require Ejar Approval', default=True)
    validate_tenant_data = fields.Boolean(string='Validate Tenant Data', default=True)
    
    @api.model
    def get_active_config(self):
        """Get the active Ejar configuration"""
        config = self.search([('is_active', '=', True)], limit=1)
        if not config:
            raise UserError(_('No active Ejar configuration found. Please configure the Ejar integration first.'))
        return config
    
    def test_connection(self):
        """Test connection to Ejar API"""
        try:
            self._authenticate()
            self.connection_status = 'connected'
            self.last_error_message = False
            return {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'title': _('Success'),
                    'message': _('Connection to Ejar platform successful!'),
                    'type': 'success',
                }
            }
        except Exception as e:
            self.connection_status = 'error'
            self.last_error_message = str(e)
            _logger.error(f"Ejar connection test failed: {e}")
            return {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'title': _('Connection Failed'),
                    'message': str(e),
                    'type': 'danger',
                }
            }
    
    def _authenticate(self):
        """Authenticate with Ejar API and get access token"""
        auth_url = f"{self.api_base_url}auth/token"
        
        payload = {
            'client_id': self.client_id,
            'client_secret': self.client_secret,
            'grant_type': 'client_credentials'
        }
        
        headers = {
            'Content-Type': 'application/json',
            'X-API-Key': self.api_key
        }
        
        try:
            response = requests.post(auth_url, json=payload, headers=headers, timeout=30)
            response.raise_for_status()
            
            token_data = response.json()
            self.access_token = token_data.get('access_token')
            self.refresh_token = token_data.get('refresh_token')
            
            # Calculate token expiry
            expires_in = token_data.get('expires_in', 3600)  # Default 1 hour
            self.token_expires_at = fields.Datetime.now() + fields.Datetime.timedelta(seconds=expires_in)
            
            return True
            
        except requests.exceptions.RequestException as e:
            raise UserError(_('Failed to authenticate with Ejar API: %s') % str(e))
        except Exception as e:
            raise UserError(_('Authentication error: %s') % str(e))
    
    def refresh_access_token(self):
        """Refresh the access token using refresh token"""
        if not self.refresh_token:
            return self._authenticate()
        
        refresh_url = f"{self.api_base_url}auth/refresh"
        
        payload = {
            'refresh_token': self.refresh_token,
            'grant_type': 'refresh_token'
        }
        
        headers = {
            'Content-Type': 'application/json',
            'X-API-Key': self.api_key
        }
        
        try:
            response = requests.post(refresh_url, json=payload, headers=headers, timeout=30)
            response.raise_for_status()
            
            token_data = response.json()
            self.access_token = token_data.get('access_token')
            
            # Update expiry time
            expires_in = token_data.get('expires_in', 3600)
            self.token_expires_at = fields.Datetime.now() + fields.Datetime.timedelta(seconds=expires_in)
            
            return True
            
        except Exception as e:
            _logger.error(f"Failed to refresh token: {e}")
            # Fall back to full authentication
            return self._authenticate()
    
    def get_valid_token(self):
        """Get a valid access token, refreshing if necessary"""
        if not self.access_token or (self.token_expires_at and fields.Datetime.now() >= self.token_expires_at):
            self.refresh_access_token()
        return self.access_token
    
    @api.constrains('api_base_url')
    def _check_api_url(self):
        """Validate API URL format"""
        for record in self:
            if record.api_base_url and not record.api_base_url.startswith(('http://', 'https://')):
                raise ValidationError(_('API Base URL must start with http:// or https://'))
    
    @api.constrains('sync_interval')
    def _check_sync_interval(self):
        """Validate sync interval"""
        for record in self:
            if record.sync_interval < 1:
                raise ValidationError(_('Sync interval must be at least 1 minute'))
    
    def sync_with_ejar(self):
        """Manual sync with Ejar platform"""
        try:
            # Update last sync date
            self.last_sync_date = fields.Datetime.now()
            
            # Trigger sync for all related models
            self.env['ejar.contract'].sync_all_contracts()
            
            return {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'title': _('Sync Complete'),
                    'message': _('Synchronization with Ejar platform completed successfully!'),
                    'type': 'success',
                }
            }
        except Exception as e:
            _logger.error(f"Ejar sync failed: {e}")
            return {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'title': _('Sync Failed'),
                    'message': str(e),
                    'type': 'danger',
                }
            }


class EjarContractType(models.Model):
    """Ejar contract types configuration"""
    _name = 'ejar.contract.type'
    _description = 'Ejar Contract Types'
    _order = 'sequence, name'

    name = fields.Char(string='Name', required=True, translate=True)
    code = fields.Char(string='Code', required=True)
    sequence = fields.Integer(string='Sequence', default=10)
    description = fields.Text(string='Description', translate=True)
    is_active = fields.Boolean(string='Active', default=True)
    
    # Contract specifications
    min_duration_months = fields.Integer(string='Minimum Duration (Months)', default=12)
    max_duration_months = fields.Integer(string='Maximum Duration (Months)', default=60)
    requires_deposit = fields.Boolean(string='Requires Deposit', default=True)
    deposit_percentage = fields.Float(string='Deposit Percentage (%)', default=10.0)
    
    @api.constrains('code')
    def _check_unique_code(self):
        """Ensure contract type codes are unique"""
        for record in self:
            if self.search_count([('code', '=', record.code), ('id', '!=', record.id)]) > 0:
                raise ValidationError(_('Contract type code must be unique'))


class EjarPropertyType(models.Model):
    """Ejar property types configuration"""
    _name = 'ejar.property.type'
    _description = 'Ejar Property Types'
    _order = 'sequence, name'

    name = fields.Char(string='Name', required=True, translate=True)
    code = fields.Char(string='Code', required=True)
    sequence = fields.Integer(string='Sequence', default=10)
    description = fields.Text(string='Description', translate=True)
    is_active = fields.Boolean(string='Active', default=True)
    
    # Property specifications
    category = fields.Selection([
        ('residential', 'Residential'),
        ('commercial', 'Commercial'),
        ('industrial', 'Industrial'),
        ('mixed', 'Mixed Use')
    ], string='Category', required=True, default='residential')
    
    @api.constrains('code')
    def _check_unique_code(self):
        """Ensure property type codes are unique"""
        for record in self:
            if self.search_count([('code', '=', record.code), ('id', '!=', record.id)]) > 0:
                raise ValidationError(_('Property type code must be unique'))