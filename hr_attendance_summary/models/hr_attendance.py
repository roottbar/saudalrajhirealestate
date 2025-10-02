# -*- coding: utf-8 -*-

from odoo import models, fields, api, _


class HrAttendance(models.Model):
    _inherit = 'hr.attendance'

    date = fields.Date(compute="_compute_date", store=True)

    @api.depends('check_in')
    def _compute_date(self):
        for rec in self:
            rec.date = rec.check_in.date()
