# -*- coding: utf-8 -*-

from odoo import models, fields


class UnitTypesConfig(models.Model):
    _name = 'rent.config.unit.types'
    _rec_name = 'unit_type_name'

    unit_type_name = fields.Char(string='Unit Type', required=True)
    unit_type_description = fields.Char(string='Description')
