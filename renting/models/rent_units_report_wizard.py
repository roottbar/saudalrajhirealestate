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

    company_ids = fields.Many2many('res.company', string='الشركات', required=True, 
                                  default=lambda self: self.env.company)
    operating_unit_id = fields.Many2one('operating.unit', string='الفرع', 
                                       domain="[('company_id', 'in', company_ids)]")
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
    ], string='نوع التقرير', default='excel', required=True)
    
    # حقول للمجاميع
    company_currency_id = fields.Many2one('res.currency', string='عملة الشركة', readonly=True)
    total_expenses = fields.Monetary(
        string='إجمالي المصروفات',
        currency_field='company_currency_id',
        compute='_compute_totals'
    )
    total_revenues = fields.Monetary(
        string='إجمالي الإيرادات',
        currency_field='company_currency_id',
        compute='_compute_totals'
    )

    @api.onchange('company_ids')
    def _onchange_company_ids(self):
        """تحديث عملة الشركة عند تغيير الشركات"""
        if self.company_ids:
            # استخدام عملة أول شركة محددة
            self.company_currency_id = self.company_ids[0].currency_id
            # إعادة تعيين الفرع
            self.operating_unit_id = False
            self.property_build_id = False
            self.property_id = False
            self.product_id = False
        else:
            self.company_currency_id = False
            
        # تحديث النطاق للفروع
        if self.company_ids:
            return {
                'domain': {
                    'operating_unit_id': [('company_id', 'in', self.company_ids.ids)]
                }
            }

    @api.onchange('operating_unit_id')
    def _onchange_operating_unit_id(self):
        """تحديث النطاق عند تغيير الفرع"""
        if self.operating_unit_id:
            # إعادة تعيين المجمع والعقار والوحدة
            self.property_build_id = False
            self.property_id = False
            self.product_id = False
            
        return {
            'domain': {
                'property_id': [('property_address_area', '=', self.operating_unit_id.id)] if self.operating_unit_id else []
            }
        }

    @api.onchange('property_build_id')
    def _onchange_property_build_id(self):
        """تحديث النطاق عند تغيير المجمع"""
        if self.property_build_id:
            # إعادة تعيين العقار والوحدة
            self.property_id = False
            self.product_id = False
            
        return {
            'domain': {
                'property_id': [('property_address_build', '=', self.property_build_id.id)] if self.property_build_id else []
            }
        }

    @api.onchange('property_id')
    def _onchange_property_id(self):
        """تحديث النطاق عند تغيير العقار"""
        if self.property_id:
            self.product_id = False
            
        return {
            'domain': {
                'product_id': [('property_id', '=', self.property_id.id)] if self.property_id else []
            }
        }

    def _get_report_data(self):
        """جلب بيانات التقرير"""
        domain = []
        
        # فلترة حسب الشركات
        if self.company_ids:
            domain.append(('company_id', 'in', self.company_ids.ids))
            
        # فلترة حسب الفرع
        if self.operating_unit_id:
            domain.append(('operating_unit_id', '=', self.operating_unit_id.id))
            
        # فلترة حسب المجمع
        if self.property_build_id:
            domain.append(('property_address_build', '=', self.property_build_id.id))
            
        # فلترة حسب العقار
        if self.property_id:
            domain.append(('property_id', '=', self.property_id.id))
            
        # فلترة حسب الوحدة
        if self.product_id:
            domain.append(('product_id', '=', self.product_id.id))
            
        # فلترة حسب التاريخ
        if self.date_from:
            domain.append(('date_start', '>=', self.date_from))
        if self.date_to:
            domain.append(('date_start', '<=', self.date_to))
            
        # البحث عن عقود الإيجار
        rent_orders = self.env['sale.order'].search(domain + [('is_rental_order', '=', True)])
        
        data = []
        for order in rent_orders:
            # حساب المصروفات والإيرادات
            expenses = 0.0
            revenues = order.amount_total
            
            # البحث عن المصروفات المرتبطة بالعقد
            if order.analytic_account_id:
                expense_lines = self.env['account.analytic.line'].search([
                    ('account_id', '=', order.analytic_account_id.id),
                    ('amount', '<', 0)  # المصروفات تكون بقيم سالبة
                ])
                expenses = sum(abs(line.amount) for line in expense_lines)
            
            # معلومات الوحدة
            unit_info = {
                'company_name': order.company_id.name,
                'operating_unit': order.operating_unit_id.name if order.operating_unit_id else '',
                'property_build': order.property_address_build.name if order.property_address_build else '',
                'property_name': order.property_id.name if order.property_id else '',
                'unit_name': order.product_id.name if order.product_id else '',
                'partner_name': order.partner_id.name,
                'date_start': order.date_start,
                'date_end': order.date_end,
                'rental_amount': order.amount_total,
                'expenses': expenses,
                'revenues': revenues,
                'net_profit': revenues - expenses,
                'currency': order.currency_id.name,
                'state': dict(order._fields['state'].selection).get(order.state, order.state),
            }
            
            # إضافة تفاصيل خطوط العقد
            unit_info['order_lines'] = []
            for line in order.order_line:
                line_info = {
                    'product_name': line.product_id.name,
                    'quantity': line.product_uom_qty,
                    'price_unit': line.price_unit,
                    'subtotal': line.price_subtotal,
                }
                unit_info['order_lines'].append(line_info)
                
            data.append(unit_info)
            
        return data

    @api.depends('date_from', 'date_to', 'company_ids', 'operating_unit_id', 'property_build_id', 'property_id', 'product_id')
    def _compute_totals(self):
        """حساب المجاميع"""
        for record in self:
            data = record._get_report_data()
            
            total_expenses = 0.0
            total_revenues = 0.0
            
            for item in data:
                total_expenses += item.get('expenses', 0.0)
                total_revenues += item.get('revenues', 0.0)
                
            record.total_expenses = total_expenses
            record.total_revenues = total_revenues

    def _calculate_analytic_amount(self, account, amount_type):
        """حساب المبالغ من الحساب التحليلي"""
        domain = [('account_id', '=', account.id)]
        
        if self.date_from:
            domain.append(('date', '>=', self.date_from))
        if self.date_to:
            domain.append(('date', '<=', self.date_to))
            
        if amount_type == 'expense':
            domain.append(('amount', '<', 0))
        elif amount_type == 'revenue':
            domain.append(('amount', '>', 0))
            
        lines = self.env['account.analytic.line'].search(domain)
        
        if amount_type == 'expense':
            return sum(abs(line.amount) for line in lines)
        else:
            return sum(line.amount for line in lines)

    def _get_column_width(self, data, column_index, header_text):
        """حساب عرض العمود بناءً على المحتوى"""
        max_width = len(header_text)
        
        for row in data:
            if isinstance(row, dict):
                values = list(row.values())
                if column_index < len(values):
                    cell_value = str(values[column_index])
                    max_width = max(max_width, len(cell_value))
                    
        # تحديد الحد الأدنى والأقصى لعرض العمود
        return min(max(max_width + 2, 10), 50)

    def generate_excel_report(self):
        """إنشاء تقرير Excel"""
        if not xlsxwriter:
            raise UserError('مكتبة xlsxwriter غير مثبتة. يرجى تثبيتها أولاً.')
            
        # جلب البيانات
        data = self._get_report_data()
        
        if not data:
            raise UserError('لا توجد بيانات لإنشاء التقرير.')
            
        # إنشاء ملف Excel في الذاكرة
        output = io.BytesIO()
        workbook = xlsxwriter.Workbook(output, {'in_memory': True})
        worksheet = workbook.add_worksheet('تقرير الوحدات المؤجرة')
        
        # تنسيقات الخلايا
        header_format = workbook.add_format({
            'bold': True,
            'bg_color': '#4472C4',
            'font_color': 'white',
            'align': 'center',
            'valign': 'vcenter',
            'border': 1
        })
        
        cell_format = workbook.add_format({
            'align': 'center',
            'valign': 'vcenter',
            'border': 1
        })
        
        number_format = workbook.add_format({
            'num_format': '#,##0.00',
            'align': 'center',
            'valign': 'vcenter',
            'border': 1
        })
        
        date_format = workbook.add_format({
            'num_format': 'dd/mm/yyyy',
            'align': 'center',
            'valign': 'vcenter',
            'border': 1
        })
        
        # عناوين الأعمدة
        headers = [
            'الشركة', 'الفرع', 'المجمع', 'العقار', 'الوحدة', 'المستأجر',
            'تاريخ البداية', 'تاريخ النهاية', 'مبلغ الإيجار', 'المصروفات',
            'الإيرادات', 'صافي الربح', 'العملة', 'الحالة'
        ]
        
        # كتابة العناوين
        for col, header in enumerate(headers):
            worksheet.write(0, col, header, header_format)
            
        # كتابة البيانات
        row = 1
        for item in data:
            worksheet.write(row, 0, item.get('company_name', ''), cell_format)
            worksheet.write(row, 1, item.get('operating_unit', ''), cell_format)
            worksheet.write(row, 2, item.get('property_build', ''), cell_format)
            worksheet.write(row, 3, item.get('property_name', ''), cell_format)
            worksheet.write(row, 4, item.get('unit_name', ''), cell_format)
            worksheet.write(row, 5, item.get('partner_name', ''), cell_format)
            
            # التواريخ
            if item.get('date_start'):
                worksheet.write(row, 6, item['date_start'], date_format)
            else:
                worksheet.write(row, 6, '', cell_format)
                
            if item.get('date_end'):
                worksheet.write(row, 7, item['date_end'], date_format)
            else:
                worksheet.write(row, 7, '', cell_format)
            
            # المبالغ
            worksheet.write(row, 8, item.get('rental_amount', 0), number_format)
            worksheet.write(row, 9, item.get('expenses', 0), number_format)
            worksheet.write(row, 10, item.get('revenues', 0), number_format)
            worksheet.write(row, 11, item.get('net_profit', 0), number_format)
            
            worksheet.write(row, 12, item.get('currency', ''), cell_format)
            worksheet.write(row, 13, item.get('state', ''), cell_format)
            
            row += 1
            
        # إضافة صف المجاميع
        if data:
            total_row = row + 1
            worksheet.write(total_row, 0, 'المجموع', header_format)
            
            # دمج الخلايا للمجموع
            worksheet.merge_range(total_row, 0, total_row, 7, 'المجموع', header_format)
            
            # حساب المجاميع
            total_rental = sum(item.get('rental_amount', 0) for item in data)
            total_expenses = sum(item.get('expenses', 0) for item in data)
            total_revenues = sum(item.get('revenues', 0) for item in data)
            total_profit = sum(item.get('net_profit', 0) for item in data)
            
            worksheet.write(total_row, 8, total_rental, number_format)
            worksheet.write(total_row, 9, total_expenses, number_format)
            worksheet.write(total_row, 10, total_revenues, number_format)
            worksheet.write(total_row, 11, total_profit, number_format)
            
        # تعديل عرض الأعمدة
        for col in range(len(headers)):
            width = self._get_column_width(data, col, headers[col])
            worksheet.set_column(col, col, width)
            
        # إغلاق الملف
        workbook.close()
        output.seek(0)
        
        # إنشاء المرفق
        report_name = f'تقرير_الوحدات_المؤجرة_{datetime.now().strftime("%Y%m%d_%H%M%S")}.xlsx'
        attachment = self.env['ir.attachment'].create({
            'name': report_name,
            'type': 'binary',
            'datas': base64.b64encode(output.read()),
            'res_model': self._name,
            'res_id': self.id,
            'mimetype': 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        })
        
        return {
            'type': 'ir.actions.act_url',
            'url': f'/web/content/{attachment.id}?download=true',
            'target': 'self',
        }

    def generate_html_report(self):
        """إنشاء تقرير HTML"""
        data = self._get_report_data()
        
        if not data:
            raise UserError('لا توجد بيانات لإنشاء التقرير.')
            
        return {
            'type': 'ir.actions.report',
            'report_name': 'renting.rent_units_report_template',
            'report_type': 'qweb-html',
            'data': {'data': data, 'wizard': self},
            'context': self.env.context,
        }

    def generate_report(self):
        """إنشاء التقرير حسب النوع المختار"""
        if self.report_type == 'html':
            return self.generate_html_report()
        else:
            return self.generate_excel_report()
