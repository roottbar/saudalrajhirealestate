# -*- coding: utf-8 -*-
from odoo import models, fields, api

class HrEmployee(models.Model):
    _inherit = 'hr.employee'

    work_location_name = fields.Char(
        string='Work Location Name',
        compute='_compute_work_location_name_type',
        store=True
    )

    @api.depends('work_location_id.name')  # ✅ فقط يعتمد على حقل موجود فعلاً
    def _compute_work_location_name_type(self):
        for rec in self:
            rec.work_location_name = rec.work_location_id.name if rec.work_location_id else ''
