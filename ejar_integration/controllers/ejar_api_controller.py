# -*- coding: utf-8 -*-

import json
import logging
from datetime import datetime, timedelta

from odoo import http, fields, _
from odoo.http import request, Response
from odoo.exceptions import ValidationError, UserError, AccessError

_logger = logging.getLogger(__name__)


class EjarAPIController(http.Controller):
    """Controller for Ejar API endpoints"""

    def _authenticate_api_request(self, api_key=None):
        """Authenticate API request"""
        if not api_key:
            api_key = request.httprequest.headers.get('X-API-Key')
        
        if not api_key:
            return {'error': 'API key is required', 'code': 401}
        
        # Find connector with matching API key
        connector = request.env['ejar.api.connector'].sudo().search([
            ('api_key', '=', api_key),
            ('status', '=', 'active')
        ], limit=1)
        
        if not connector:
            return {'error': 'Invalid API key', 'code': 401}
        
        return {'connector': connector}
    
    def _validate_json_data(self, required_fields=None):
        """Validate JSON data from request"""
        try:
            data = json.loads(request.httprequest.data.decode('utf-8'))
        except (ValueError, UnicodeDecodeError):
            return {'error': 'Invalid JSON data', 'code': 400}
        
        if required_fields:
            missing_fields = [field for field in required_fields if field not in data]
            if missing_fields:
                return {'error': f'Missing required fields: {", ".join(missing_fields)}', 'code': 400}
        
        return {'data': data}
    
    def _create_response(self, data=None, error=None, code=200):
        """Create standardized API response"""
        response_data = {
            'success': error is None,
            'timestamp': datetime.now().isoformat(),
        }
        
        if error:
            response_data['error'] = error
        else:
            response_data['data'] = data or {}
        
        return Response(
            json.dumps(response_data, default=str),
            content_type='application/json',
            status=code
        )

    # Property Management Endpoints
    
    @http.route('/api/ejar/properties', type='http', auth='none', methods=['GET'], csrf=False)
    def get_properties(self, **kwargs):
        """Get list of properties"""
        auth_result = self._authenticate_api_request()
        if 'error' in auth_result:
            return self._create_response(error=auth_result['error'], code=auth_result['code'])
        
        try:
            # Parse query parameters
            limit = int(kwargs.get('limit', 50))
            offset = int(kwargs.get('offset', 0))
            status = kwargs.get('status')
            property_type = kwargs.get('type')
            
            # Build domain
            domain = []
            if status:
                domain.append(('status', '=', status))
            if property_type:
                domain.append(('property_type', '=', property_type))
            
            # Search properties
            properties = request.env['ejar.property'].sudo().search(
                domain, limit=limit, offset=offset, order='create_date desc'
            )
            
            # Prepare response data
            properties_data = []
            for prop in properties:
                properties_data.append({
                    'id': prop.id,
                    'ejar_id': prop.ejar_property_id,
                    'name': prop.name,
                    'type': prop.property_type,
                    'subtype': prop.property_subtype,
                    'status': prop.status,
                    'area': prop.area,
                    'bedrooms': prop.bedrooms,
                    'bathrooms': prop.bathrooms,
                    'monthly_rent': prop.monthly_rent,
                    'address': prop.address,
                    'city': prop.city,
                    'district': prop.district,
                    'landlord_id': prop.landlord_id.ejar_landlord_id if prop.landlord_id else None,
                    'created_date': prop.create_date.isoformat() if prop.create_date else None,
                })
            
            return self._create_response({
                'properties': properties_data,
                'total': len(properties_data),
                'limit': limit,
                'offset': offset
            })
            
        except Exception as e:
            _logger.error(f"Error getting properties: {e}")
            return self._create_response(error=str(e), code=500)
    
    @http.route('/api/ejar/properties/<int:property_id>', type='http', auth='none', methods=['GET'], csrf=False)
    def get_property(self, property_id, **kwargs):
        """Get specific property details"""
        auth_result = self._authenticate_api_request()
        if 'error' in auth_result:
            return self._create_response(error=auth_result['error'], code=auth_result['code'])
        
        try:
            property_rec = request.env['ejar.property'].sudo().browse(property_id)
            if not property_rec.exists():
                return self._create_response(error='Property not found', code=404)
            
            # Prepare detailed property data
            property_data = {
                'id': property_rec.id,
                'ejar_id': property_rec.ejar_property_id,
                'name': property_rec.name,
                'description': property_rec.description,
                'type': property_rec.property_type,
                'subtype': property_rec.property_subtype,
                'status': property_rec.status,
                'area': property_rec.area,
                'built_area': property_rec.built_area,
                'bedrooms': property_rec.bedrooms,
                'bathrooms': property_rec.bathrooms,
                'parking_spaces': property_rec.parking_spaces,
                'floor_number': property_rec.floor_number,
                'total_floors': property_rec.total_floors,
                'monthly_rent': property_rec.monthly_rent,
                'security_deposit': property_rec.security_deposit,
                'broker_commission_rate': property_rec.broker_commission_rate,
                'address': property_rec.address,
                'city': property_rec.city,
                'district': property_rec.district,
                'neighborhood': property_rec.neighborhood,
                'latitude': property_rec.latitude,
                'longitude': property_rec.longitude,
                'furnishing_status': property_rec.furnishing_status,
                'property_condition': property_rec.property_condition,
                'construction_year': property_rec.construction_year,
                'features': {
                    'has_balcony': property_rec.has_balcony,
                    'has_garden': property_rec.has_garden,
                    'has_pool': property_rec.has_pool,
                    'has_gym': property_rec.has_gym,
                    'has_elevator': property_rec.has_elevator,
                    'has_security': property_rec.has_security,
                    'has_parking': property_rec.has_parking,
                    'has_storage': property_rec.has_storage,
                    'has_maid_room': property_rec.has_maid_room,
                    'has_laundry': property_rec.has_laundry,
                },
                'utilities': {
                    'electricity_included': property_rec.electricity_included,
                    'water_included': property_rec.water_included,
                    'internet_included': property_rec.internet_included,
                    'maintenance_included': property_rec.maintenance_included,
                },
                'landlord': {
                    'id': property_rec.landlord_id.id if property_rec.landlord_id else None,
                    'ejar_id': property_rec.landlord_id.ejar_landlord_id if property_rec.landlord_id else None,
                    'name': property_rec.landlord_id.name if property_rec.landlord_id else None,
                } if property_rec.landlord_id else None,
                'created_date': property_rec.create_date.isoformat() if property_rec.create_date else None,
                'updated_date': property_rec.write_date.isoformat() if property_rec.write_date else None,
            }
            
            return self._create_response(property_data)
            
        except Exception as e:
            _logger.error(f"Error getting property {property_id}: {e}")
            return self._create_response(error=str(e), code=500)
    
    @http.route('/api/ejar/properties', type='http', auth='none', methods=['POST'], csrf=False)
    def create_property(self, **kwargs):
        """Create new property"""
        auth_result = self._authenticate_api_request()
        if 'error' in auth_result:
            return self._create_response(error=auth_result['error'], code=auth_result['code'])
        
        data_result = self._validate_json_data(['name', 'property_type', 'area', 'monthly_rent'])
        if 'error' in data_result:
            return self._create_response(error=data_result['error'], code=data_result['code'])
        
        try:
            data = data_result['data']
            
            # Create property
            property_vals = {
                'name': data['name'],
                'property_type': data['property_type'],
                'area': data['area'],
                'monthly_rent': data['monthly_rent'],
                'description': data.get('description'),
                'property_subtype': data.get('property_subtype'),
                'built_area': data.get('built_area'),
                'bedrooms': data.get('bedrooms', 0),
                'bathrooms': data.get('bathrooms', 0),
                'parking_spaces': data.get('parking_spaces', 0),
                'floor_number': data.get('floor_number'),
                'total_floors': data.get('total_floors'),
                'security_deposit': data.get('security_deposit'),
                'broker_commission_rate': data.get('broker_commission_rate', 2.5),
                'address': data.get('address'),
                'city': data.get('city'),
                'district': data.get('district'),
                'neighborhood': data.get('neighborhood'),
                'latitude': data.get('latitude'),
                'longitude': data.get('longitude'),
                'furnishing_status': data.get('furnishing_status', 'unfurnished'),
                'property_condition': data.get('property_condition', 'good'),
                'construction_year': data.get('construction_year'),
                'status': data.get('status', 'available'),
            }
            
            # Handle features
            features = data.get('features', {})
            for feature in ['has_balcony', 'has_garden', 'has_pool', 'has_gym', 
                           'has_elevator', 'has_security', 'has_parking', 'has_storage',
                           'has_maid_room', 'has_laundry']:
                property_vals[feature] = features.get(feature, False)
            
            # Handle utilities
            utilities = data.get('utilities', {})
            for utility in ['electricity_included', 'water_included', 
                           'internet_included', 'maintenance_included']:
                property_vals[utility] = utilities.get(utility, False)
            
            # Handle landlord
            if data.get('landlord_id'):
                landlord = request.env['ejar.landlord'].sudo().search([
                    ('ejar_landlord_id', '=', data['landlord_id'])
                ], limit=1)
                if landlord:
                    property_vals['landlord_id'] = landlord.id
            
            property_rec = request.env['ejar.property'].sudo().create(property_vals)
            
            # Register with Ejar if auto-sync is enabled
            if property_rec.auto_sync_ejar:
                try:
                    property_rec.action_register_with_ejar()
                except Exception as e:
                    _logger.warning(f"Failed to auto-sync property {property_rec.id} with Ejar: {e}")
            
            return self._create_response({
                'id': property_rec.id,
                'ejar_id': property_rec.ejar_property_id,
                'message': 'Property created successfully'
            }, code=201)
            
        except Exception as e:
            _logger.error(f"Error creating property: {e}")
            return self._create_response(error=str(e), code=500)

    # Contract Management Endpoints
    
    @http.route('/api/ejar/contracts', type='http', auth='none', methods=['GET'], csrf=False)
    def get_contracts(self, **kwargs):
        """Get list of contracts"""
        auth_result = self._authenticate_api_request()
        if 'error' in auth_result:
            return self._create_response(error=auth_result['error'], code=auth_result['code'])
        
        try:
            # Parse query parameters
            limit = int(kwargs.get('limit', 50))
            offset = int(kwargs.get('offset', 0))
            status = kwargs.get('status')
            tenant_id = kwargs.get('tenant_id')
            landlord_id = kwargs.get('landlord_id')
            
            # Build domain
            domain = []
            if status:
                domain.append(('status', '=', status))
            if tenant_id:
                domain.append(('tenant_id.ejar_tenant_id', '=', tenant_id))
            if landlord_id:
                domain.append(('landlord_id.ejar_landlord_id', '=', landlord_id))
            
            # Search contracts
            contracts = request.env['ejar.contract'].sudo().search(
                domain, limit=limit, offset=offset, order='create_date desc'
            )
            
            # Prepare response data
            contracts_data = []
            for contract in contracts:
                contracts_data.append({
                    'id': contract.id,
                    'ejar_id': contract.ejar_contract_id,
                    'contract_number': contract.contract_number,
                    'status': contract.status,
                    'start_date': contract.start_date.isoformat() if contract.start_date else None,
                    'end_date': contract.end_date.isoformat() if contract.end_date else None,
                    'monthly_rent': contract.monthly_rent,
                    'security_deposit': contract.security_deposit,
                    'property': {
                        'id': contract.property_id.id if contract.property_id else None,
                        'name': contract.property_id.name if contract.property_id else None,
                        'ejar_id': contract.property_id.ejar_property_id if contract.property_id else None,
                    } if contract.property_id else None,
                    'tenant': {
                        'id': contract.tenant_id.id if contract.tenant_id else None,
                        'name': contract.tenant_id.name if contract.tenant_id else None,
                        'ejar_id': contract.tenant_id.ejar_tenant_id if contract.tenant_id else None,
                    } if contract.tenant_id else None,
                    'landlord': {
                        'id': contract.landlord_id.id if contract.landlord_id else None,
                        'name': contract.landlord_id.name if contract.landlord_id else None,
                        'ejar_id': contract.landlord_id.ejar_landlord_id if contract.landlord_id else None,
                    } if contract.landlord_id else None,
                    'created_date': contract.create_date.isoformat() if contract.create_date else None,
                })
            
            return self._create_response({
                'contracts': contracts_data,
                'total': len(contracts_data),
                'limit': limit,
                'offset': offset
            })
            
        except Exception as e:
            _logger.error(f"Error getting contracts: {e}")
            return self._create_response(error=str(e), code=500)
    
    @http.route('/api/ejar/contracts/<int:contract_id>', type='http', auth='none', methods=['GET'], csrf=False)
    def get_contract(self, contract_id, **kwargs):
        """Get specific contract details"""
        auth_result = self._authenticate_api_request()
        if 'error' in auth_result:
            return self._create_response(error=auth_result['error'], code=auth_result['code'])
        
        try:
            contract = request.env['ejar.contract'].sudo().browse(contract_id)
            if not contract.exists():
                return self._create_response(error='Contract not found', code=404)
            
            # Prepare detailed contract data
            contract_data = {
                'id': contract.id,
                'ejar_id': contract.ejar_contract_id,
                'contract_number': contract.contract_number,
                'status': contract.status,
                'start_date': contract.start_date.isoformat() if contract.start_date else None,
                'end_date': contract.end_date.isoformat() if contract.end_date else None,
                'duration_months': contract.duration_months,
                'monthly_rent': contract.monthly_rent,
                'annual_rent': contract.annual_rent,
                'security_deposit': contract.security_deposit,
                'broker_commission': contract.broker_commission,
                'payment_frequency': contract.payment_frequency,
                'advance_payment_months': contract.advance_payment_months,
                'late_fee_percentage': contract.late_fee_percentage,
                'renewal_notice_days': contract.renewal_notice_days,
                'terms_conditions': contract.terms_conditions,
                'special_conditions': contract.special_conditions,
                'property': {
                    'id': contract.property_id.id if contract.property_id else None,
                    'name': contract.property_id.name if contract.property_id else None,
                    'ejar_id': contract.property_id.ejar_property_id if contract.property_id else None,
                    'address': contract.property_id.address if contract.property_id else None,
                } if contract.property_id else None,
                'tenant': {
                    'id': contract.tenant_id.id if contract.tenant_id else None,
                    'name': contract.tenant_id.name if contract.tenant_id else None,
                    'ejar_id': contract.tenant_id.ejar_tenant_id if contract.tenant_id else None,
                    'phone': contract.tenant_id.phone if contract.tenant_id else None,
                    'email': contract.tenant_id.email if contract.tenant_id else None,
                } if contract.tenant_id else None,
                'landlord': {
                    'id': contract.landlord_id.id if contract.landlord_id else None,
                    'name': contract.landlord_id.name if contract.landlord_id else None,
                    'ejar_id': contract.landlord_id.ejar_landlord_id if contract.landlord_id else None,
                    'phone': contract.landlord_id.phone if contract.landlord_id else None,
                    'email': contract.landlord_id.email if contract.landlord_id else None,
                } if contract.landlord_id else None,
                'broker': {
                    'id': contract.broker_id.id if contract.broker_id else None,
                    'name': contract.broker_id.name if contract.broker_id else None,
                    'ejar_id': contract.broker_id.ejar_broker_id if contract.broker_id else None,
                } if contract.broker_id else None,
                'created_date': contract.create_date.isoformat() if contract.create_date else None,
                'updated_date': contract.write_date.isoformat() if contract.write_date else None,
            }
            
            return self._create_response(contract_data)
            
        except Exception as e:
            _logger.error(f"Error getting contract {contract_id}: {e}")
            return self._create_response(error=str(e), code=500)

    # Tenant Management Endpoints
    
    @http.route('/api/ejar/tenants', type='http', auth='none', methods=['GET'], csrf=False)
    def get_tenants(self, **kwargs):
        """Get list of tenants"""
        auth_result = self._authenticate_api_request()
        if 'error' in auth_result:
            return self._create_response(error=auth_result['error'], code=auth_result['code'])
        
        try:
            # Parse query parameters
            limit = int(kwargs.get('limit', 50))
            offset = int(kwargs.get('offset', 0))
            status = kwargs.get('status')
            
            # Build domain
            domain = []
            if status:
                domain.append(('status', '=', status))
            
            # Search tenants
            tenants = request.env['ejar.tenant'].sudo().search(
                domain, limit=limit, offset=offset, order='create_date desc'
            )
            
            # Prepare response data
            tenants_data = []
            for tenant in tenants:
                tenants_data.append({
                    'id': tenant.id,
                    'ejar_id': tenant.ejar_tenant_id,
                    'name': tenant.name,
                    'national_id': tenant.national_id,
                    'phone': tenant.phone,
                    'mobile': tenant.mobile,
                    'email': tenant.email,
                    'status': tenant.status,
                    'verification_status': tenant.verification_status,
                    'active_contracts_count': tenant.active_contracts_count,
                    'created_date': tenant.create_date.isoformat() if tenant.create_date else None,
                })
            
            return self._create_response({
                'tenants': tenants_data,
                'total': len(tenants_data),
                'limit': limit,
                'offset': offset
            })
            
        except Exception as e:
            _logger.error(f"Error getting tenants: {e}")
            return self._create_response(error=str(e), code=500)

    # Sync Status Endpoints
    
    @http.route('/api/ejar/sync/status', type='http', auth='none', methods=['GET'], csrf=False)
    def get_sync_status(self, **kwargs):
        """Get synchronization status"""
        auth_result = self._authenticate_api_request()
        if 'error' in auth_result:
            return self._create_response(error=auth_result['error'], code=auth_result['code'])
        
        try:
            # Get sync statistics
            sync_logs = request.env['ejar.sync.log'].sudo()
            
            # Recent sync operations (last 24 hours)
            recent_logs = sync_logs.search([
                ('create_date', '>=', fields.Datetime.now() - timedelta(hours=24))
            ])
            
            # Count by status
            status_counts = {}
            for log in recent_logs:
                status = log.status
                if status not in status_counts:
                    status_counts[status] = 0
                status_counts[status] += 1
            
            # Get failed operations
            failed_logs = sync_logs.search([
                ('status', '=', 'failed'),
                ('create_date', '>=', fields.Datetime.now() - timedelta(hours=24))
            ], limit=10, order='create_date desc')
            
            failed_operations = []
            for log in failed_logs:
                failed_operations.append({
                    'id': log.id,
                    'operation_type': log.operation_type,
                    'related_model': log.related_model,
                    'related_id': log.related_id,
                    'error_message': log.error_message,
                    'created_date': log.create_date.isoformat() if log.create_date else None,
                })
            
            return self._create_response({
                'sync_statistics': {
                    'total_operations': len(recent_logs),
                    'successful': status_counts.get('success', 0),
                    'failed': status_counts.get('failed', 0),
                    'pending': status_counts.get('pending', 0),
                },
                'failed_operations': failed_operations,
                'last_updated': fields.Datetime.now().isoformat(),
            })
            
        except Exception as e:
            _logger.error(f"Error getting sync status: {e}")
            return self._create_response(error=str(e), code=500)
    
    @http.route('/api/ejar/sync/retry/<int:log_id>', type='http', auth='none', methods=['POST'], csrf=False)
    def retry_sync_operation(self, log_id, **kwargs):
        """Retry failed sync operation"""
        auth_result = self._authenticate_api_request()
        if 'error' in auth_result:
            return self._create_response(error=auth_result['error'], code=auth_result['code'])
        
        try:
            sync_log = request.env['ejar.sync.log'].sudo().browse(log_id)
            if not sync_log.exists():
                return self._create_response(error='Sync log not found', code=404)
            
            if sync_log.status != 'failed':
                return self._create_response(error='Only failed operations can be retried', code=400)
            
            # Retry the operation
            sync_log.action_retry()
            
            return self._create_response({
                'message': 'Sync operation retry initiated',
                'log_id': log_id,
                'status': sync_log.status
            })
            
        except Exception as e:
            _logger.error(f"Error retrying sync operation {log_id}: {e}")
            return self._create_response(error=str(e), code=500)

    # Health Check Endpoint
    
    @http.route('/api/ejar/health', type='http', auth='none', methods=['GET'], csrf=False)
    def health_check(self, **kwargs):
        """Health check endpoint"""
        try:
            # Check database connection
            request.env['ejar.api.connector'].sudo().search([], limit=1)
            
            # Check Ejar API connectivity
            connector = request.env['ejar.api.connector'].sudo().get_active_connector()
            api_status = 'unknown'
            
            if connector:
                try:
                    test_result = connector.test_connection()
                    api_status = 'connected' if test_result else 'disconnected'
                except Exception:
                    api_status = 'error'
            
            return self._create_response({
                'status': 'healthy',
                'database': 'connected',
                'ejar_api': api_status,
                'timestamp': datetime.now().isoformat(),
                'version': '1.0.0'
            })
            
        except Exception as e:
            _logger.error(f"Health check failed: {e}")
            return self._create_response({
                'status': 'unhealthy',
                'error': str(e),
                'timestamp': datetime.now().isoformat()
            }, code=503)