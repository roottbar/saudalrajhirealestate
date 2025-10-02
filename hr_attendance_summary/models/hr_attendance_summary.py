# -*- coding: utf-8 -*-
from pytz import timezone, UTC, utc
from odoo.addons.resource.models.resource import float_to_time, HOURS_PER_DAY

from datetime import datetime, timedelta
from odoo import models, fields, api, _
from odoo.exceptions import ValidationError, UserError


class HrAttendanceSummary(models.Model):
    _name = 'hr.attendance.summary'
    _description = "Attendance Summary"

    employee_id = fields.Many2one('hr.employee', string='Employee', required=True, ondelete='cascade')
    date = fields.Date(required=True)
    late_in = fields.Float(compute="_compute_late_lines_values")
    early_out = fields.Float(compute="_compute_late_lines_values")
    total_late = fields.Float(compute="_compute_late_lines_values")
    rule_ids = fields.Many2many('late.rule', string='Lating Rules', compute="_compute_rule_ids")
    payslip_paid = fields.Boolean()
    exception = fields.Boolean()
    exception_reason = fields.Char()
    attendance_ids = fields.One2many('hr.attendance.summary.line', 'summary_id', string='Attendances')
    late_lines = fields.One2many('hr.attendance.summary.late.line', 'summary_id', string='Late Lines')
    contract_id = fields.Many2one('hr.contract', related='employee_id.contract_id', string='Current Contract')
    wage_day = fields.Float(related='contract_id.wage_day')
    resource_calendar_id = fields.Many2one('resource.calendar', 'Working Schedule',
                                           related='contract_id.resource_calendar_id')
    weekday = fields.Selection([
        ('0', 'Monday'),
        ('1', 'Tuesday'),
        ('2', 'Wednesday'),
        ('3', 'Thursday'),
        ('4', 'Friday'),
        ('5', 'Saturday'),
        ('6', 'Sunday')], string='Day Of The Week', compute='_compute_weekday', readonly=False)
    state = fields.Selection([
        ('attendance', 'Attendance'),
        ('absence', 'Absence'),
        ('weekend', 'Weekend'),
        ('holiday', 'Holiday'),
    ], string='Status',
        default='absence')

    @api.depends('late_lines')
    def _compute_late_lines_values(self):
        for rec in self:
            rec.late_in, rec.early_out, rec.total_late = 0, 0, 0
            if rec.late_lines:
                rec.late_in = sum([l.late_value for l in rec.late_lines.filtered(lambda x: x.type == 'check_in')])
                rec.early_out = sum([l.late_value for l in rec.late_lines.filtered(lambda x: x.type == 'check_out')])
                rec.total_late = rec.late_in + rec.early_out

    @api.depends('date')
    def _compute_weekday(self):
        for rec in self:
            rec.weekday = str(rec.date.weekday())

    @api.depends('late_lines')
    def _compute_rule_ids(self):
        for rec in self:
            rec.rule_ids = False
            if rec.late_lines:
                rec.rule_ids = rec.late_lines.mapped('rule_id').ids

    def name_get(self):
        result = []
        for rec in self:
            name = "%s - %s" % (rec.employee_id.name, rec.date)
            result.append((rec.id, name))
        return result

    def get_attendance_status(self):

        if self.attendance_ids:
            return 'attendance'

        weekday = self.date.weekday()
        shifts = self.resource_calendar_id.attendance_ids.filtered(lambda x: x.dayofweek == str(weekday))
        if not shifts:
            return 'weekend'

        holidays = self.env['hr.leave'].sudo().search([
            ('employee_id', '=', self.employee_id.id),
            ('state', '=', 'validate'),
            ('date_from', '<=', self.date),
            ('date_to', '>=', self.date),
        ])

        if holidays:
            return 'holiday'

        return 'absence'

    def compute_status(self):
        """
        compute late values
        """
        # flush late table
        self.late_lines = False

        self.state = self.get_attendance_status()

        if not self.attendance_ids or not self.contract_id or not self.resource_calendar_id:
            return
        # get employee shifts depend on attendance date
        weekday = self.date.weekday()
        shifts = self.resource_calendar_id.attendance_ids.filtered(lambda x: x.dayofweek == str(weekday))
        if not shifts or not self.resource_calendar_id.late_rule_ids:
            return
        # check late for each shift
        for shift in shifts:
            tz = self.employee_id.tz or 'UTC'
            hour_from = float_to_time(shift.hour_from)
            hour_to = float_to_time(shift.hour_to)

            shift_start = timezone(tz).localize(datetime.combine(self.date, hour_from)).astimezone(
                UTC).replace(tzinfo=None)
            shift_end = timezone(tz).localize(datetime.combine(self.date, hour_to)).astimezone(
                UTC).replace(tzinfo=None)

            # check in late rules

            if self.attendance_ids.filtered(lambda a: a.check_in <= shift_start and a.check_out >= shift_start):
                continue

            attendance_ids = self.attendance_ids.filtered(lambda a: a.check_in > shift_start).sorted(key='check_in')
            if not attendance_ids:
                continue

            diff = attendance_ids[0].check_in - shift_start
            diff_minutes = diff.total_seconds() / 60

            self.check_late_rule(diff_minutes, type='check_in')

            # check out late rules

            if self.attendance_ids.filtered(lambda a: a.check_in <= shift_end and a.check_out >= shift_end):
                continue

            attendance_ids = self.attendance_ids.filtered(lambda a: a.check_out)
            attendance_ids = attendance_ids.filtered(lambda a: a.check_out < shift_end).sorted(key='check_out',
                                                                                               reverse=True)
            if not attendance_ids:
                continue

            diff = shift_end - attendance_ids[0].check_out
            diff_minutes = diff.total_seconds() / 60

            self.check_late_rule(diff_minutes, type='check_out')

    def check_late_rule(self, diff_minutes, type):

        rule = self.get_late_rule(self.resource_calendar_id.late_rule_ids, diff_minutes, type)

        if not rule or not rule.rule_lines:
            return

        rule_line = self.get_rule_sequence(rule, self.employee_id, self.date)

        self.env['hr.attendance.summary.late.line'].create({
            'summary_id': self.id,
            'rule_id': rule.id,
            'rule_line_id': rule_line.id,
            'late_minutes': diff_minutes
        })

    def get_rule_sequence(self, rule, employee_id, date):
        date_from, date_to = rule.get_date_range(date)
        late_attendances = self.search_count(
            [('employee_id', '=', employee_id.id), ('rule_ids', 'in', rule.id), ('date', '>=', date_from),
             ('date', '<=', date_to)])
        late_attendances += 1
        rule_line = rule.rule_lines.filtered(lambda l: l.sequence == late_attendances)
        if not rule_line:
            rule_line = rule.rule_lines.sorted(key='sequence', reverse=True)[0]
        return rule_line

    def get_late_rule(self, rules, diff_minutes, type):
        rules = rules.search([('type', '=', type)], order='from_minute desc,sequence desc')
        if not rules:
            return False

        rule = rules.filtered(lambda r: r.from_minute * 60 <= diff_minutes <= r.to_minute * 60)
        if not rule:
            rule = rules[0]

        return rule


class HrAttendanceSummaryLine(models.Model):
    _name = 'hr.attendance.summary.line'
    _description = "Attendance Summary Line"

    summary_id = fields.Many2one('hr.attendance.summary', string='Attendance Summary', ondelete='cascade')
    check_in = fields.Datetime()
    check_out = fields.Datetime()


class HrAttendanceSummaryLateLine(models.Model):
    _name = 'hr.attendance.summary.late.line'
    _description = "Attendance Summary Late Line"

    summary_id = fields.Many2one('hr.attendance.summary', string='Attendance Summary', ondelete='cascade')
    rule_id = fields.Many2one('late.rule', string='Lating Rule')
    type = fields.Selection([("check_in", "Check-In"), ("check_out", "Check-Out")], related='rule_id.type')
    rule_line_id = fields.Many2one('late.rule.line', string='Rule Line')
    sequence = fields.Integer(default=1, related='rule_line_id.sequence')
    penalty_percent = fields.Integer(string="Penalty Percent (%)", related='rule_line_id.penalty_percent')
    late_minutes_deduction = fields.Boolean(related='rule_line_id.late_minutes_deduction')
    late_minutes = fields.Float()
    late_value = fields.Float(compute='_compute_late_value')

    @api.depends('late_minutes', 'rule_line_id')
    def _compute_late_value(self):
        for rec in self:
            rec.late_value = 0
            if rec.summary_id.contract_id and rec.summary_id.resource_calendar_id:
                wage_day = rec.summary_id.wage_day
                late_value = wage_day * (rec.penalty_percent / 100)
                if rec.late_minutes_deduction:
                    wage_minutes = wage_day / rec.summary_id.resource_calendar_id.hours_per_day / 60
                    rec.late_value += wage_minutes * rec.late_minutes
                rec.late_value = late_value
