# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError, UserError
import logging

_logger = logging.getLogger(__name__)


class ProductTemplateInherit(models.Model):
    """Inherit Product Template to integrate with Ejar properties"""
    _inherit = 'product.template'

    # Ejar Integration Fields
    is_ejar_property = fields.Boolean(string='Is Ejar Property', default=False,
                                     help='Check if this product represents an Ejar property')
    
    ejar_property_id = fields.Many2one('ejar.property', string='Ejar Property',
                                      help='Related Ejar property record')
    
    # Property Type
    property_type = fields.Selection([
        ('residential', 'Residential'),
        ('commercial', 'Commercial'),
        ('industrial', 'Industrial'),
        ('land', 'Land'),
        ('mixed_use', 'Mixed Use')
    ], string='Property Type', help='Type of property')
    
    property_subtype = fields.Selection([
        # Residential subtypes
        ('apartment', 'Apartment'),
        ('villa', 'Villa'),
        ('townhouse', 'Townhouse'),
        ('studio', 'Studio'),
        ('duplex', 'Duplex'),
        ('penthouse', 'Penthouse'),
        ('compound', 'Compound'),
        
        # Commercial subtypes
        ('office', 'Office'),
        ('retail', 'Retail'),
        ('warehouse', 'Warehouse'),
        ('showroom', 'Showroom'),
        ('restaurant', 'Restaurant'),
        ('clinic', 'Clinic'),
        ('hotel', 'Hotel'),
        
        # Industrial subtypes
        ('factory', 'Factory'),
        ('workshop', 'Workshop'),
        ('storage', 'Storage'),
        
        # Land subtypes
        ('residential_land', 'Residential Land'),
        ('commercial_land', 'Commercial Land'),
        ('industrial_land', 'Industrial Land'),
        ('agricultural_land', 'Agricultural Land')
    ], string='Property Subtype', help='Subtype of property')
    
    # Property Details
    property_area = fields.Float(string='Property Area (sqm)', help='Total area in square meters')
    built_area = fields.Float(string='Built Area (sqm)', help='Built-up area in square meters')
    
    bedrooms_count = fields.Integer(string='Bedrooms Count', default=0)
    bathrooms_count = fields.Integer(string='Bathrooms Count', default=0)
    parking_spaces = fields.Integer(string='Parking Spaces', default=0)
    
    floor_number = fields.Integer(string='Floor Number')
    total_floors = fields.Integer(string='Total Floors in Building')
    
    # Property Features
    has_balcony = fields.Boolean(string='Has Balcony', default=False)
    has_garden = fields.Boolean(string='Has Garden', default=False)
    has_pool = fields.Boolean(string='Has Swimming Pool', default=False)
    has_gym = fields.Boolean(string='Has Gym', default=False)
    has_elevator = fields.Boolean(string='Has Elevator', default=False)
    has_security = fields.Boolean(string='Has Security', default=False)
    has_parking = fields.Boolean(string='Has Parking', default=False)
    has_storage = fields.Boolean(string='Has Storage Room', default=False)
    has_maid_room = fields.Boolean(string='Has Maid Room', default=False)
    has_laundry = fields.Boolean(string='Has Laundry Room', default=False)
    
    # Furnishing
    furnishing_status = fields.Selection([
        ('unfurnished', 'Unfurnished'),
        ('semi_furnished', 'Semi Furnished'),
        ('fully_furnished', 'Fully Furnished')
    ], string='Furnishing Status', default='unfurnished')
    
    # Property Condition
    property_condition = fields.Selection([
        ('excellent', 'Excellent'),
        ('very_good', 'Very Good'),
        ('good', 'Good'),
        ('fair', 'Fair'),
        ('needs_renovation', 'Needs Renovation')
    ], string='Property Condition', default='good')
    
    construction_year = fields.Integer(string='Construction Year')
    property_age = fields.Integer(string='Property Age (Years)', compute='_compute_property_age', store=True)
    
    # Location Details
    property_address = fields.Text(string='Property Address')
    property_city = fields.Char(string='Property City')
    property_district = fields.Char(string='Property District')
    property_neighborhood = fields.Char(string='Property Neighborhood')
    
    latitude = fields.Float(string='Latitude', digits=(10, 7))
    longitude = fields.Float(string='Longitude', digits=(10, 7))
    
    # Rental Information
    monthly_rent = fields.Monetary(string='Monthly Rent')
    annual_rent = fields.Monetary(string='Annual Rent', compute='_compute_annual_rent', store=True)
    
    security_deposit_amount = fields.Monetary(string='Security Deposit Amount')
    broker_commission_rate = fields.Float(string='Broker Commission Rate (%)', default=2.5)
    broker_commission_amount = fields.Monetary(string='Broker Commission Amount',
                                              compute='_compute_broker_commission', store=True)
    
    # Utilities
    electricity_included = fields.Boolean(string='Electricity Included', default=False)
    water_included = fields.Boolean(string='Water Included', default=False)
    internet_included = fields.Boolean(string='Internet Included', default=False)
    maintenance_included = fields.Boolean(string='Maintenance Included', default=False)
    
    # Property Status
    property_status = fields.Selection([
        ('available', 'Available'),
        ('rented', 'Rented'),
        ('maintenance', 'Under Maintenance'),
        ('reserved', 'Reserved'),
        ('not_available', 'Not Available')
    ], string='Property Status', default='available')
    
    # Ejar Sync Status
    ejar_sync_status = fields.Selection([
        ('not_synced', 'Not Synced'),
        ('pending', 'Pending'),
        ('synced', 'Synced'),
        ('error', 'Error')
    ], string='Ejar Sync Status', default='not_synced', readonly=True)
    
    ejar_sync_date = fields.Datetime(string='Last Ejar Sync Date', readonly=True)
    ejar_sync_error = fields.Text(string='Ejar Sync Error', readonly=True)
    
    # Auto-sync
    auto_sync_ejar = fields.Boolean(string='Auto Sync with Ejar', default=True,
                                   help='Automatically sync with Ejar when product is updated')
    
    @api.depends('construction_year')
    def _compute_property_age(self):
        """Calculate property age"""
        current_year = fields.Date.today().year
        for product in self:
            if product.construction_year:
                product.property_age = max(current_year - product.construction_year, 0)
            else:
                product.property_age = 0
    
    @api.depends('monthly_rent')
    def _compute_annual_rent(self):
        """Calculate annual rent"""
        for product in self:
            product.annual_rent = product.monthly_rent * 12
    
    @api.depends('annual_rent', 'broker_commission_rate')
    def _compute_broker_commission(self):
        """Calculate broker commission amount"""
        for product in self:
            if product.annual_rent and product.broker_commission_rate:
                product.broker_commission_amount = product.annual_rent * (product.broker_commission_rate / 100)
            else:
                product.broker_commission_amount = 0
    
    @api.constrains('property_area', 'built_area')
    def _check_areas(self):
        """Validate property areas"""
        for product in self:
            if product.is_ejar_property:
                if product.property_area <= 0:
                    raise ValidationError(_('Property area must be greater than zero'))
                
                if product.built_area > product.property_area:
                    raise ValidationError(_('Built area cannot exceed total property area'))
    
    @api.constrains('bedrooms_count', 'bathrooms_count', 'parking_spaces')
    def _check_counts(self):
        """Validate counts"""
        for product in self:
            if product.is_ejar_property:
                if product.bedrooms_count < 0:
                    raise ValidationError(_('Bedrooms count cannot be negative'))
                
                if product.bathrooms_count < 0:
                    raise ValidationError(_('Bathrooms count cannot be negative'))
                
                if product.parking_spaces < 0:
                    raise ValidationError(_('Parking spaces cannot be negative'))
    
    @api.constrains('floor_number', 'total_floors')
    def _check_floors(self):
        """Validate floor information"""
        for product in self:
            if product.is_ejar_property and product.floor_number and product.total_floors:
                if product.floor_number > product.total_floors:
                    raise ValidationError(_('Floor number cannot exceed total floors'))
    
    @api.constrains('monthly_rent', 'security_deposit_amount')
    def _check_amounts(self):
        """Validate amounts"""
        for product in self:
            if product.is_ejar_property:
                if product.monthly_rent <= 0:
                    raise ValidationError(_('Monthly rent must be greater than zero'))
                
                if product.security_deposit_amount < 0:
                    raise ValidationError(_('Security deposit amount cannot be negative'))
    
    @api.constrains('construction_year')
    def _check_construction_year(self):
        """Validate construction year"""
        current_year = fields.Date.today().year
        for product in self:
            if product.construction_year:
                if product.construction_year < 1900 or product.construction_year > current_year + 5:
                    raise ValidationError(_('Construction year must be between 1900 and %d') % (current_year + 5))
    
    @api.onchange('is_ejar_property')
    def _onchange_is_ejar_property(self):
        """Handle Ejar property flag change"""
        if self.is_ejar_property:
            # Set product as service type for rental
            self.type = 'service'
            self.invoice_policy = 'order'
            
            # Set default category for properties
            property_category = self.env['product.category'].search([
                ('name', 'ilike', 'property')
            ], limit=1)
            if property_category:
                self.categ_id = property_category
        else:
            # Clear Ejar-related fields
            self.ejar_property_id = False
            self.property_type = False
            self.property_subtype = False
    
    @api.onchange('property_type')
    def _onchange_property_type(self):
        """Handle property type change"""
        if self.property_type:
            # Clear subtype when type changes
            self.property_subtype = False
    
    @api.onchange('monthly_rent')
    def _onchange_monthly_rent(self):
        """Handle monthly rent change"""
        if self.monthly_rent:
            # Update list price
            self.list_price = self.monthly_rent
            
            # Set default security deposit (usually 1-2 months rent)
            if not self.security_deposit_amount:
                self.security_deposit_amount = self.monthly_rent
    
    @api.onchange('property_subtype')
    def _onchange_property_subtype(self):
        """Handle property subtype change"""
        if self.property_subtype:
            # Set default values based on subtype
            if self.property_subtype == 'studio':
                self.bedrooms_count = 0
                self.bathrooms_count = 1
            elif self.property_subtype == 'apartment':
                if not self.bedrooms_count:
                    self.bedrooms_count = 2
                if not self.bathrooms_count:
                    self.bathrooms_count = 2
            elif self.property_subtype == 'villa':
                if not self.bedrooms_count:
                    self.bedrooms_count = 4
                if not self.bathrooms_count:
                    self.bathrooms_count = 3
                self.has_garden = True
                self.has_parking = True
    
    def action_create_ejar_property(self):
        """Create Ejar property record from product"""
        self.ensure_one()
        
        if not self.is_ejar_property:
            raise UserError(_('This product is not marked as Ejar property'))
        
        if self.ejar_property_id:
            raise UserError(_('Ejar property record already exists for this product'))
        
        # Prepare property data
        property_vals = self._prepare_ejar_property_data()
        
        # Create property record
        property_rec = self.env['ejar.property'].create(property_vals)
        
        # Link to product
        self.ejar_property_id = property_rec.id
        
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'ejar.property',
            'res_id': property_rec.id,
            'view_mode': 'form',
            'target': 'current',
        }
    
    def _prepare_ejar_property_data(self):
        """Prepare data for Ejar property creation"""
        return {
            'name': self.name,
            'product_template_id': self.id,
            'property_type': self.property_type,
            'property_subtype': self.property_subtype,
            'area': self.property_area,
            'built_area': self.built_area,
            'bedrooms': self.bedrooms_count,
            'bathrooms': self.bathrooms_count,
            'parking_spaces': self.parking_spaces,
            'floor_number': self.floor_number,
            'total_floors': self.total_floors,
            'has_balcony': self.has_balcony,
            'has_garden': self.has_garden,
            'has_pool': self.has_pool,
            'has_gym': self.has_gym,
            'has_elevator': self.has_elevator,
            'has_security': self.has_security,
            'has_parking': self.has_parking,
            'has_storage': self.has_storage,
            'has_maid_room': self.has_maid_room,
            'has_laundry': self.has_laundry,
            'furnishing_status': self.furnishing_status,
            'property_condition': self.property_condition,
            'construction_year': self.construction_year,
            'address': self.property_address,
            'city': self.property_city,
            'district': self.property_district,
            'neighborhood': self.property_neighborhood,
            'latitude': self.latitude,
            'longitude': self.longitude,
            'monthly_rent': self.monthly_rent,
            'security_deposit': self.security_deposit_amount,
            'broker_commission_rate': self.broker_commission_rate,
            'electricity_included': self.electricity_included,
            'water_included': self.water_included,
            'internet_included': self.internet_included,
            'maintenance_included': self.maintenance_included,
            'status': self.property_status,
            'company_id': self.company_id.id,
        }
    
    def action_sync_with_ejar(self):
        """Manually sync with Ejar"""
        self.ensure_one()
        
        if not self.is_ejar_property:
            raise UserError(_('This product is not marked as Ejar property'))
        
        try:
            if not self.ejar_property_id:
                # Create Ejar property if not exists
                self.action_create_ejar_property()
            
            # Sync with Ejar platform
            self.ejar_property_id.action_register_with_ejar()
            
            self.write({
                'ejar_sync_status': 'synced',
                'ejar_sync_date': fields.Datetime.now(),
                'ejar_sync_error': False,
            })
            
            return {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'title': _('Sync Successful'),
                    'message': _('Product successfully synced with Ejar'),
                    'type': 'success',
                }
            }
            
        except Exception as e:
            self.write({
                'ejar_sync_status': 'error',
                'ejar_sync_error': str(e),
                'ejar_sync_date': fields.Datetime.now(),
            })
            
            raise UserError(_('Sync failed: %s') % str(e))
    
    def action_view_ejar_property(self):
        """View related Ejar property"""
        self.ensure_one()
        
        if not self.ejar_property_id:
            raise UserError(_('No Ejar property found for this product'))
        
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'ejar.property',
            'res_id': self.ejar_property_id.id,
            'view_mode': 'form',
            'target': 'current',
        }
    
    def action_set_available(self):
        """Set property as available"""
        self.ensure_one()
        
        self.property_status = 'available'
        
        if self.ejar_property_id:
            self.ejar_property_id.status = 'available'
    
    def action_set_rented(self):
        """Set property as rented"""
        self.ensure_one()
        
        self.property_status = 'rented'
        
        if self.ejar_property_id:
            self.ejar_property_id.status = 'rented'
    
    def action_set_maintenance(self):
        """Set property under maintenance"""
        self.ensure_one()
        
        self.property_status = 'maintenance'
        
        if self.ejar_property_id:
            self.ejar_property_id.status = 'maintenance'
    
    @api.model
    def _cron_sync_ejar_properties(self):
        """Cron job to sync pending Ejar properties"""
        pending_products = self.search([
            ('is_ejar_property', '=', True),
            ('ejar_sync_status', 'in', ['not_synced', 'error']),
            ('auto_sync_ejar', '=', True)
        ])
        
        for product in pending_products:
            try:
                product.action_sync_with_ejar()
                _logger.info(f"Successfully synced product {product.name} with Ejar")
            except Exception as e:
                _logger.error(f"Failed to sync product {product.name} with Ejar: {e}")
    
    def write(self, vals):
        """Override write to handle Ejar field changes"""
        result = super(ProductTemplateInherit, self).write(vals)
        
        # Check if Ejar-related fields changed
        ejar_fields = ['name', 'monthly_rent', 'property_area', 'bedrooms_count', 
                      'bathrooms_count', 'property_address', 'property_status']
        
        if any(field in vals for field in ejar_fields):
            for product in self:
                if (product.is_ejar_property and product.ejar_property_id and 
                    product.auto_sync_ejar):
                    try:
                        # Update Ejar property with new data
                        property_vals = product._prepare_ejar_property_data()
                        product.ejar_property_id.write(property_vals)
                        
                        # Sync with Ejar platform if needed
                        if product.ejar_property_id.ejar_sync_status == 'synced':
                            product.ejar_property_id.action_update_in_ejar()
                            
                    except Exception as e:
                        _logger.error(f"Failed to update Ejar property for product {product.name}: {e}")
        
        return result


class ProductProductInherit(models.Model):
    """Inherit Product Variant for Ejar integration"""
    _inherit = 'product.product'

    # Inherit Ejar fields from template
    is_ejar_property = fields.Boolean(related='product_tmpl_id.is_ejar_property', store=True)
    ejar_property_id = fields.Many2one(related='product_tmpl_id.ejar_property_id', store=True)
    property_type = fields.Selection(related='product_tmpl_id.property_type', store=True)
    property_status = fields.Selection(related='product_tmpl_id.property_status', store=True)
    monthly_rent = fields.Monetary(related='product_tmpl_id.monthly_rent', store=True)
    
    def action_view_ejar_property(self):
        """View related Ejar property"""
        return self.product_tmpl_id.action_view_ejar_property()
    
    def action_sync_with_ejar(self):
        """Sync with Ejar"""
        return self.product_tmpl_id.action_sync_with_ejar()