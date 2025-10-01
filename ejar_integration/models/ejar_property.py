# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError, UserError
import logging

_logger = logging.getLogger(__name__)


class EjarProperty(models.Model):
    """Ejar platform property management"""
    _name = 'ejar.property'
    _description = 'Ejar Property'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'name'
    _rec_name = 'name'

    # Basic Information
    name = fields.Char(string='Property Name', required=True, tracking=True)
    ejar_property_id = fields.Char(string='Ejar Property ID', readonly=True, copy=False)
    property_code = fields.Char(string='Property Code', required=True, copy=False)
    
    # Property Details
    property_type_id = fields.Many2one('ejar.property.type', string='Property Type', required=True, tracking=True)
    category = fields.Selection(related='property_type_id.category', string='Category', store=True)
    
    # Location Information
    address = fields.Text(string='Address', required=True, tracking=True)
    city = fields.Char(string='City', required=True)
    district = fields.Char(string='District', required=True)
    neighborhood = fields.Char(string='Neighborhood')
    street = fields.Char(string='Street')
    building_number = fields.Char(string='Building Number')
    unit_number = fields.Char(string='Unit Number')
    postal_code = fields.Char(string='Postal Code')
    
    # Geographic Coordinates
    latitude = fields.Float(string='Latitude', digits=(10, 7))
    longitude = fields.Float(string='Longitude', digits=(10, 7))
    
    # Property Specifications
    total_area = fields.Float(string='Total Area (sqm)', required=True, tracking=True)
    built_area = fields.Float(string='Built Area (sqm)', tracking=True)
    land_area = fields.Float(string='Land Area (sqm)', tracking=True)
    
    # Rooms and Facilities
    bedrooms = fields.Integer(string='Bedrooms', default=0)
    bathrooms = fields.Integer(string='Bathrooms', default=0)
    living_rooms = fields.Integer(string='Living Rooms', default=0)
    kitchens = fields.Integer(string='Kitchens', default=0)
    parking_spaces = fields.Integer(string='Parking Spaces', default=0)
    
    # Building Information
    building_age = fields.Integer(string='Building Age (Years)')
    floor_number = fields.Integer(string='Floor Number')
    total_floors = fields.Integer(string='Total Floors in Building')
    has_elevator = fields.Boolean(string='Has Elevator')
    
    # Amenities
    has_balcony = fields.Boolean(string='Has Balcony')
    has_garden = fields.Boolean(string='Has Garden')
    has_pool = fields.Boolean(string='Has Swimming Pool')
    has_gym = fields.Boolean(string='Has Gym')
    has_security = fields.Boolean(string='Has Security')
    has_parking = fields.Boolean(string='Has Parking')
    is_furnished = fields.Boolean(string='Furnished')
    
    # Utilities
    electricity_available = fields.Boolean(string='Electricity Available', default=True)
    water_available = fields.Boolean(string='Water Available', default=True)
    gas_available = fields.Boolean(string='Gas Available')
    internet_available = fields.Boolean(string='Internet Available')
    
    # Legal Information
    title_deed_number = fields.Char(string='Title Deed Number', required=True)
    survey_number = fields.Char(string='Survey Number')
    plan_number = fields.Char(string='Plan Number')
    municipality_license = fields.Char(string='Municipality License')
    
    # Ownership Information
    landlord_id = fields.Many2one('ejar.landlord', string='Landlord', required=True, tracking=True)
    ownership_type = fields.Selection([
        ('owned', 'Owned'),
        ('leased', 'Leased'),
        ('managed', 'Managed')
    ], string='Ownership Type', default='owned', required=True)
    
    # Financial Information
    market_value = fields.Monetary(string='Market Value', tracking=True)
    monthly_rent = fields.Monetary(string='Monthly Rent', tracking=True)
    annual_rent = fields.Monetary(string='Annual Rent', compute='_compute_annual_rent', store=True)
    
    currency_id = fields.Many2one('res.currency', string='Currency', 
                                  default=lambda self: self.env.company.currency_id)
    
    # Status
    state = fields.Selection([
        ('draft', 'Draft'),
        ('available', 'Available'),
        ('rented', 'Rented'),
        ('maintenance', 'Under Maintenance'),
        ('unavailable', 'Unavailable')
    ], string='Status', default='draft', tracking=True)
    
    # Ejar Integration
    ejar_status = fields.Selection([
        ('not_registered', 'Not Registered'),
        ('pending', 'Pending Registration'),
        ('registered', 'Registered'),
        ('rejected', 'Rejected')
    ], string='Ejar Status', default='not_registered', tracking=True)
    
    # Related Records
    product_template_id = fields.Many2one('product.template', string='Product Template')
    rent_property_id = fields.Many2one('rent.property', string='Rent Property')
    
    # Company and Operating Unit
    company_id = fields.Many2one('res.company', string='Company', 
                                 default=lambda self: self.env.company)
    operating_unit_id = fields.Many2one('operating.unit', string='Operating Unit')
    
    # Contracts
    contract_ids = fields.One2many('ejar.contract', 'property_id', string='Contracts')
    active_contract_id = fields.Many2one('ejar.contract', string='Active Contract', 
                                         compute='_compute_active_contract')
    contract_count = fields.Integer(string='Contract Count', compute='_compute_contract_count')
    
    # Images and Documents
    image_ids = fields.One2many('ejar.property.image', 'property_id', string='Property Images')
    document_ids = fields.One2many('ejar.property.document', 'property_id', string='Property Documents')
    
    # Maintenance
    maintenance_ids = fields.One2many('ejar.property.maintenance', 'property_id', string='Maintenance Records')
    last_maintenance_date = fields.Date(string='Last Maintenance Date', compute='_compute_last_maintenance')
    
    # Sync Information
    last_sync_date = fields.Datetime(string='Last Sync Date', readonly=True)
    sync_status = fields.Selection([
        ('pending', 'Pending'),
        ('synced', 'Synced'),
        ('error', 'Error')
    ], string='Sync Status', default='pending')
    sync_error_message = fields.Text(string='Sync Error Message', readonly=True)
    
    @api.depends('monthly_rent')
    def _compute_annual_rent(self):
        """Calculate annual rent"""
        for record in self:
            record.annual_rent = record.monthly_rent * 12
    
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
    
    @api.depends('maintenance_ids')
    def _compute_last_maintenance(self):
        """Get last maintenance date"""
        for record in self:
            if record.maintenance_ids:
                record.last_maintenance_date = max(record.maintenance_ids.mapped('date'))
            else:
                record.last_maintenance_date = False
    
    @api.constrains('total_area', 'built_area', 'land_area')
    def _check_areas(self):
        """Validate area values"""
        for record in self:
            if record.total_area <= 0:
                raise ValidationError(_('Total area must be greater than zero'))
            
            if record.built_area and record.built_area > record.total_area:
                raise ValidationError(_('Built area cannot exceed total area'))
            
            if record.land_area and record.land_area > record.total_area:
                raise ValidationError(_('Land area cannot exceed total area'))
    
    @api.constrains('bedrooms', 'bathrooms', 'living_rooms', 'kitchens', 'parking_spaces')
    def _check_room_counts(self):
        """Validate room counts"""
        for record in self:
            if any(count < 0 for count in [record.bedrooms, record.bathrooms, 
                                          record.living_rooms, record.kitchens, record.parking_spaces]):
                raise ValidationError(_('Room counts cannot be negative'))
    
    @api.constrains('latitude', 'longitude')
    def _check_coordinates(self):
        """Validate geographic coordinates"""
        for record in self:
            if record.latitude and not (-90 <= record.latitude <= 90):
                raise ValidationError(_('Latitude must be between -90 and 90 degrees'))
            
            if record.longitude and not (-180 <= record.longitude <= 180):
                raise ValidationError(_('Longitude must be between -180 and 180 degrees'))
    
    @api.model
    def create(self, vals):
        """Override create to generate property code"""
        if not vals.get('property_code'):
            vals['property_code'] = self.env['ir.sequence'].next_by_code('ejar.property') or _('New')
        return super(EjarProperty, self).create(vals)
    
    def action_register_with_ejar(self):
        """Register property with Ejar platform"""
        self.ensure_one()
        
        if self.ejar_status != 'not_registered':
            raise UserError(_('Property is already registered or pending registration'))
        
        try:
            # Prepare property data for Ejar API
            property_data = self._prepare_ejar_property_data()
            
            # Submit to Ejar API
            api_connector = self.env['ejar.api.connector']
            response = api_connector.register_property(property_data)
            
            if response.get('success'):
                self.write({
                    'ejar_property_id': response.get('property_id'),
                    'ejar_status': 'pending',
                    'sync_status': 'synced',
                    'sync_error_message': False,
                    'last_sync_date': fields.Datetime.now()
                })
                
                self.message_post(
                    body=_('Property successfully registered with Ejar platform. ID: %s') % response.get('property_id'),
                    message_type='notification'
                )
                
                return {
                    'type': 'ir.actions.client',
                    'tag': 'display_notification',
                    'params': {
                        'title': _('Success'),
                        'message': _('Property registered with Ejar platform successfully!'),
                        'type': 'success',
                    }
                }
            else:
                raise UserError(_('Failed to register property with Ejar: %s') % response.get('error', 'Unknown error'))
                
        except Exception as e:
            self.write({
                'sync_status': 'error',
                'sync_error_message': str(e)
            })
            _logger.error(f"Failed to register property {self.property_code} with Ejar: {e}")
            raise UserError(_('Failed to register property with Ejar: %s') % str(e))
    
    def _prepare_ejar_property_data(self):
        """Prepare property data for Ejar API"""
        return {
            'property_code': self.property_code,
            'name': self.name,
            'type': self.property_type_id.code,
            'category': self.category,
            'location': {
                'address': self.address,
                'city': self.city,
                'district': self.district,
                'neighborhood': self.neighborhood,
                'street': self.street,
                'building_number': self.building_number,
                'unit_number': self.unit_number,
                'postal_code': self.postal_code,
                'latitude': self.latitude,
                'longitude': self.longitude,
            },
            'specifications': {
                'total_area': self.total_area,
                'built_area': self.built_area,
                'land_area': self.land_area,
                'bedrooms': self.bedrooms,
                'bathrooms': self.bathrooms,
                'living_rooms': self.living_rooms,
                'kitchens': self.kitchens,
                'parking_spaces': self.parking_spaces,
            },
            'building_info': {
                'building_age': self.building_age,
                'floor_number': self.floor_number,
                'total_floors': self.total_floors,
                'has_elevator': self.has_elevator,
            },
            'amenities': {
                'has_balcony': self.has_balcony,
                'has_garden': self.has_garden,
                'has_pool': self.has_pool,
                'has_gym': self.has_gym,
                'has_security': self.has_security,
                'has_parking': self.has_parking,
                'is_furnished': self.is_furnished,
            },
            'utilities': {
                'electricity_available': self.electricity_available,
                'water_available': self.water_available,
                'gas_available': self.gas_available,
                'internet_available': self.internet_available,
            },
            'legal_info': {
                'title_deed_number': self.title_deed_number,
                'survey_number': self.survey_number,
                'plan_number': self.plan_number,
                'municipality_license': self.municipality_license,
            },
            'landlord': {
                'id': self.landlord_id.ejar_landlord_id,
                'national_id': self.landlord_id.national_id,
                'name': self.landlord_id.name,
            },
            'financial': {
                'market_value': self.market_value,
                'monthly_rent': self.monthly_rent,
            }
        }
    
    def action_check_ejar_status(self):
        """Check property status on Ejar platform"""
        self.ensure_one()
        
        if not self.ejar_property_id:
            raise UserError(_('Property has not been registered with Ejar yet'))
        
        try:
            api_connector = self.env['ejar.api.connector']
            status_data = api_connector.get_property_status(self.ejar_property_id)
            
            if status_data.get('success'):
                old_status = self.ejar_status
                new_status = status_data.get('status')
                
                self.write({
                    'ejar_status': new_status,
                    'last_sync_date': fields.Datetime.now(),
                    'sync_status': 'synced',
                    'sync_error_message': False
                })
                
                # Log status change
                if old_status != new_status:
                    self.message_post(
                        body=_('Ejar status updated from %s to %s') % (old_status, new_status),
                        message_type='notification'
                    )
                
                return {
                    'type': 'ir.actions.client',
                    'tag': 'display_notification',
                    'params': {
                        'title': _('Status Updated'),
                        'message': _('Property status updated to: %s') % new_status,
                        'type': 'success',
                    }
                }
            else:
                raise UserError(_('Failed to get property status from Ejar: %s') % status_data.get('error'))
                
        except Exception as e:
            self.write({
                'sync_status': 'error',
                'sync_error_message': str(e)
            })
            _logger.error(f"Failed to check Ejar status for property {self.property_code}: {e}")
            raise UserError(_('Failed to check Ejar status: %s') % str(e))
    
    def action_view_contracts(self):
        """View property contracts"""
        self.ensure_one()
        return {
            'name': _('Property Contracts'),
            'type': 'ir.actions.act_window',
            'res_model': 'ejar.contract',
            'view_mode': 'tree,form',
            'domain': [('property_id', '=', self.id)],
            'context': {'default_property_id': self.id}
        }
    
    def action_create_contract(self):
        """Create new contract for this property"""
        self.ensure_one()
        return {
            'name': _('New Contract'),
            'type': 'ir.actions.act_window',
            'res_model': 'ejar.contract',
            'view_mode': 'form',
            'context': {
                'default_property_id': self.id,
                'default_landlord_id': self.landlord_id.id,
                'default_monthly_rent': self.monthly_rent,
            }
        }


class EjarPropertyImage(models.Model):
    """Property images"""
    _name = 'ejar.property.image'
    _description = 'Property Image'
    _order = 'sequence, id'

    property_id = fields.Many2one('ejar.property', string='Property', required=True, ondelete='cascade')
    sequence = fields.Integer(string='Sequence', default=10)
    name = fields.Char(string='Name', required=True)
    image = fields.Image(string='Image', required=True)
    description = fields.Text(string='Description')
    is_main = fields.Boolean(string='Main Image')
    
    @api.model
    def create(self, vals):
        """Ensure only one main image per property"""
        if vals.get('is_main'):
            property_id = vals.get('property_id')
            if property_id:
                self.search([('property_id', '=', property_id), ('is_main', '=', True)]).write({'is_main': False})
        return super(EjarPropertyImage, self).create(vals)
    
    def write(self, vals):
        """Ensure only one main image per property"""
        if vals.get('is_main'):
            for record in self:
                record.property_id.image_ids.filtered(lambda i: i.id != record.id).write({'is_main': False})
        return super(EjarPropertyImage, self).write(vals)


class EjarPropertyDocument(models.Model):
    """Property documents"""
    _name = 'ejar.property.document'
    _description = 'Property Document'
    _order = 'document_type, name'

    property_id = fields.Many2one('ejar.property', string='Property', required=True, ondelete='cascade')
    name = fields.Char(string='Document Name', required=True)
    document_type = fields.Selection([
        ('title_deed', 'Title Deed'),
        ('survey', 'Survey Document'),
        ('plan', 'Building Plan'),
        ('license', 'Municipality License'),
        ('insurance', 'Insurance Policy'),
        ('other', 'Other')
    ], string='Document Type', required=True)
    
    attachment_id = fields.Many2one('ir.attachment', string='Attachment', required=True)
    description = fields.Text(string='Description')
    expiry_date = fields.Date(string='Expiry Date')
    is_required = fields.Boolean(string='Required for Ejar', default=True)


class EjarPropertyMaintenance(models.Model):
    """Property maintenance records"""
    _name = 'ejar.property.maintenance'
    _description = 'Property Maintenance'
    _order = 'date desc'

    property_id = fields.Many2one('ejar.property', string='Property', required=True, ondelete='cascade')
    name = fields.Char(string='Maintenance Description', required=True)
    date = fields.Date(string='Maintenance Date', required=True, default=fields.Date.today)
    
    maintenance_type = fields.Selection([
        ('preventive', 'Preventive'),
        ('corrective', 'Corrective'),
        ('emergency', 'Emergency'),
        ('inspection', 'Inspection')
    ], string='Maintenance Type', required=True)
    
    cost = fields.Monetary(string='Cost')
    currency_id = fields.Many2one('res.currency', string='Currency', 
                                  default=lambda self: self.env.company.currency_id)
    
    contractor = fields.Char(string='Contractor')
    notes = fields.Text(string='Notes')
    
    state = fields.Selection([
        ('planned', 'Planned'),
        ('in_progress', 'In Progress'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled')
    ], string='Status', default='planned')