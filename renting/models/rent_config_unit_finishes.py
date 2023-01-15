# -*- coding: utf-8 -*-

from odoo import models, fields


class UnitFinishesConfig(models.Model):
    _name = 'rent.config.unit.finishes'
    _rec_name = 'unit_finish_name'

    unit_finish_name = fields.Char(string='Unit finish', required=True)
    unit_finish_description = fields.Char(string='Description')
