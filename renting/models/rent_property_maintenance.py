# -*- coding: utf-8 -*-

from odoo import models, fields


class RentPropertyMaintenance(models.Model):
    _name = 'rent.property.maintenance'
    _rec_name = 'property_maintenance_date'

    property_id = fields.Many2one('rent.property', copy=True, string='Properties', ondelete='cascade')

    property_maintenance_description = fields.Char(string='Maintenance Description')
    property_maintenance_date = fields.Date(string='Maintenance Date')
    property_maintenance_value = fields.Float(string='Maintenance Value')
    property_rent_config_maintenance_type_id = fields.Many2one('rent.config.property.maintenance.types',
                                                               string='Maintenance Type',
                                                               copy=True)  # Related field to menu item "Maintenance Types"
    property_rent_config_maintenance_status_id = fields.Many2one('rent.config.property.maintenance.statuses',
                                                                 string='Maintenance Status',
                                                                 copy=True)  # Related field to menu item "Maintenance Statuses"
