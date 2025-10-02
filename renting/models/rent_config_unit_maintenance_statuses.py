# -*- coding: utf-8 -*-

from odoo import models, fields


class UnitMaintenanceStatusesConfig(models.Model):
    _name = 'rent.config.unit.maintenance.statuses'
    _rec_name = 'unit_maintenance_status_name'

    unit_maintenance_status_name = fields.Char(string='Maintenance Status', required=True)
    unit_maintenance_status_description = fields.Char(string='Description')
