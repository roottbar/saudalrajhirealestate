# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError, UserError


class HrOvertime(models.Model):
    _name = 'hr.overtime'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = "Overtime Request"

    # @api.model
    # def default_get(self, field_list):
    #     result = super(HrOvertime, self).default_get(field_list)
    #     if result.get('user_id'):
    #         ts_user_id = result['user_id']
    #     else:
    #         ts_user_id = self.env.context.get('user_id', self.env.user.id)
    #     result['employee_id'] = self.env['hr.employee'].search([('user_id', '=', ts_user_id)], limit=1).id
    #     return result

    @api.depends('employee_id')
    def _compute_contract_id(self):
        Contract = self.env['hr.contract']
        for rec in self:
            rec.contract_id = False
            contract_id = Contract.search(
                [('employee_id', '=', rec.employee_id.id), ('state', 'in', ['open', 'trial_period', 'pending'])],
                order='date_start desc', limit=1)
            if contract_id:
                rec.contract_id = contract_id.id

    @api.depends('salary', 'date', 'contract_id')
    def _compute_salary_per_hour(self):
        for rec in self:
            rec.salary_per_hour = False
            if rec.salary and rec.date and rec.contract_id:
                hours_per_day = rec.contract_id.resource_calendar_id.hours_per_day
                month_days = rec.env.user.company_id.get_month_days(rec.date)
                rec.salary_per_hour = rec.salary / month_days / hours_per_day

    @api.depends('type_id', 'date', 'contract_id')
    def _compute_extra_salary_per_hour(self):
        for rec in self:
            rec.extra_salary_per_hour = False
            if rec.type_id and rec.date and rec.contract_id:
                extra_salary = rec.type_id.compute_salary(rec.contract_id)
                hours_per_day = rec.contract_id.resource_calendar_id.hours_per_day
                month_days = rec.env.user.company_id.get_month_days(rec.date)
                rec.extra_salary_per_hour = extra_salary / month_days / hours_per_day

    @api.depends('salary_per_hour', 'extra_salary_per_hour', 'actual_hours_num')
    def _compute_overtime_amount(self):
        for rec in self:
            rec.overtime_amount = False
            if rec.salary_per_hour and rec.extra_salary_per_hour and rec.actual_hours_num:
                rec.overtime_amount = rec.actual_hours_num * (rec.salary_per_hour + 0.5 * rec.extra_salary_per_hour)

    name = fields.Char(string="Overtime Name", default="/", readonly=True, help="Sequence of the overtime Request")
    date = fields.Date(string="Request Date", default=fields.Date.today(), readonly=True)
    date_from = fields.Date('Start Date')
    date_to = fields.Date('End Date')
    employee_id = fields.Many2one('hr.employee', string="Employee", required=True)
    department_id = fields.Many2one('hr.department', related="employee_id.department_id", readonly=True,
                                    string="Department")
    address_id = fields.Many2one('res.partner', related="employee_id.address_id", readonly=True,
                                 string="Work Address")
    employee_no = fields.Char(related="employee_id.employee_no", readonly=True, string="Employee Number")
    contract_id = fields.Many2one('hr.contract', compute="_compute_contract_id", string='Current Contract')
    salary = fields.Float(related="contract_id.gross_wage", compute_sudo=True)
    salary_per_hour = fields.Float(compute="_compute_salary_per_hour")
    type_id = fields.Many2one('hr.overtime.type', string='Overtime Type', required=True)
    extra_salary_per_hour = fields.Float(compute="_compute_extra_salary_per_hour")
    hours_num = fields.Float(string='Number of Hours')
    actual_hours_num = fields.Float(string='Actual Number of Hours')
    overtime_amount = fields.Float(compute="_compute_overtime_amount")
    payslip_paid = fields.Boolean(readonly=True)

    state = fields.Selection([
        ('draft', 'Draft'),
        ('waiting_approval', 'Submitted'),
        ('approved', 'Approved'),
        ('refused', 'Refused'),
        ('cancel', 'Canceled'),
    ], string="State", default='draft', track_visibility='onchange', copy=False, )

    @api.onchange('employee_id', 'contact_id')
    def check_contact(self):
        if self.employee_id and not self.contract_id:
            raise ValidationError(_("%s Has No Running Contact.", self.employee_id.name))

    @api.model
    def create(self, values):
        values['name'] = self.env['ir.sequence'].get('hr.overtime.seq') or ' '
        res = super(HrOvertime, self).create(values)
        return res

    def action_refuse(self):
        return self.write({'state': 'refused'})

    def action_submit(self):
        self.write({'state': 'waiting_approval'})

    def action_cancel(self):
        for rec in self:
            if rec.payslip_paid:
                raise UserError('You cannot Cancel a overtime which is paid in payslip')
            rec.write({'state': 'cancel'})

    def action_set_to_draft(self):
        self.write({'state': 'draft'})

    def action_approve(self):
        self.write({'state': 'approved'})

    def unlink(self):
        for overtime in self:
            if overtime.state not in ('draft', 'cancel'):
                raise UserError('You cannot delete a overtime which is not in draft or cancelled state')
        return super(HrOvertime, self).unlink()
