# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError, UserError
import logging

_logger = logging.getLogger(__name__)


class EjarProperty(models.Model):
    """Ejar platform property management"""
    _name = 'ejar.property'
    _description = 'Ejar Property'
    _inherit = ['mail.thread']
    _order = 'name'
    _rec_name = 'name'

    # Basic Information
    name = fields.Char(string='Property Name', required=True, tracking=True)
    ejar_property_id = fields.Char(string='Ejar Property ID', readonly=True, copy=False, index=True)
    property_code = fields.Char(string='Property Code', required=True, copy=False, index=True)
    
    # Property Details
    property_type = fields.Selection([
        ('apartment', 'Apartment'),
        ('villa', 'Villa'),
        ('office', 'Office'),
        ('shop', 'Shop'),
        ('warehouse', 'Warehouse')
    ], string='Property Type', required=True, tracking=True)
    
    # Location Information
    address = fields.Text(string='Address', required=True)
    city = fields.Char(string='City', required=True, index=True)
    district = fields.Char(string='District')
    
    # Property Specifications
    total_area = fields.Float(string='Total Area (sqm)', required=True)
    bedrooms = fields.Integer(string='Bedrooms', default=0)
    bathrooms = fields.Integer(string='Bathrooms', default=0)
    
    # Financial Information
    monthly_rent = fields.Monetary(string='Monthly Rent', currency_field='currency_id', tracking=True)
    currency_id = fields.Many2one('res.currency', string='Currency', 
                                  default=lambda self: self.env.company.currency_id)
    
    # Status and Sync
    state = fields.Selection([
        ('draft', 'Draft'),
        ('available', 'Available'),
        ('rented', 'Rented'),
        ('maintenance', 'Under Maintenance'),
        ('inactive', 'Inactive')
    ], string='Status', default='draft', tracking=True)
    
    # Ejar Integration
    ejar_sync_status = fields.Selection([
        ('not_synced', 'Not Synced'),
        ('syncing', 'Syncing'),
        ('synced', 'Synced'),
        ('error', 'Error')
    ], string='Ejar Sync Status', default='not_synced', readonly=True)
    
    last_sync_date = fields.Datetime(string='Last Sync Date', readonly=True)
    sync_error_message = fields.Text(string='Sync Error Message', readonly=True)
    
    # Relations
    contract_ids = fields.One2many('ejar.contract', 'property_id', string='Contracts')
    active_contract_id = fields.Many2one('ejar.contract', string='Active Contract', 
                                         compute='_compute_active_contract', store=True)
    
    # Computed Fields
    contract_count = fields.Integer(string='Contract Count', compute='_compute_contract_count')
    
    @api.depends('contract_ids', 'contract_ids.state')
    def _compute_active_contract(self):
        for record in self:
            active_contract = record.contract_ids.filtered(lambda c: c.state == 'active')
            record.active_contract_id = active_contract[0] if active_contract else False
    
    @api.depends('contract_ids')
    def _compute_contract_count(self):
        for record in self:
            record.contract_count = len(record.contract_ids)
    
    @api.model
    def create(self, vals):
        """Override create to generate property code if not provided"""
        if not vals.get('property_code'):
            vals['property_code'] = self.env['ir.sequence'].next_by_code('ejar.property') or 'PROP-NEW'
        return super().create(vals)
    
    def action_sync_to_ejar(self):
        """Sync property to Ejar platform"""
        for record in self:
            try:
                record.ejar_sync_status = 'syncing'
                # Sync logic would go here
                record.ejar_sync_status = 'synced'
                record.last_sync_date = fields.Datetime.now()
                record.sync_error_message = False
            except Exception as e:
                record.ejar_sync_status = 'error'
                record.sync_error_message = str(e)
                _logger.error("Failed to sync property %s: %s", record.name, str(e))
    
    def action_view_contracts(self):
        """View property contracts"""
        return {
            'type': 'ir.actions.act_window',
            'name': _('Property Contracts'),
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