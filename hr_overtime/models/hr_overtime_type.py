# -*- coding: utf-8 -*-
from odoo import models, fields, api, _


class HrOvertimeType(models.Model):
    _name = 'hr.overtime.type'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = "Overtime Type"

    name = fields.Char(required=True)
    transportation_allowance = fields.Boolean(string="Transportation", copy=False, tracking=True)
    food_allowance = fields.Boolean(string="Food", copy=False, tracking=True)
    housing_allowance = fields.Boolean(string="Housing", copy=False, tracking=True)
    mobile_allowance = fields.Boolean(string="Mobile", copy=False, tracking=True)
    fuel_allowance = fields.Boolean(string="Fuel", copy=False, tracking=True)
    ticket_allowance = fields.Boolean(string="Ticket", copy=False, tracking=True)
    commission_allowance = fields.Boolean(string='Commission', copy=False, tracking=True)
    other_allowance = fields.Boolean(string='Other', copy=False, tracking=True)

    def compute_salary(self, contract):
        salary = contract.wage
        if self.transportation_allowance:
            salary += contract.transportation_allowance
        if self.food_allowance:
            salary += contract.food_allowance
        if self.housing_allowance:
            salary += contract.housing_allowance
        if self.mobile_allowance:
            salary += contract.mobile_allowance
        if self.fuel_allowance:
            salary += contract.fuel_allowance
        if self.ticket_allowance:
            salary += contract.ticket_allowance
        if self.commission_allowance:
            salary += contract.commission_allowance
        if self.other_allowance:
            salary += contract.other_allowance
        return salary
