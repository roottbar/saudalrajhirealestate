# -*- coding: utf-8 -*-

import base64
import io

from odoo import fields, models
from odoo.tools.float_utils import float_round
from odoo.tools.misc import xlsxwriter


class Employee(models.Model):
    _inherit = 'hr.employee'

    religion_id = fields.Many2one('res.religion', string="Religion", domain=[('active', '=', True)])

    def action_export_xls(self, ):
        output = io.BytesIO()
        workbook = xlsxwriter.Workbook(output, {'in_memory': True})
        worksheet = workbook.add_worksheet('HR Master List')

        # title

        merge_format = workbook.add_format({
            'bold': True,
            'align': 'center',
            'valign': 'vcenter',
            'fg_color': '#1f4e79',
            'font_color': 'white'
        })

        worksheet.merge_range('A1:B2', 'HR Master list', merge_format)

        # header
        style_header = workbook.add_format(
            {'bold': True, 'pattern': 1, 'bg_color': '#1f4e79', 'align': 'center', 'font_color': 'white',
             'font_size': 10, })
        items_header = ["EMP ID", "Employee Name Arabic", "Employee Name English",
                        "Nationality", "Sponsorship", "Company Name",
                        "Cost Center", "Project Code", "Project Name",
                        "Joining Date", "Date of birth", "Religion",
                        "IQAMA #", "IQAMA Expiry date", "Contract Vacation Days",
                        "Vacation Days Balance", "GOSI #", "Contact number",
                        "Marital Status", "No. of dependents", "Employee Status",
                        "Position - IQAMA", "Position - English", "Position - Arabic",
                        "Insurance class", "Insurance premium", "Basic Salary",
                        "Transportation Allowance", "Housing Allowance", "Food Allowance",
                        "Mobile Allowance", "Fuel Allowance", "Other Allowances",
                        "Total Salary", "Payment Type", "BANK Name", "Account Number", ]
        row = 2
        col = 0
        for item_header in items_header:
            worksheet.write(row, col, item_header, style_header)
            worksheet.set_column(0, col, 15)
            col += 1

        # information
        style_normal = workbook.add_format({'align': 'center', 'font_size': 8})
        for employee in self:
            contract = employee.contract_id
            col = 0
            row += 1

            worksheet.write(row, col, employee.id, style_normal)  # id
            col += 1
            worksheet.write(row, col, employee.arabic_name, style_normal)  # arabic name
            col += 1
            worksheet.write(row, col, employee.name, style_normal)  # name
            col += 1
            worksheet.write(row, col, employee.country_id.name, style_normal)  # Nationality
            col += 1
            worksheet.write(row, col, employee.sponsorship, style_normal)  # Sponsorship
            col += 1
            worksheet.write(row, col, employee.company_id.name, style_normal)  # Company
            col += 1
            worksheet.write(row, col, contract.analytic_account_id.name, style_normal)  # Cost Center
            col += 1
            worksheet.write(row, col, "Project Code", style_normal)
            col += 1
            worksheet.write(row, col, "Project name", style_normal)
            col += 1
            worksheet.write(row, col, contract.date_start.strftime("%d-%m-%Y") if contract.date_start else '',
                            style_normal)  # Joining Date
            col += 1
            worksheet.write(row, col, employee.birthday.strftime("%d-%m-%Y") if employee.birthday else '',
                            style_normal)  # birthday
            col += 1
            worksheet.write(row, col, employee.religion_id.name, style_normal)  # Religion
            col += 1
            worksheet.write(row, col, employee.iqama_no, style_normal)  # iqama
            col += 1
            worksheet.write(row, col,
                            employee.iqama_expiry_date.strftime("%d-%m-%Y") if employee.iqama_expiry_date else '',
                            style_normal)  # iqama_expiry_date
            col += 1
            worksheet.write(row, col, employee.allocation_count, style_normal)  # Contract Vacation Days
            col += 1
            worksheet.write(row, col,
                            float_round(employee.allocation_count - employee.remaining_leaves, precision_digits=2),
                            style_normal)  # Vacation Days Balance
            col += 1
            worksheet.write(row, col, employee.gosi, style_normal)  # Vacation Days Balance
            col += 1
            worksheet.write(row, col, contract.name, style_normal)  # Contact number
            col += 1
            worksheet.write(row, col, employee.marital, style_normal)  # Marital Status
            col += 1
            worksheet.write(row, col, employee.children, style_normal)  # No. of dependents
            col += 1
            worksheet.write(row, col, employee.activity_state, style_normal)  # Employee Status
            col += 1
            worksheet.write(row, col, employee.position_iqama, style_normal)  # Position - IQAMA
            col += 1
            worksheet.write(row, col, employee.job_id.name, style_normal)  # Position - English
            col += 1
            worksheet.write(row, col, employee.job_id.arabic_name, style_normal)  # Position - Arabic
            col += 1
            worksheet.write(row, col, employee.insurance_class, style_normal)  # Insurance premium
            col += 1
            worksheet.write(row, col, "Insurance premium", style_normal)  # Insurance premium
            col += 1
            worksheet.write(row, col, contract.wage, style_normal)  # Basic Salary
            col += 1
            worksheet.write(row, col, contract.transportation_allowance, style_normal)  # Transportation Allowance
            col += 1
            worksheet.write(row, col, contract.housing_allowance, style_normal)  # Housing Allowance
            col += 1
            worksheet.write(row, col, contract.food_allowance, style_normal)  # food_allowance
            col += 1
            worksheet.write(row, col, contract.mobile_allowance, style_normal)  # mobile_allowance
            col += 1
            worksheet.write(row, col, contract.fuel_allowance, style_normal)  # fuel_allowance
            col += 1
            worksheet.write(row, col, contract.other_allowance, style_normal)  # other_allowance
            col += 1
            worksheet.write(row, col,
                            contract.wage +
                            contract.transportation_allowance +
                            contract.housing_allowance +
                            contract.food_allowance +
                            contract.mobile_allowance +
                            contract.fuel_allowance +
                            contract.other_allowance, style_normal)  # Total salary
            col += 1
            worksheet.write(row, col, employee.payment_type, style_normal)  # Payment Type
            col += 1
            worksheet.write(row, col, employee.bank_account_id.bank_id.name, style_normal)  # bank_id name
            col += 1
            worksheet.write(row, col, employee.bank_account_id.acc_number, style_normal)  # account name
            col += 1

        workbook.close()

        attachment_opj = self.env['ir.attachment']
        attachment = attachment_opj.search([('is_export_report', '=', True)], limit=1)

        if not attachment:
            attachment = attachment_opj.create({
                'datas': base64.encodebytes(output.getvalue()),
                'name': 'HR Employee List.xls',
                'is_export_report': True,
            })
        else:
            attachment.write({
                'datas': base64.encodebytes(output.getvalue()),
                'name': 'HR Employee List.xls',
            })
        return {
            'type': 'ir.actions.act_url',
            'name': 'Payslip Report',
            'url': '/web/content/ir.attachment/%s/datas/?download=true&filename=%s' % (attachment.id, attachment.name),
            'target': 'self'
        }
