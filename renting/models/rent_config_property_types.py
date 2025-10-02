# -*- coding: utf-8 -*-

from odoo import models, fields


class PropertyTypesConfig(models.Model):
    _name = 'rent.config.property.types'
    _rec_name = 'property_type_name'

    property_type_name = fields.Char(string='Property Type', required=True)
    property_type_description = fields.Char(string='Description')
