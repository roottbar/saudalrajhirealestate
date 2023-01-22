# -*- coding: utf-8 -*-

from odoo import models, fields


class PropertyPurposesConfig(models.Model):
    _name = 'rent.config.property.purposes'
    _rec_name = 'property_purpose_name'

    property_purpose_name = fields.Char(string='Property Purpose', required=True)
    property_purpose_description = fields.Char(string='Description')