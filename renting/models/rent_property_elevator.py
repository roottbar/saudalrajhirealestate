# -*- coding: utf-8 -*-

from odoo import models, fields


class RentPropertyElevator(models.Model):
    _name = 'rent.property.elevator'
    _rec_name = 'elevator_maintenance_date'

    property_id = fields.Many2one('rent.property', copy=True, string='Properties', ondelete='cascade')

    # elevator_contract = fields.File(string='Elevator Contract')

    elevator_maintenance_description = fields.Char(string='Maintenance Description')
    elevator_number_name = fields.Char(string='Elevator Number/Name')

    elevator_maintenance_date = fields.Date(string='Maintenance Date')

    elevator_maintenance_value = fields.Float(string='Maintenance Value')




