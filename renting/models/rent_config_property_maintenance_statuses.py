# -*- coding: utf-8 -*-

from odoo import models, fields


class PropertyMaintenanceStatusesConfig(models.Model):
    _name = 'rent.config.property.maintenance.statuses'
    _rec_name = 'property_maintenance_status_name'

    property_maintenance_status_name = fields.Char(string='Maintenance Status', required=True)
    property_maintenance_status_description = fields.Char(string='Description')
