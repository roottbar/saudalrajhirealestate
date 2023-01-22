# -*- coding: utf-8 -*-

from odoo import models, fields


class UnitPurposesConfig(models.Model):
    _name = 'rent.config.unit.purposes'
    _rec_name = 'unit_purpose_name'

    unit_purpose_name = fields.Char(string='Unit Purpose', required=True)
    unit_purpose_description = fields.Char(string='Description')