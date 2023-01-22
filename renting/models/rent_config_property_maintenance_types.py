# -*- coding: utf-8 -*-

from odoo import models, fields


class PropertyMaintenanceTypesConfig(models.Model):
    _name = 'rent.config.property.maintenance.types'
    _rec_name = 'property_maintenance_type_name'

    property_maintenance_type_name = fields.Char(string='Maintenance Type', required=True)
    property_maintenance_type_description = fields.Char(string='Description')
