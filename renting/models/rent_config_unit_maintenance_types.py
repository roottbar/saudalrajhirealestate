# -*- coding: utf-8 -*-

from odoo import models, fields


class UnitMaintenanceTypesConfig(models.Model):
    _name = 'rent.config.unit.maintenance.types'
    _rec_name = 'unit_maintenance_type_name'

    unit_maintenance_type_name = fields.Char(string='Maintenance Type', required=True)
    unit_maintenance_type_description = fields.Char(string='Description')
