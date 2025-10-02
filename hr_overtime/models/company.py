#!/usr/bin/python
# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import UserError
from calendar import monthrange


class Company(models.Model):
    _inherit = "res.company"

    month_days = fields.Selection([('month_days', 'Month_days'), ('30day', '30 Day'), ], default='30day', required=True)

    def get_month_days(self, data):
        if self.month_days == '30day':
            return 30
        elif self.month_days == 'month_days':
            num_days = monthrange(data.year, data.month)[1]
            return num_days
