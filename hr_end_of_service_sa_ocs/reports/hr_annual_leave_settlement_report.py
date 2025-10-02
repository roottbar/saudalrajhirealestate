# -*- coding: utf-8 -*-

from odoo import models, fields, api
from datetime import datetime
import base64
import io

try:
    from odoo.addons.report_xlsx.report.report_xlsx import ReportXlsx
except ImportError:
    ReportXlsx = object


class HrAnnualLeaveSettlementReportXlsx(ReportXlsx):
    
    def generate_xlsx_report(self, workbook, data, settlements):
        """Generate Excel report for Annual Leave settlements"""
        
        # Define formats
        title_format = workbook.add_format({
            'bold': True,
            'font_size': 16,
            'align': 'center',
            'valign': 'vcenter',
            'bg_color': '#70AD47',
            'font_color': 'white',
            'border': 1
        })
        
        header_format = workbook.add_format({
            'bold': True,
            'font_size': 12,
            'align': 'center',
            'valign': 'vcenter',
            'bg_color': '#E2EFDA',
            'border': 1,
            'text_wrap': True
        })
        
        cell_format = workbook.add_format({
            'font_size': 10,
            'align': 'center',
            'valign': 'vcenter',
            'border': 1
        })
        
        currency_format = workbook.add_format({
            'font_size': 10,
            'align': 'center',
            'valign': 'vcenter',
            'border': 1,
            'num_format': '#,##0.00'
        })
        
        date_format = workbook.add_format({
            'font_size': 10,
            'align': 'center',
            'valign': 'vcenter',
            'border': 1,
            'num_format': 'dd/mm/yyyy'
        })
        
        for settlement in settlements:
            # Create worksheet for each settlement
            sheet_name = f"إجازة_{settlement.employee_id.name[:20]}"
            worksheet = workbook.add_worksheet(sheet_name)
            
            # Set column widths
            worksheet.set_column('A:A', 25)
            worksheet.set_column('B:B', 20)
            worksheet.set_column('C:C', 25)
            worksheet.set_column('D:D', 20)
            
            row = 0
            
            # Title
            worksheet.merge_range(row, 0, row, 3, 'تصفية الإجازة السنوية', title_format)
            row += 2
            
            # Company Information
            company = settlement.company_id
            worksheet.write(row, 0, 'اسم الشركة:', header_format)
            worksheet.write(row, 1, company.name or '', cell_format)
            worksheet.write(row, 2, 'تاريخ التقرير:', header_format)
            worksheet.write(row, 3, datetime.now().strftime('%d/%m/%Y'), date_format)
            row += 2
            
            # Employee Information Section
            worksheet.merge_range(row, 0, row, 3, 'معلومات الموظف', header_format)
            row += 1
            
            employee_data = [
                ('اسم الموظف', settlement.employee_id.name),
                ('رقم الهوية', settlement.employee_id.identification_id or ''),
                ('المسمى الوظيفي', settlement.employee_id.job_id.name if settlement.employee_id.job_id else ''),
                ('القسم', settlement.employee_id.department_id.name if settlement.employee_id.department_id else ''),
                ('تاريخ الحساب', settlement.calculation_date.strftime('%d/%m/%Y') if settlement.calculation_date else ''),
                ('نوع التصفية', dict(settlement._fields['settlement_type'].selection).get(settlement.settlement_type, '')),
            ]
            
            for label, value in employee_data:
                worksheet.write(row, 0, label, header_format)
                worksheet.write(row, 1, value, cell_format)
                row += 1
            
            row += 1
            
            # Settlement Period Section
            worksheet.merge_range(row, 0, row, 3, 'فترة التصفية', header_format)
            row += 1
            
            period_data = [
                ('من تاريخ', settlement.period_from.strftime('%d/%m/%Y') if settlement.period_from else ''),
                ('إلى تاريخ', settlement.period_to.strftime('%d/%m/%Y') if settlement.period_to else ''),
                ('تاريخ التصفية', settlement.settlement_date.strftime('%d/%m/%Y') if settlement.settlement_date else ''),
            ]
            
            for label, value in period_data:
                worksheet.write(row, 0, label, header_format)
                worksheet.write(row, 1, value, cell_format)
                row += 1
            
            row += 1
            
            # Salary Details Section
            worksheet.merge_range(row, 0, row, 3, 'تفاصيل الراتب', header_format)
            row += 1
            
            salary_data = [
                ('الراتب الأساسي', settlement.basic_salary),
                ('بدل السكن', settlement.housing_allowance),
                ('بدل المواصلات', settlement.transport_allowance),
                ('البدلات الأخرى', settlement.other_allowances),
                ('إجمالي الراتب', settlement.total_salary),
                ('الراتب اليومي', settlement.daily_salary),
            ]
            
            for label, value in salary_data:
                worksheet.write(row, 0, label, header_format)
                worksheet.write(row, 1, value, currency_format)
                row += 1
            
            row += 1
            
            # Leave Details Section
            worksheet.merge_range(row, 0, row, 3, 'تفاصيل الإجازة', header_format)
            row += 1
            
            leave_data = [
                ('إجمالي أيام الإجازة السنوية', f"{settlement.total_leave_days} يوم"),
                ('أيام الإجازة المستخدمة', f"{settlement.used_leave_days} يوم"),
                ('أيام الإجازة المتبقية', f"{settlement.remaining_leave_days} يوم"),
            ]
            
            for label, value in leave_data:
                worksheet.write(row, 0, label, header_format)
                worksheet.write(row, 1, value, cell_format)
                row += 1
            
            row += 1
            
            # Settlement Calculation Section
            worksheet.merge_range(row, 0, row, 3, 'حساب التصفية', header_format)
            row += 1
            
            calculation_data = [
                ('مبلغ تصفية الإجازة', settlement.settlement_amount),
                ('مكافآت أخرى', settlement.other_benefits),
                ('إجمالي المكافآت', settlement.gross_amount),
            ]
            
            for label, value in calculation_data:
                worksheet.write(row, 0, label, header_format)
                worksheet.write(row, 1, value, currency_format)
                row += 1
            
            row += 1
            
            # Deductions Section
            worksheet.merge_range(row, 0, row, 3, 'الخصومات', header_format)
            row += 1
            
            deductions_data = [
                ('خصم القروض', settlement.loan_deductions),
                ('خصم السلف', settlement.advance_deductions),
                ('خصومات أخرى', settlement.other_deductions),
                ('إجمالي الخصومات', settlement.total_deductions),
            ]
            
            for label, value in deductions_data:
                worksheet.write(row, 0, label, header_format)
                worksheet.write(row, 1, value, currency_format)
                row += 1
            
            row += 1
            
            # Net Amount Section
            worksheet.merge_range(row, 0, row, 1, 'صافي المبلغ المستحق', title_format)
            worksheet.merge_range(row, 2, row, 3, settlement.net_amount, title_format)
            row += 2
            
            # Calculation Formula Section
            worksheet.merge_range(row, 0, row, 3, 'طريقة الحساب', header_format)
            row += 1
            
            formula_text = f"صافي المبلغ = (أيام الإجازة المتبقية × الراتب اليومي) + المكافآت الأخرى - إجمالي الخصومات"
            worksheet.merge_range(row, 0, row, 3, formula_text, cell_format)
            row += 1
            
            calculation_text = f"صافي المبلغ = ({settlement.remaining_leave_days} × {settlement.daily_salary}) + {settlement.other_benefits} - {settlement.total_deductions} = {settlement.net_amount}"
            worksheet.merge_range(row, 0, row, 3, calculation_text, cell_format)
            row += 2
            
            # Notes Section
            if settlement.notes:
                worksheet.merge_range(row, 0, row, 3, 'ملاحظات', header_format)
                row += 1
                worksheet.merge_range(row, 0, row, 3, settlement.notes, cell_format)
                row += 2
            
            # Signatures Section
            worksheet.write(row, 0, 'توقيع الموظف:', header_format)
            worksheet.write(row, 1, '_________________', cell_format)
            worksheet.write(row, 2, 'توقيع المدير:', header_format)
            worksheet.write(row, 3, '_________________', cell_format)
            row += 2
            
            worksheet.write(row, 0, 'التاريخ:', header_format)
            worksheet.write(row, 1, '_________________', cell_format)
            worksheet.write(row, 2, 'التاريخ:', header_format)
            worksheet.write(row, 3, '_________________', cell_format)


class HrAnnualLeaveSettlementReport(models.AbstractModel):
    _name = 'report.hr_end_of_service_sa.annual_leave_settlement_xlsx'
    _inherit = 'report.report_xlsx.abstract'
    
    def generate_xlsx_report(self, workbook, data, settlements):
        report = HrAnnualLeaveSettlementReportXlsx()
        return report.generate_xlsx_report(workbook, data, settlements)


class HrAnnualLeaveSettlementPdfReport(models.AbstractModel):
    _name = 'report.hr_end_of_service_sa.annual_leave_settlement_pdf'
    _description = 'Annual Leave Settlement PDF Report'
    
    @api.model
    def _get_report_values(self, docids, data=None):
        settlements = self.env['hr.annual.leave.settlement'].browse(docids)
        
        return {
            'doc_ids': docids,
            'doc_model': 'hr.annual.leave.settlement',
            'docs': settlements,
            'data': data,
            'company': self.env.company,
            'print_date': datetime.now().strftime('%d/%m/%Y %H:%M'),
        }