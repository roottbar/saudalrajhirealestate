# -*- coding: utf-8 -*-

from odoo import models, fields


class RentUnitMaintenance(models.Model):
    _name = 'rent.unit.maintenance'
    _rec_name = 'unit_maintenance_date'

    product_id = fields.Many2one('product.template', copy=True, string='Units', ondelete='cascade')

    unit_maintenance_description = fields.Char(string='Maintenance Description')
    unit_maintenance_date = fields.Date(string='Maintenance Date')
    unit_maintenance_value = fields.Float(string='Maintenance Value')
    unit_rent_config_unit_maintenance_type_id = fields.Many2one('rent.config.unit.maintenance.types',
                                                                string='Maintenance Type', copy=True)                      # Related field to menu item "Maintenance Types"
    unit_rent_config_unit_maintenance_status_id = fields.Many2one('rent.config.unit.maintenance.statuses',
                                                                  string='Maintenance Status', copy=True)                   # Related field to menu item "Maintenance Statuses"
