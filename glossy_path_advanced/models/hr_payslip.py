# -*- coding: utf-8 -*-

import base64
import io

from odoo import models
from odoo.tools.misc import xlsxwriter


class HrPayslip(models.Model):
    _inherit = 'hr.payslip'

    def get_employee_number_of_days_per_month_with_vacation(self, payslip):
        contract = payslip.contract_id
        work_hours = contract._get_work_hours(payslip.date_from, payslip.date_to)
        work_hours_ordered = sorted(work_hours.items(), key=lambda x: x[1])
        biggest_work = work_hours_ordered[-1][0] if work_hours_ordered else 0
        add_days_rounding = 0
        number_of_days = 0
        calendar = contract.resource_calendar_id
        for work_entry_type_id, hours in work_hours_ordered:
            work_entry_type = self.env['hr.work.entry.type'].browse(work_entry_type_id)
            days = round(hours / calendar.hours_per_day, 5) if calendar.hours_per_day else 0
            if work_entry_type_id == biggest_work:
                days += add_days_rounding
            number_of_days = payslip._round_days(work_entry_type, days)
            add_days_rounding += (days - number_of_days)
        return number_of_days

    def get_employee_number_of_days_per_month_without_vacation(self, payslip):
        contract = payslip.contract_id
        work_hours = contract._get_work_hours(payslip.date_from, payslip.date_to)
        work_hours_ordered = sorted(work_hours.items(), key=lambda x: x[1])
        biggest_work = work_hours_ordered[-1][0] if work_hours_ordered else 0
        add_days_rounding = 0
        number_of_days = 0
        calendar = contract.resource_calendar_id
        for work_entry_type_id, hours in work_hours_ordered:
            work_entry_type = self.env['hr.work.entry.type'].browse(work_entry_type_id)
            days = round(hours / calendar.hours_per_day, 5) if calendar.hours_per_day else 0
            if work_entry_type_id == biggest_work:
                days += add_days_rounding
            number_of_days = payslip._round_days(work_entry_type, days)
            add_days_rounding += (days)
        return number_of_days

    def get_rules(self, payslip, rule):
        amount = 0.0
        lines = payslip.line_ids.filtered(lambda l: l.salary_rule_id and rule == l.salary_rule_id.id and l.total != 0.0)
        if lines:
            amount = lines.total
        return amount

    def action_export_xls(self, ):
        output = io.BytesIO()
        workbook = xlsxwriter.Workbook(output, {'in_memory': True})
        worksheet = workbook.add_worksheet('Payroll Register')

        # # header

        header_format1 = workbook.add_format(
            {'align': 'center', 'valign': 'vcenter', 'fg_color': '#e7f3fd', 'font_size': 10})
        header_format2 = workbook.add_format(
            {'align': 'center', 'valign': 'vcenter', 'fg_color': '#548dd4', 'font_size': 10})

        worksheet.merge_range('A1:F1', 'Employee Information', header_format1)
        worksheet.merge_range('G1:L1', 'AS PER CONTRACT', header_format2)
        worksheet.merge_range('M1:N1', 'Worked Hours', header_format1)
        worksheet.merge_range('O1:W1', 'EARNED SALARY', header_format2)
        worksheet.merge_range('X1:AG1', 'BENEFITS', header_format1)
        worksheet.merge_range('AH1:AR1', 'DEDUCTIONS', header_format2)
        worksheet.write('AS1', 'NET', header_format1)

        items_header = ["Employee ID", "Employee Name Arabic", "Employee Name English", 'Employee Joining Date',
                        'Cost Center', 'Iqama Number', 'Basic Salary', 'Housing Allowance',
                        'Transportation Allowance', 'Food Allowance', 'Other Allowances',
                        'Total as contract', 'Paid Hours', 'OV Hours', 'Basic Salary',
                        'Housing Allowance', 'Transportation Allowance', 'Mobile Allowance', 'Over Time',
                        'Food Allowance', 'Other Allowances', 'Fuel Allowance', 'Gross Salary',
                        'Loan Payment', 'Bonus', 'Salary Adjustment', 'Mobile Device  Advance',
                        'Annual Ticket Payment', 'Annual Vacation Payment', 'Housing Advance',
                        'Annual Leave Entitlement Result',
                        'Business Trip', 'Total Benefits', 'Cash Advance', 'Loan Deduction',
                        'Traffic Violation Ded', 'GOSI Deduction', 'Absence Deductions', 'Late Hour deduction',
                        'Hous.Adv.Deduct', 'Penalty Education', 'Other Deductions', 'Penelty Deducation',
                        'Total Deduction', 'Net Pay',

                        ]
        row = 1
        col = 0
        for item_header in items_header:
            worksheet.write(row, col, item_header, header_format1)
            worksheet.set_column(0, col, 20)
            col += 1

        # information
        style_normal = workbook.add_format({'align': 'center', 'font_size': 8})
        for payslip in self:
            employee = payslip.employee_id
            contract = employee.contract_id
            employee_number_of_days_per_month_with_vacation = payslip.get_employee_number_of_days_per_month_with_vacation(
                payslip)
            employee_number_of_days_per_month_without_vacation = payslip.get_employee_number_of_days_per_month_without_vacation(
                payslip)
            number_of_hours_per_momnth = employee_number_of_days_per_month_with_vacation * employee.resource_calendar_id.hours_per_day
            balance_days = employee_number_of_days_per_month_without_vacation - employee_number_of_days_per_month_with_vacation
            print(balance_days, "balance_days")
            try:
                balance = balance_days / employee_number_of_days_per_month_without_vacation
            except ZeroDivisionError:
                balance = 0
            earned_salary_wage = round(contract.wage - (balance * contract.wage), 2)
            over_time_number_of_hours = payslip.get_rules(payslip,
                                                          self.env.ref("hr_advanced.hr_rule_overtime_allowance").id)

            earned_salary_housing_allowance = round(contract.housing_allowance - (
                    balance * payslip.get_rules(payslip, self.env.ref("hr_advanced.hr_rule_housing_allowance").id)),
                                                    2)
            earned_salary_transportation_allowance = round(contract.transportation_allowance - (
                    balance * payslip.get_rules(payslip,
                                                self.env.ref("hr_advanced.hr_rule_transportation_allowance").id)),
                                                           2)
            earned_salary_mobile_allowance = round(contract.mobile_allowance - (
                    balance * payslip.get_rules(payslip, self.env.ref("hr_advanced.hr_rule_mobile_allowance").id)),
                                                   2)
            earned_salary_overtime_allowance = round(contract.overtime_allowance - (balance * payslip.get_rules(payslip,
                                                                                                                self.env.ref(
                                                                                                                    "hr_advanced.hr_rule_overtime_allowance").id)),
                                                     2)
            earned_salary_food_allowance = round(contract.food_allowance - (
                    balance * payslip.get_rules(payslip, self.env.ref("hr_advanced.hr_rule_food_allowance").id)), 2)
            earned_salary_other_allowance = round(contract.other_allowance - (
                    balance * payslip.get_rules(payslip, self.env.ref("hr_advanced.hr_rule_other_allowance").id)),
                                                  2)
            earned_salary_fuel_allowance = round(contract.fuel_allowance - (
                    balance * payslip.get_rules(payslip, self.env.ref("hr_advanced.hr_rule_fuel_allowance").id)), 2)
            amount_rule_loan = payslip.get_rules(payslip, self.env.ref("hr_loan.hr_rule_loan").id)
            print(amount_rule_loan, "amount_rule_loan")
            loanpayment = round(amount_rule_loan - (balance * amount_rule_loan), 2)
            amount_rule_bonus = payslip.get_rules(payslip, self.env.ref("hr_bonus_deduction.hr_rule_bonus").id)
            bonus = round(amount_rule_bonus - (balance * amount_rule_bonus), 2)

            col = 0
            row += 1

            worksheet.write(row, col, employee.id, style_normal)  # id
            col += 1
            worksheet.write(row, col, employee.arabic_name, style_normal)  # arabic name
            col += 1
            worksheet.write(row, col, employee.name, style_normal)  # name
            col += 1
            worksheet.write(row, col, contract.date_start.strftime("%d-%m-%Y") if contract.date_start else '',
                            style_normal)  # Employee Joining Date
            col += 1
            worksheet.write(row, col, contract.analytic_account_id.name, style_normal)  # Cost Center
            col += 1
            worksheet.write(row, col, employee.iqama_no, style_normal)  # iqama
            col += 1
            worksheet.write(row, col, contract.wage, style_normal)  # Basic Salary
            col += 1
            worksheet.write(row, col, contract.housing_allowance, style_normal)  # Housing Allowance
            col += 1

            worksheet.write(row, col, contract.transportation_allowance, style_normal)  # Transportation Allowance
            col += 1
            worksheet.write(row, col, contract.food_allowance, style_normal)  # food_allowance
            col += 1
            worksheet.write(row, col, contract.other_allowance, style_normal)  # other_allowance
            col += 1
            worksheet.write(row, col,
                            contract.wage +
                            contract.transportation_allowance +
                            contract.housing_allowance +
                            contract.food_allowance +
                            contract.other_allowance, style_normal)  # Total as contract
            col += 1
            worksheet.write(row, col, number_of_hours_per_momnth, style_normal)  # Paid Hours
            col += 1

            worksheet.write(row, col, over_time_number_of_hours, style_normal)  # OUT Hours
            col += 1
            worksheet.write(row, col, earned_salary_wage, style_normal)  # Basic Salary
            col += 1
            worksheet.write(row, col, earned_salary_housing_allowance, style_normal)  # Housing Allowance
            col += 1

            worksheet.write(row, col, earned_salary_transportation_allowance, style_normal)  # Transportation Allowance
            col += 1
            worksheet.write(row, col, earned_salary_mobile_allowance, style_normal)  # mobile_allowance
            col += 1
            worksheet.write(row, col, earned_salary_overtime_allowance, style_normal)  # overtime_allowance
            col += 1

            worksheet.write(row, col, earned_salary_food_allowance, style_normal)  # food_allowance
            col += 1
            worksheet.write(row, col, earned_salary_other_allowance, style_normal)  # other_allowance
            col += 1
            worksheet.write(row, col, earned_salary_fuel_allowance, style_normal)  # fuel_allowance
            col += 1
            worksheet.write(row, col,
                            earned_salary_wage +
                            earned_salary_housing_allowance +
                            earned_salary_transportation_allowance +
                            earned_salary_mobile_allowance +
                            earned_salary_overtime_allowance +
                            earned_salary_food_allowance +
                            earned_salary_fuel_allowance +
                            earned_salary_other_allowance, style_normal)  # Gross Salary
            col += 1
            worksheet.write(row, col, loanpayment, style_normal)  # Loan Payment
            col += 1
            worksheet.write(row, col, bonus, style_normal)  # bonus
            col += 1

        workbook.close()
        attachment_opj = self.env['ir.attachment']
        attachment = attachment_opj.search([('is_export_report', '=', True)], limit=1)

        if not attachment:
            attachment = attachment_opj.create({
                'datas': base64.encodebytes(output.getvalue()),
                'name': 'HR Master List.xls',
                'is_export_report': True,
            })
        else:
            attachment.write({
                'datas': base64.encodebytes(output.getvalue()),
                'name': 'HR Master List.xls',
            })

        return {
            'type': 'ir.actions.act_url',
            'name': 'Payslip Report',
            'url': '/web/content/ir.attachment/%s/datas/?download=true&filename=%s' % (attachment.id, attachment.name),
            'target': 'self'
        }
