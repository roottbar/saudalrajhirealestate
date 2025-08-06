# -*- coding: utf-8 -*-

from odoo import models, fields, api
from odoo.exceptions import UserError
import base64
import io
from datetime import datetime
try:
    import xlsxwriter
except ImportError:
    xlsxwriter = None


class RentUnitsReportWizard(models.TransientModel):
    _name = 'rent.units.report.wizard'
    _description = 'معالج تقرير الوحدات المؤجرة'

    company_id = fields.Many2one('res.company', string='الشركة', required=True, 
                                default=lambda self: self.env.company)
    operating_unit_id = fields.Many2one('operating.unit', string='الفرع', 
                                       domain="[('company_id', '=', company_id)]")
    property_build_id = fields.Many2one('rent.property.build', string='المجمع')
    property_id = fields.Many2one('rent.property', string='العقار',
                                 domain="[('property_address_build', '=', property_build_id), ('property_address_area', '=', operating_unit_id)]")
    product_id = fields.Many2one('product.product', string='الوحدة',
                                domain="[('property_id', '=', property_id)]")
    
    date_from = fields.Date(string='من تاريخ')
    date_to = fields.Date(string='إلى تاريخ')
    
    report_type = fields.Selection([
        ('html', 'HTML'),
        ('excel', 'Excel')
    ], string='نوع التقرير', default='html', required=True)

    @api.onchange('company_id')
    def _onchange_company_id(self):
        """تصفية الفروع حسب الشركة المختارة"""
        self.operating_unit_id = False
        self.property_build_id = False
        self.property_id = False
        self.product_id = False
        return {'domain': {'operating_unit_id': [('company_id', '=', self.company_id.id)]}}

    @api.onchange('operating_unit_id')
    def _onchange_operating_unit_id(self):
        """تصفية المجمعات حسب الفرع المختار"""
        self.property_build_id = False
        self.property_id = False
        self.product_id = False
        if self.operating_unit_id:
            # البحث عن المجمعات المرتبطة بالفرع
            properties = self.env['rent.property'].search([('property_address_area', '=', self.operating_unit_id.id)])
            build_ids = properties.mapped('property_address_build').ids
            return {'domain': {'property_build_id': [('id', 'in', build_ids)]}}
        return {'domain': {'property_build_id': []}}

    @api.onchange('property_build_id')
    def _onchange_property_build_id(self):
        """تصفية العقارات حسب المجمع المختار"""
        self.property_id = False
        self.product_id = False
        if self.property_build_id and self.operating_unit_id:
            return {'domain': {'property_id': [
                ('property_address_build', '=', self.property_build_id.id),
                ('property_address_area', '=', self.operating_unit_id.id)
            ]}}
        return {'domain': {'property_id': []}}

    @api.onchange('property_id')
    def _onchange_property_id(self):
        """تصفية الوحدات حسب العقار المختار"""
        self.product_id = False
        if self.property_id:
            return {'domain': {'product_id': [('property_id', '=', self.property_id.id)]}}
        return {'domain': {'product_id': []}}

    def _get_report_data(self):
        """جلب بيانات التقرير"""
        domain = []
        
        # تطبيق الفلاتر
        if self.operating_unit_id:
            domain.append(('property_address_area', '=', self.operating_unit_id.id))
        if self.property_build_id:
            domain.append(('property_address_build2', '=', self.property_build_id.id))
        if self.property_id:
            domain.append(('property_number', '=', self.property_id.id))
        if self.product_id:
            domain.append(('product_id', '=', self.product_id.id))
        if self.date_from:
            domain.append(('fromdate', '>=', self.date_from))
        if self.date_to:
            domain.append(('todate', '<=', self.date_to))

        # جلب بيانات خطوط أوامر البيع
        sale_order_lines = self.env['sale.order.line'].search(domain)
        
        data = []
        for line in sale_order_lines:
            data.append({
                'company_name': line.order_id.company_id.name,
                'operating_unit': line.property_address_area.name if line.property_address_area else '',
                'property_build': line.property_address_build2.name if line.property_address_build2 else '',
                'property_name': line.property_number.property_name if line.property_number else '',
                'analytic_account': line.analytic_account_id.name if line.analytic_account_id else '',
                'unit_name': line.product_id.name,
                'customer_name': line.order_partner_id.name if line.order_partner_id else '',
                'contract_number': line.order_id.name,
                'unit_state': line.unit_state or '',
                'amount_paid': line.amount_paid,
                'amount_due': line.amount_due,
                'unit_expenses': line.unit_expenses,
                'unit_revenues': line.unit_revenues,
                'from_date': line.fromdate,
                'to_date': line.todate,
            })
        
        return data

    def generate_html_report(self):
        """إنشاء تقرير HTML"""
        data = self._get_report_data()
        return self.env.ref('renting.rent_units_report').report_action(self, data={'docs': data})

    def generate_excel_report(self):
        """إنشاء تقرير Excel"""
        if not xlsxwriter:
            raise UserError('مكتبة xlsxwriter غير مثبتة. يرجى تثبيتها أولاً.')
        
        data = self._get_report_data()
        
        # إنشاء ملف Excel
        output = io.BytesIO()
        workbook = xlsxwriter.Workbook(output, {'in_memory': True})
        worksheet = workbook.add_worksheet('تقرير الوحدات المؤجرة')
        
        # تنسيق الخلايا
        header_format = workbook.add_format({
            'bold': True,
            'bg_color': '#D7E4BC',
            'border': 1,
            'align': 'center',
            'valign': 'vcenter'
        })
        
        cell_format = workbook.add_format({
            'border': 1,
            'align': 'center',
            'valign': 'vcenter'
        })
        
        # كتابة العناوين
        headers = [
            'الشركة', 'الفرع', 'المجمع', 'العقار', 'الحساب التحليلي', 'الوحدة',
            'اسم العميل', 'رقم العقد', 'حالة الوحدة', 'المبلغ المدفوع',
            'المبلغ المستحق', 'المصروفات', 'الإيرادات', 'تاريخ الاستلام', 'تاريخ التسليم'
        ]
        
        for col, header in enumerate(headers):
            worksheet.write(0, col, header, header_format)
        
        # كتابة البيانات
        for row, line_data in enumerate(data, 1):
            worksheet.write(row, 0, line_data['company_name'], cell_format)
            worksheet.write(row, 1, line_data['operating_unit'], cell_format)
            worksheet.write(row, 2, line_data['property_build'], cell_format)
            worksheet.write(row, 3, line_data['property_name'], cell_format)
            worksheet.write(row, 4, line_data['analytic_account'], cell_format)
            worksheet.write(row, 5, line_data['unit_name'], cell_format)
            worksheet.write(row, 6, line_data['customer_name'], cell_format)
            worksheet.write(row, 7, line_data['contract_number'], cell_format)
            worksheet.write(row, 8, line_data['unit_state'], cell_format)
            worksheet.write(row, 9, line_data['amount_paid'], cell_format)
            worksheet.write(row, 10, line_data['amount_due'], cell_format)
            worksheet.write(row, 11, line_data['unit_expenses'], cell_format)
            worksheet.write(row, 12, line_data['unit_revenues'], cell_format)
            worksheet.write(row, 13, str(line_data['from_date']) if line_data['from_date'] else '', cell_format)
            worksheet.write(row, 14, str(line_data['to_date']) if line_data['to_date'] else '', cell_format)
        
        # ضبط عرض الأعمدة
        worksheet.set_column('A:O', 15)
        
        workbook.close()
        output.seek(0)
        
        # إنشاء المرفق
        filename = f'تقرير_الوحدات_المؤجرة_{datetime.now().strftime("%Y%m%d_%H%M%S")}.xlsx'
        attachment = self.env['ir.attachment'].create({
            'name': filename,
            'type': 'binary',
            'datas': base64.b64encode(output.read()),
            'res_model': self._name,
            'res_id': self.id,
            'mimetype': 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        })
        
        return {
            'type': 'ir.actions.act_url',
            'url': f'/web/content/{attachment.id}?download=true',
            'target': 'new',
        }

    def generate_report(self):
        """إنشاء التقرير حسب النوع المختار"""
        if self.report_type == 'html':
            return self.generate_html_report()
        else:
            return self.generate_excel_report()
