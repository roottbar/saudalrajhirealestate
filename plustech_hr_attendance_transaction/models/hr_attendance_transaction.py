# -*- coding: utf-8 -*-

##############################################################################
#
#
#    Copyright (C) 2020-TODAY .
#    Author: Eng.Hassan Abdallah
#
#    It is forbidden to publish, distribute, sublicense, or sell copies
#    of the Software or modified copies of the Software.
#
##############################################################################

from datetime import datetime, date, timedelta, time
from dateutil.relativedelta import relativedelta
from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError
from odoo.addons.resource.models.resource import float_to_time, HOURS_PER_DAY, \
    make_aware, datetime_to_string, string_to_datetime
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT, DEFAULT_SERVER_DATE_FORMAT
import pytz

DATETIME_FORMAT = "%Y-%m-%d %H:%M:%S"
TIME_FORMAT = "%H:%M:%S"


class AttendanceTransaction(models.Model):
    _name = 'attendance.transaction'
    _description = 'Hr Attendance Transaction'
    _order = 'id desc'

    employee_id = fields.Many2one(comodel_name='hr.employee', string='Employee',
                                  required=True)
    attendance_id = fields.Many2one('hr.attendance')
    department_id = fields.Many2one(related='employee_id.department_id',
                                    string='Department', store=True)
    date = fields.Date("Date")
    atten_date = fields.Date("Atten Date")
    day = fields.Selection([
        ('0', 'Monday'),
        ('1', 'Tuesday'),
        ('2', 'Wednesday'),
        ('3', 'Thursday'),
        ('4', 'Friday'),
        ('5', 'Saturday'),
        ('6', 'Sunday')
    ], 'Day of Week', required=True, index=True, )
    pl_sign_in = fields.Float("Planned sign in", readonly=True)
    pl_sign_out = fields.Float("Planned sign out", readonly=True)
    pl_hours = fields.Float("Working Hours", compute="compute_working_hours", store=True, readonly=True)
    worked_hours = fields.Float("Worked Hours", compute="compute_working_hours", store=True, readonly=True)
    ac_sign_in = fields.Float("Actual sign in", readonly=True)
    ac_sign_out = fields.Float("Actual sign out", readonly=True)
    overtime = fields.Float("Overtime", readonly=True, compute='compute_check_diff')
    overtime_amount = fields.Float("Overtime Amount", readonly=True, compute='compute_check_diff')
    late_in = fields.Float("Early late", readonly=True, compute='_compute_early_late', store=True)
    diff_time = fields.Float("Diff Time", compute="_compute_diff_time", store=True,
                             help="Difference between the working time and attendance time(s) ",
                             readonly=True)
    deducted_amount = fields.Float(compute="_compute_deducted_amount", readonly=True, store=True)
    early_exit = fields.Float("Early Exit", readonly=True, compute='_compute_early_exit', store=True)

    status = fields.Selection(string="Status",
                              selection=[('ex', 'Exist'),
                                         ('ab', 'Absence'),
                                         ('weekend', 'Week End'),
                                         ('ph', 'Public Holiday'),
                                         ('leave', 'Leave'),
                                         ('dep', 'Deputation'), ],
                              required=False, readonly=True)
    company_id = fields.Many2one('res.company', 'Company', default=lambda self: self.env.user.company_id)

    @api.model
    def _get_attendance_transaction(self):
        attendance_transaction = self.env['attendance.transaction']
        employee_obj = self.env['hr.employee'].search([])
        today = fields.Date.today()
        now = datetime.now()
        for emp in employee_obj:
            dayofweek = str(today.weekday())
            attendance_ids = emp.resource_calendar_id.attendance_ids.filtered(lambda line: line.dayofweek == dayofweek)
            status = 'ab'
            attendance = self.env['hr.attendance'].search(
                [('employee_id', '=', emp.id), ('is_taken', '=', False)], order='check_in desc')
            for atten in attendance:
                tzinfo = pytz.timezone(atten.employee_id.tz)
                transaction = attendance_transaction.search(
                    [('employee_id', '=', emp.id), ('attendance_id', '=', atten.id)])
                ac_sign_in = 0
                ac_sign_out = 0
                if atten:
                    check_in = atten.check_in.astimezone(tzinfo)
                    ac_sign_in = str(check_in.hour) + '.' + str(check_in.minute)
                    status = 'ex'
                if atten.check_out:
                    check_out = atten.check_out.astimezone(tzinfo)
                    ac_sign_out = str(check_out.hour) + '.' + str(check_out.minute)

                if len(transaction) == 0:
                    attendance_transaction.create({
                        'date': atten.atten_date,
                        'atten_date': atten.atten_date,
                        'employee_id': emp.id,
                        'attendance_id': atten.id,
                        'day': str(atten.atten_date.weekday()),
                        'ac_sign_in': ac_sign_in,
                        'ac_sign_out': ac_sign_out,
                        'pl_sign_in': attendance_ids[0].hour_from,
                        'pl_sign_out': attendance_ids[0].hour_to,
                        'status': status
                    })
                elif len(transaction) > 0:
                    transaction.write({
                        'ac_sign_out': ac_sign_out,
                        'status': status
                    })
                if atten.check_out:
                    atten.write({'is_taken': True, })
            today_checkin = self.env['hr.attendance'].search(
                [('employee_id', '=', emp.id), ('atten_date', '=', today)], order='check_out asc')
            today_trans = attendance_transaction.search([('employee_id', '=', emp.id), ('date', '=', today)], limit=1)
            if len(today_checkin) == 0 and len(today_trans) == 0:
                status = 'ab'
                holiday = self.get_public_holiday(now, emp)
                if len(holiday) > 0:
                    status = 'ph'
                leaves = self._get_emp_leave_intervals(emp, today)
                if len(leaves) > 0:
                    status = 'leave'
                if self._get_weekend_days(emp, today):
                    status = 'weekend'
                attendance_transaction.create({
                    'date': today,
                    'employee_id': emp.id,
                    'day': dayofweek,
                    'ac_sign_in': 0,
                    'ac_sign_out': 0,
                    'pl_sign_in': attendance_ids[0].check_in_start if attendance_ids else 0.0,
                    'pl_sign_out': attendance_ids[0].check_out_start if attendance_ids else 0.0,
                    'status': status
                })

    def _get_emp_leave_intervals(self, emp, start_datetime=None):
        start_datetime = datetime.combine(start_datetime, datetime.min.time())
        leaves = []
        leave_obj = self.env['hr.leave']
        leave_ids = leave_obj.search([
            ('employee_id', '=', emp.id),
            ('state', '=', 'validate'),
            ('date_from', '<', start_datetime),
            ('date_to', '>', start_datetime)
        ])

        for leave in leave_ids:
            leaves.append((leave.date_from, leave.date_to))
        return leaves

    def get_public_holiday(self, date, emp):
        calendar_id = emp.contract_id.resource_calendar_id
        holiday = calendar_id.global_leave_ids.filtered(lambda line: line.date_from <= date and line.date_to >= date)
        return holiday

    def _get_weekend_days(self, employee_id, date):
        weekend = False
        Working_Hours = employee_id.resource_calendar_id
        attendance = Working_Hours.attendance_ids
        work_day = []
        for attend in attendance:
            if attend.dayofweek not in work_day:
                work_day.append(attend.dayofweek)
        if str(date.weekday()) not in work_day:
            weekend = True
        return weekend

    @api.depends('pl_sign_in', 'ac_sign_in')
    def _compute_early_late(self):
        for rec in self:
            if rec.pl_sign_in and rec.ac_sign_in:
                rec.late_in = rec.ac_sign_in - rec.pl_sign_in

    @api.depends('pl_sign_out', 'ac_sign_out')
    def _compute_early_exit(self):
        for rec in self:
            if rec.pl_sign_out and rec.ac_sign_out:
                rec.early_exit = rec.ac_sign_out - rec.pl_sign_out

    @api.depends('late_in', 'early_exit')
    def _compute_diff_time(self):
        for rec in self:
            if rec.late_in or rec.early_exit:
                rec.diff_time = rec.late_in + rec.early_exit
            elif not rec.ac_sign_in:
                rec.diff_time = -(rec.pl_hours)

    @api.depends('ac_sign_in', 'ac_sign_out')
    def compute_working_hours(self):
        for rec in self:
            if rec.ac_sign_in and rec.ac_sign_out:
                rec.worked_hours = rec.ac_sign_out - rec.ac_sign_in
            if rec.pl_sign_in and rec.pl_sign_out:
                rec.pl_hours = rec.pl_sign_out - rec.pl_sign_in

    @api.depends('diff_time', 'late_in', 'early_exit')
    def _compute_deducted_amount(self):
        for rec in self:
            schedule_id = rec.employee_id.resource_calendar_id
            if rec.late_in or rec.early_exit:
                late_in_deduct = (rec.late_in % 60) * schedule_id.check_in_minute
                early_exit_deduct = (rec.early_exit % 60) * schedule_id.check_out_minute
                rec.deducted_amount = abs(late_in_deduct + early_exit_deduct)
            elif rec.diff_time:
                wage = rec.employee_id.contract_id.wage
                rec.deducted_amount = wage / rec.employee_id.resource_calendar_id.month_work_days

    @api.depends('employee_id', 'ac_sign_in', 'ac_sign_out')
    def compute_check_diff(self):

        for rec in self:
            rec.overtime_amount=0.0
            rec.overtime = 0.0
            if rec.employee_id and rec.ac_sign_in:
                check_in_ot_diff = 0.0
                check_out_ot_diff = 0.0
                check_in_diff = 0.0
                check_out_diff = 0.0
                wage_minute = 0.0
                check_out = False
                schedule_check_in = False
                schedule_check_out = False
                work_days = []
                schedule_id = False
                wage = rec.employee_id.contract_id.wage
                attendance_date = datetime.strptime(str(rec.attendance_id.atten_date),
                                                    DEFAULT_SERVER_DATE_FORMAT).date()
                attendance_ids = self.env['hr.attendance'].search([('atten_date', '=', attendance_date)],
                                                                  order='check_in ASC')
                if attendance_ids:
                    if rec.ac_sign_in != attendance_ids[0].check_in:
                        schedule_id = self.env['resource.calendar.attendance'].search(
                            [('calendar_id', '=', rec.employee_id.resource_calendar_id.id),
                             ('dayofweek', '=', str(attendance_date.weekday()))]
                            , order='hour_from DESC', limit=1)
                    else:
                        schedule_id = self.env['resource.calendar.attendance'].search(
                            [('calendar_id', '=', rec.employee_id.resource_calendar_id.id),
                             ('dayofweek', '=', str(attendance_date.weekday()))]
                            , order='hour_from ASC', limit=1)
                else:
                    schedule_id = self.env['resource.calendar.attendance'].search(
                        [('calendar_id', '=', rec.employee_id.resource_calendar_id.id),
                         ('dayofweek', '=', str(attendance_date.weekday()))]
                        , order='hour_from ASC', limit=1)
                atten_date = datetime.combine(rec.atten_date, datetime.min.time())
                ac_sign_in = atten_date + timedelta(hours=rec.ac_sign_in)
                check_in_date = datetime.strptime(str(ac_sign_in), DEFAULT_SERVER_DATETIME_FORMAT).date()
                check_in = datetime.strptime(str(ac_sign_in), DEFAULT_SERVER_DATETIME_FORMAT) + relativedelta(
                    hours=3)
                if schedule_id:
                    wage_minute = wage / (schedule_id.calendar_id.month_work_days * schedule_id.calendar_id.work_hours)
                    schedule_start_in = str(check_in_date) + ' ' + schedule_id.check_in_start_str
                    schedule_check_in = str(check_in_date) + ' ' + schedule_id.check_in_str
                    schedule_end_in = str(check_in_date) + ' ' + schedule_id.check_in_end_str
                    schedule_check_in = datetime.strptime(schedule_check_in, DEFAULT_SERVER_DATETIME_FORMAT)
                    schedule_start_in = datetime.strptime(schedule_start_in, DEFAULT_SERVER_DATETIME_FORMAT)
                    schedule_end_in = datetime.strptime(schedule_end_in, DEFAULT_SERVER_DATETIME_FORMAT)

                    if schedule_id.calendar_id.attendance_ids:
                        for attendance in schedule_id:
                            work_days.append(str(attendance.dayofweek))

                if schedule_id and rec.ac_sign_in:
                    if check_in < schedule_start_in:
                        if schedule_id.calendar_id.check_in_early == 'yes':
                            check_in_ot_diff = ((schedule_start_in - check_in).total_seconds() / 60)
                            if check_in_ot_diff < float(schedule_id.calendar_id.min_ot_check_in):
                                check_in_ot_diff = 0.0

                if rec.ac_sign_out and schedule_id:
                    atten_date = datetime.combine(rec.atten_date, datetime.min.time())
                    ac_sign_out = atten_date + timedelta(hours=rec.ac_sign_out)
                    check_out = datetime.strptime(str(ac_sign_out), DEFAULT_SERVER_DATETIME_FORMAT) + relativedelta(
                        hours=3)
                    # schedule_check_out = str(check_out_date) + ' ' + schedule_id.check_out_str
                    # schedule_check_out = datetime.strptime(schedule_check_out, DEFAULT_SERVER_DATETIME_FORMAT)
                    # schedule_start_out = str(check_out_date) + ' ' + schedule_id.check_out_start_str
                    schedule_end_out = str(atten_date.date()) + ' ' + schedule_id.check_out_end_str
                    # schedule_start_out = datetime.strptime(schedule_start_out, DEFAULT_SERVER_DATETIME_FORMAT)
                    schedule_end_out = datetime.strptime(schedule_end_out, DEFAULT_SERVER_DATETIME_FORMAT)

                    if check_out > schedule_end_out:
                        if schedule_id.calendar_id.check_out_delay == 'yes':
                            check_out_ot_diff = (check_out - schedule_end_out).total_seconds() / 3600
                            if (check_out_ot_diff * 60) < schedule_id.calendar_id.min_ot_check_out:
                                check_out_ot_diff = 0.0
                if check_in_ot_diff >= 0.0 and check_out_ot_diff >= 0.0:
                    minute_wage = rec.employee_id.contract_id.over_hour / 60
                    if str(check_in_date.weekday()) in work_days:
                        rec.overtime = (check_in_ot_diff * schedule_id.calendar_id.ot_working_day) + \
                                       (check_out_ot_diff * schedule_id.calendar_id.ot_working_day)
                        rec.overtime_amount = (
                                                      check_in_ot_diff * minute_wage * schedule_id.calendar_id.ot_working_day) + \
                                              (check_out_ot_diff * minute_wage * schedule_id.calendar_id.ot_working_day)
                    if str(check_in_date.weekday()) not in work_days:
                        rec.overtime = (check_in_ot_diff * schedule_id.calendar_id.ot_holiday) + \
                                       (check_out_ot_diff * schedule_id.calendar_id.ot_holiday)
                        rec.overtime_amount = (check_in_ot_diff * minute_wage * schedule_id.calendar_id.ot_holiday) + \
                                              (check_out_ot_diff * minute_wage * schedule_id.calendar_id.ot_holiday)


class HrAttendance(models.Model):
    _inherit = 'hr.attendance'
    atten_date = fields.Date(compute='_get_attendance', store=True)
    is_taken = fields.Boolean()

    @api.depends('check_in')
    def _get_attendance(self):
        for rec in self:
            rec.atten_date = rec.check_in.strftime('%Y-%m-%d')
