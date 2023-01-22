# -*- coding: utf-8 -*-
from datetime import date, datetime
from dateutil.relativedelta import relativedelta
from pytz import timezone, UTC, utc
from odoo.tools import format_datetime
from odoo.tools import format_time
from odoo import api, fields, models, _
from odoo.exceptions import UserError
from odoo.osv import expression
from odoo.addons.resource.models.resource import float_to_time, HOURS_PER_DAY


class HrAttendanceBatchLine(models.Model):
    _name = 'hr.attendance.batch.line'

    attendance_batch_id = fields.Many2one('hr.attendance.batch', ondelete='cascade')
    employee_id = fields.Many2one('hr.employee', string='Employee', required=True)
    check_in_date = fields.Date(related='attendance_batch_id.check_in')
    check_in = fields.Datetime(required=True, compute="_compute_check_times", readonly="0")
    check_out = fields.Datetime(required=True)
    worked_hours = fields.Float(required=True)
    notes = fields.Char(string="Notes")
    attendance_id = fields.Many2one('hr.attendance', 'Attendance')

    @api.depends('worked_hours', 'check_out')
    def _compute_check_times(self):
        for rec in self:
            rec.check_in = False
            if rec.worked_hours and rec.check_out:
                if rec.worked_hours < 0:
                    raise UserError(_("Number of hours must be greater than or equal zero"))
                rec.check_in = rec.check_out - relativedelta(hours=rec.worked_hours)

    def get_weekday_id(self, day):
        if day == 'Monday':
            return 0
        if day == 'Tuesday':
            return 1
        if day == 'Wednesday':
            return 2
        if day == 'Thursday':
            return 3
        if day == 'Friday':
            return 4
        if day == 'Saturday':
            return 5
        if day == 'Sunday':
            return 6

    @api.onchange('employee_id', 'check_in_date')
    def onchange_employee_id(self):
        for rec in self:
            if rec.employee_id and rec.check_in_date:
                dayofweek = rec.get_weekday_id(datetime.strftime(rec.check_in_date, '%A'))
                calendar_hour_from = self.env['resource.calendar.attendance'].search(
                    [('calendar_id', '=', rec.employee_id.contract_id.resource_calendar_id.id),
                     ('dayofweek', '=', dayofweek)], order="hour_from", limit=1)
                calendar_hour_to = self.env['resource.calendar.attendance'].search(
                    [('calendar_id', '=', rec.employee_id.contract_id.resource_calendar_id.id),
                     ('dayofweek', '=', dayofweek)], order="hour_to desc", limit=1)

                if calendar_hour_from and calendar_hour_from:
                    tz = rec.employee_id.tz or 'UTC'
                    hour_from = float_to_time(calendar_hour_from.hour_from)
                    hour_to = float_to_time(calendar_hour_to.hour_to)
                    rec.check_in = timezone(tz).localize(datetime.combine(rec.check_in_date, hour_from)).astimezone(
                        UTC).replace(tzinfo=None)
                    rec.check_out = timezone(tz).localize(datetime.combine(rec.check_in_date, hour_to)).astimezone(
                        UTC).replace(tzinfo=None)
                    rec.worked_hours = rec.employee_id.contract_id.resource_calendar_id.hours_per_day
                else:
                    rec.unlink()
