# -*- coding: utf-8 -*-

from odoo import models, fields


class UnitOverlooksConfig(models.Model):
    _name = 'rent.config.unit.overlooks'
    _rec_name = 'unit_overlook_name'

    unit_overlook_name = fields.Char(string='Unit Overlooking', required=True)
    unit_overlook_description = fields.Char(string='Description')
