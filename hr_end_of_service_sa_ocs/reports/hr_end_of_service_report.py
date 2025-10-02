# -*- coding: utf-8 -*-

from odoo import models, fields, api
from datetime import datetime
import base64
import io

try:
    from odoo.addons.report_xlsx.report.report_xlsx import ReportXlsx
except ImportError:
    ReportXlsx = object


class HrEndOfServiceReportXlsx(ReportXlsx):
    
    def generate_xlsx_report(self, workbook, data, settlements):
        """Generate Excel report for End of Service settlements"""
        
        # Define formats
        title_format = workbook.add_format({
            'bold': True,
            'font_size': 16,
            'align': 'center',
            'valign': 'vcenter',
            'bg_color': '#4472C4',
            'font_color': 'white',
            'border': 1
        })
        
        header_format = workbook.add_format({
            'bold': True,
            'font_size': 12,
            'align': 'center',
            'valign': 'vcenter',
            'bg_color': '#D9E2F3',
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
            sheet_name = f"تصفية_{settlement.employee_id.name[:20]}"
            worksheet = workbook.add_worksheet(sheet_name)
            
            # Set column widths
            worksheet.set_column('A:A', 25)
            worksheet.set_column('B:B', 20)
            worksheet.set_column('C:C', 25)
            worksheet.set_column('D:D', 20)
            
            row = 0
            
            # Title
            worksheet.merge_range(row, 0, row, 3, 'تصفية نهاية الخدمة', title_format)
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
                ('تاريخ التعيين', settlement.start_date.strftime('%d/%m/%Y') if settlement.start_date else ''),
                ('تاريخ انتهاء الخدمة', settlement.end_date.strftime('%d/%m/%Y') if settlement.end_date else ''),
                ('نوع إنهاء الخدمة', dict(settlement._fields['termination_type'].selection).get(settlement.termination_type, '')),
            ]
            
            for label, value in employee_data:
                worksheet.write(row, 0, label, header_format)
                worksheet.write(row, 1, value, cell_format)
                row += 1
            
            row += 1
            
            # Service Period Section
            worksheet.merge_range(row, 0, row, 3, 'فترة الخدمة', header_format)
            row += 1
            
            service_data = [
                ('إجمالي أيام الخدمة', settlement.total_service_days),
                ('سنوات الخدمة', f"{settlement.service_years} سنة"),
                ('الأشهر', f"{settlement.service_months} شهر"),
                ('الأيام', f"{settlement.service_days} يوم"),
            ]
            
            for label, value in service_data:
                worksheet.write(row, 0, label, header_format)
                worksheet.write(row, 1, str(value), cell_format)
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
            ]
            
            for label, value in salary_data:
                worksheet.write(row, 0, label, header_format)
                worksheet.write(row, 1, value, currency_format)
                row += 1
            
            row += 1
            
            # Benefits and Entitlements Section
            worksheet.merge_range(row, 0, row, 3, 'المكافآت والاستحقاقات', header_format)
            row += 1
            
            benefits_data = [
                ('مكافأة نهاية الخدمة', settlement.end_of_service_benefit),
                ('أيام الإجازة المتبقية', settlement.remaining_vacation_days),
                ('مبلغ الإجازة', settlement.vacation_amount),
                ('مكافآت أخرى', settlement.other_benefits),
                ('إجمالي المكافآت', settlement.gross_amount),
            ]
            
            for label, value in benefits_data:
                if label == 'أيام الإجازة المتبقية':
                    worksheet.write(row, 0, label, header_format)
                    worksheet.write(row, 1, f"{value} يوم", cell_format)
                else:
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


class HrEndOfServiceReport(models.AbstractModel):
    _name = 'report.hr_end_of_service_sa.end_of_service_xlsx'
    _inherit = 'report.report_xlsx.abstract'
    
    def generate_xlsx_report(self, workbook, data, settlements):
        report = HrEndOfServiceReportXlsx()
        return report.generate_xlsx_report(workbook, data, settlements)


class HrEndOfServicePdfReport(models.AbstractModel):
    _name = 'report.hr_end_of_service_sa.end_of_service_pdf'
    _description = 'End of Service PDF Report'
    
    @api.model
    def _get_report_values(self, docids, data=None):
        settlements = self.env['hr.end.of.service'].browse(docids)
        
        return {
            'doc_ids': docids,
            'doc_model': 'hr.end.of.service',
            'docs': settlements,
            'data': data,
            'company': self.env.company,
            'print_date': datetime.now().strftime('%d/%m/%Y %H:%M'),
        }