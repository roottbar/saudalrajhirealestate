# -*- coding: utf-8 -*-
from datetime import date, datetime
from odoo import models, fields, api, _
from odoo.exceptions import UserError
from dateutil.relativedelta import relativedelta


class UpdateAttendanceSummary(models.TransientModel):
    _name = "update.attendance.summary"
    _description = "Update Attendance Summary"

    employee_ids = fields.Many2many('hr.employee', string='Employees')
    date_from = fields.Date(string='Start Date', required=True,
                            default=lambda self: fields.Date.to_string(date.today().replace(day=1)), )
    date_to = fields.Date(string='End Date', required=True,
                          default=lambda self: fields.Date.to_string(
                              (datetime.now() + relativedelta(months=+1, day=1, days=-1)).date()), )
    delete_old_records = fields.Boolean()

    @api.onchange('date_to', 'date_from')
    def onchange_date_to(self):
        if self.date_from and self.date_to and self.date_to < self.date_from:
            raise UserError(_('End date must be greater than start date!'))

    def caret_attendance_summary(self, employee, date, attendances=False):
        summary = self.env['hr.attendance.summary'].create({'employee_id': employee.id, 'date': date})
        for attendance in attendances:
            self.env['hr.attendance.summary.line'].create({
                'summary_id': summary.id,
                'check_in': attendance.check_in,
                'check_out': attendance.check_out
            })
        summary.compute_status()

    def action_update(self):
        """group employee attendance by date and add them in one attendance summary"""
        employees = self.employee_ids

        if not self.employee_ids:
            employees = self.env['hr.employee'].search([])

        # flush old attendance summary
        old_attendance = self.env['hr.attendance.summary'].search(
            [('employee_id', 'in', employees.ids), ('date', '>=', self.date_from), ('date', '<=', self.date_to)])
        old_attendance.unlink()

        attendances = self.env['hr.attendance'].search(
            [('employee_id', 'in', employees.ids), ('date', '>=', self.date_from), ('date', '<=', self.date_to)],
            order='check_in')

        for employee in employees:
            emp_attendances = attendances.filtered(lambda a: a.employee_id.id == employee.id)
            date_from = self.date_from
            while date_from <= self.date_to:
                date_attendances = emp_attendances.filtered(lambda a: a.date == date_from)
                self.caret_attendance_summary(employee, date_from, date_attendances)
                date_from += relativedelta(days=1)
