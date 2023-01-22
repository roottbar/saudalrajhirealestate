# -*- coding: utf-8 -*-
import babel
import time
from datetime import datetime

from odoo import models, fields, api, tools, _
from odoo.exceptions import AccessError, UserError, AccessDenied


class HrPayslipInput(models.Model):
    _inherit = 'hr.payslip.input'

    leave_id = fields.Many2one('hr.leave', string="Leave")


class HrPayslip(models.Model):
    _inherit = 'hr.payslip'

    housing_allowance = fields.Monetary(compute='_compute_allowances')
    other_earnings = fields.Monetary(compute='_get_other_earnings', string="Other Earnings")
    other_deductions = fields.Monetary(compute='_get_other_deductions', string="Total Deductions")

    def _compute_allowances(self):
        for payslip in self:
            payslip.housing_allowance = payslip._get_salary_line_total('Housing')

    def _get_other_earnings(self):
        lines = self.line_ids.filtered(lambda line: line.category_id.code == 'ALW' and line.code != 'Housing')
        self.other_earnings = sum([line.total for line in lines])

    def _get_other_deductions(self):
        lines = self.line_ids.filtered(lambda line: line.category_id.code == 'DED')
        self.other_deductions = sum([line.total for line in lines])

    @api.onchange('employee_id', 'date_from', 'date_to')
    def onchange_employee1(self):
        employee = self.employee_id
        date_from = self.date_from
        date_to = self.date_to

        if not self.env.context.get('contract') or not self.contract_id:
            contracts = employee._get_contracts(date_from, date_to)

            if not contracts:
                return
            self.contract_id = contracts[0]

        self.input_line_ids = self.get_travel_inputs(contracts, date_from, date_to)

    def get_travel_inputs(self, contract_ids, date_from, date_to):
        """This Compute the other inputs to employee payslip."""
        self.ensure_one()
        res = []
        if contract_ids[0].travel_value > 0:
            contract_obj = self.env['hr.contract']
            emp_id = contract_obj.browse(contract_ids[0].id).employee_id
            leaves = self.env['hr.leave'].search([('employee_id', '=', emp_id.id), ('state', '=', 'validate')])
            for l in leaves:
                # if (date_from <= l.request_date_from <= date_to and not l.is_travel_done) and (not self.input_line_ids.filtered(lambda i: i.leave_id.id == l.id)):
                if (not l.is_travel_done) and (not self.input_line_ids.filtered(lambda i: i.leave_id.id == l.id)):
                    vals = {
                        'input_type_id': self.env.ref('bstt_hr.hr_rule_input_travel').id,
                        'code': 'Travel',
                        'amount': contract_ids[0].travel_value,
                        'leave_id': l.id,
                    }
                    res.append((0, 0, vals))
        return res

    def action_payslip_done(self):
        for line in self.input_line_ids:
            if line.leave_id:
                line.leave_id.is_travel_done = True
        return super(HrPayslip, self).action_payslip_done()

    def action_payslip_cancel(self):
        if not self.env.user._is_system() and self.filtered(lambda slip: slip.state == 'done'):
            raise UserError(_("Cannot cancel a payslip that is done."))
        self.write({'state': 'cancel'})
        self.mapped('payslip_run_id').action_close()

