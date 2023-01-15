# -*- coding: utf-8 -*-

from odoo import models, fields


class RentRentalWizardInherit(models.TransientModel):
    _inherit = 'rental.wizard'

    duration_unit = fields.Selection([("hour", "Hours"), ("day", "Days"), ("week", "Weeks"), ("month", "Months"), ("year", "years")],
                                     string="Unit", required=True, compute="_compute_duration")
