# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError
from odoo.tools import float_compare, float_is_zero
import logging


class HrSalaryRule(models.Model):
    _inherit = 'hr.salary.rule'

    account_analytic_type = fields.Selection([('debit', 'Debit'), ('credit', 'Credit')], string="وضع الحساب التحليلي")


class HrPayslip(models.Model):
    _inherit = 'hr.payslip'

    def _prepare_line_values(self, line, account_id, date, debit, credit, analytic):
        return {
            'name': line.name,
            'partner_id': line.partner_id.id,
            'account_id': account_id,
            'journal_id': line.slip_id.struct_id.journal_id.id,
            'date': date,
            'debit': debit,
            'credit': credit,
            'analytic_account_id': analytic,
            # 'analytic_account_id': line.salary_rule_id.analytic_account_id.id or line.slip_id.contract_id.analytic_account_id.id,
        }

    def _prepare_slip_lines(self, date, line_ids):
        self.ensure_one()
        precision = self.env['decimal.precision'].precision_get('Payroll')
        new_lines = []
        for line in self.line_ids.filtered(lambda line: line.category_id):
            amount = -line.total if self.credit_note else line.total
            if line.code == 'NET': # Check if the line is the 'Net Salary'.
                for tmp_line in self.line_ids.filtered(lambda line: line.category_id):
                    if tmp_line.salary_rule_id.not_computed_in_net: # Check if the rule must be computed in the 'Net Salary' or not.
                        if amount > 0:
                            amount -= abs(tmp_line.total)
                        elif amount < 0:
                            amount += abs(tmp_line.total)
            if float_is_zero(amount, precision_digits=precision):
                continue
            debit_account_id = line.salary_rule_id.account_debit.id
            credit_account_id = line.salary_rule_id.account_credit.id

            if debit_account_id: # If the rule has a debit account.

                # Shaimaa Analytic Account Modifications
                if line.salary_rule_id.account_analytic_type and line.salary_rule_id.account_analytic_type == 'debit':
                    cost_center_analytic = line.salary_rule_id.analytic_account_id.id or line.slip_id.contract_id.analytic_account_id.id
                else:
                    cost_center_analytic = False
                ##########################################

                debit = amount if amount > 0.0 else 0.0
                credit = -amount if amount < 0.0 else 0.0
                # edited by shaimaa
                # debit_line = self._get_existing_lines(
                #     line_ids + new_lines, line, debit_account_id, debit, credit)
                #
                # if not debit_line:
                debit_line = self._prepare_line_values(line, debit_account_id, date, debit, credit, cost_center_analytic)
                new_lines.append(debit_line)
                # else:
                #     debit_line['debit'] += debit
                #     debit_line['credit'] += credit

            if credit_account_id: # If the rule has a credit account.

                # Shaimaa Analytic Account Modifications
                if line.salary_rule_id.account_analytic_type and line.salary_rule_id.account_analytic_type == 'credit':
                    cost_center_analytic = line.salary_rule_id.analytic_account_id.id or line.slip_id.contract_id.analytic_account_id.id
                else:
                    cost_center_analytic = False
                ##########################################

                debit = -amount if amount < 0.0 else 0.0
                credit = amount if amount > 0.0 else 0.0

                # edited by shaimaa
                # credit_line = self._get_existing_lines(
                #     line_ids + new_lines, line, credit_account_id, debit, credit)
                #
                # if not credit_line:
                credit_line = self._prepare_line_values(line, credit_account_id, date, debit, credit, cost_center_analytic)
                new_lines.append(credit_line)
                # else:
                #     credit_line['debit'] += debit
                #     credit_line['credit'] += credit
        return new_lines

