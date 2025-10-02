# -*- coding: utf-8 -*-
from odoo import api, fields, models
from datetime import datetime
from dateutil.relativedelta import relativedelta
import time


class HrPayslip(models.Model):
    _inherit = 'hr.payslip'

    attendance_ded = fields.Float(string='Attendance Month Deduction', compute='compute_attendance_ded')

    @api.depends('employee_id', 'date_from', 'date_to')
    def compute_attendance_ded(self):
        total_ded = 0.0
        for rec in self:
            attendance_ded = self.env['attendance.transaction'].search(
                [('employee_id', '=', rec.employee_id.id), ('date', '>=', rec.date_from),
                 ('date', '<=', rec.date_to)], order='date ASC')
            if attendance_ded:
                for ded in attendance_ded:
                    total_ded += ded.deducted_amount
            rec.attendance_ded = total_ded
