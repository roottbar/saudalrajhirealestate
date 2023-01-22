# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError, UserError

from dateutil.relativedelta import relativedelta


class LateRule(models.Model):
    _name = 'late.rule'
    _description = "Late Rules"

    def _get_dafault_salary_rule_id(self):
        self.salary_rule_id = self.env.ref('hr_attendance_summary.hr_rule_attendance_late').id

    salary_input_code = fields.Char(default='LAT', required=True)
    sequence = fields.Integer(default=1, required=True)
    type = fields.Selection([("check_in", "Check-In"), ("check_out", "Check-Out")], default='check_in', required=True)
    sequence_range = fields.Selection([("month", "Month"), ("year", "Year")], string="End Sequence Every",
                                      default='month', required=True)
    from_minute = fields.Float(default=0, required=True)
    to_minute = fields.Float(default=1, required=True)
    rule_lines = fields.One2many('late.rule.line', 'rule_id', string='Rules')
    salary_rule_id = fields.Many2one('hr.salary.rule', compute=_get_dafault_salary_rule_id, readonly=1)

    def name_get(self):
        result = []
        for rec in self:

            if rec.type == 'check_in':
                type = "Check-in"
            else:
                type = "Check-Out"

            from_minute = '{0:02.0f}:{1:02.0f}'.format(*divmod(rec.from_minute * 60, 60))
            to_minute = '{0:02.0f}:{1:02.0f}'.format(*divmod(rec.to_minute * 60, 60))
            name = "%s [%s - %s]" % (type, from_minute, to_minute)
            result.append((rec.id, name))
        return result

    def get_date_range(self, date):
        if self.sequence_range == 'month':
            date_from = date.replace(day=1)
            date_to = (date + relativedelta(months=+1, day=1, days=-1))
        elif self.sequence_range == 'year':
            date_from = (date + relativedelta(day=1, month=1))
            date_to = (date + relativedelta(years=+1, day=1, month=1, days=-1))

        return date_from, date_to


class LateRuleLine(models.Model):
    _name = 'late.rule.line'
    _description = "Late Rules line"

    rule_id = fields.Many2one('late.rule', string='Rule', ondelete='cascade')
    sequence = fields.Integer(default=1, required=True)
    penalty_percent = fields.Integer(string="Penalty Percent (%)", default=1, required=True)
    late_minutes_deduction = fields.Boolean()
    send_warning_email = fields.Boolean()
    mail_template_id = fields.Many2one("mail.template", string="Email Template",
                                       domain=[("model", "=", "late.rule")])
