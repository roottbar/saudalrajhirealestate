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
    
    # إضافة الحقول المحسوبة الجديدة
    company_currency_id = fields.Many2one('res.currency', related='company_id.currency_id', readonly=True)
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

    @api.depends('date_from', 'date_to', 'company_id', 'operating_unit_id', 'property_build_id', 'property_id', 'product_id')
    def _compute_totals(self):
        for record in self:
            try:
                if not record.company_id:
                    record.total_expenses = 0.0
                    record.total_revenues = 0.0
                    continue

                # جلب بيانات خطوط أوامر البيع حسب الفلاتر
                domain = [('order_id.company_id', '=', record.company_id.id)]
                
                if record.operating_unit_id:
                    domain.append(('property_address_area', '=', record.operating_unit_id.id))
                if record.property_build_id:
                    domain.append(('property_address_build2', '=', record.property_build_id.id))
                if record.property_id:
                    domain.append(('property_number', '=', record.property_id.id))
                if record.product_id:
                    domain.append(('product_id', '=', record.product_id.id))
                if record.date_from:
                    domain.append(('fromdate', '>=', record.date_from))
                if record.date_to:
                    domain.append(('todate', '<=', record.date_to))

                sale_order_lines = self.env['sale.order.line'].search(domain)
                
                # حساب إجمالي المصروفات والإيرادات
                total_expenses = 0.0
                total_revenues = 0.0
                
                for line in sale_order_lines:
                    if line.analytic_account_id:
                        expenses = record._calculate_analytic_amount(line.analytic_account_id, 'expenses')
                        revenues = record._calculate_analytic_amount(line.analytic_account_id, 'revenues')
                        total_expenses += expenses
                        total_revenues += revenues
                
                record.total_expenses = total_expenses
                record.total_revenues = total_revenues
                
            except Exception as e:
                record.total_expenses = 0.0
                record.total_revenues = 0.0

    def _calculate_analytic_amount(self, account, amount_type):
        """حساب المبلغ لحساب تحليلي محدد"""
        try:
            if not account or not account.id:
                return 0.0
                
            base_domain = [
                ('date', '>=', self.date_from),
                ('date', '<=', self.date_to),
                ('company_id', '=', self.company_id.id),
                ('analytic_account_id', '=', account.id),
                ('move_id.state', '=', 'posted')
            ]
            
            if amount_type == 'expenses':
                # المصروفات - البحث في حسابات المصروفات
                domain = base_domain + [
                    ('account_id.internal_group', '=', 'expense')
                ]
                lines = self.env['account.move.line'].search(domain)
                return sum(abs(line.balance) for line in lines if line.balance > 0)
                
            elif amount_type == 'revenues':
                # الإيرادات - البحث في حسابات الإيرادات
                domain = base_domain + [
                    ('account_id.internal_group', '=', 'income')
                ]
                lines = self.env['account.move.line'].search(domain)
                return sum(abs(line.balance) for line in lines if line.balance < 0)
                
            return 0.0
            
        except Exception:
            return 0.0

    def _get_column_width(self, data, column_index, header_text):
        """حساب عرض العمود بناءً على أطول نص"""
        max_length = len(header_text)
        
        for row in data:
            if isinstance(row, dict):
                values = list(row.values())
                if column_index < len(values):
                    cell_value = str(values[column_index]) if values[column_index] else ''
                    max_length = max(max_length, len(cell_value))
            elif isinstance(row, (list, tuple)):
                if column_index < len(row):
                    cell_value = str(row[column_index]) if row[column_index] else ''
                    max_length = max(max_length, len(cell_value))
        
        # إضافة هامش إضافي وحد أقصى/أدنى للعرض
        return min(max(max_length + 2, 8), 50)

    def generate_excel_report(self):
        """إنشاء تقرير Excel محسن مع اللوجو والتنسيق ونظام الشجرة"""
        if not xlsxwriter:
            raise UserError('مكتبة xlsxwriter غير مثبتة. يرجى تثبيتها أولاً.')
        
        data = self._get_report_data()
        
        # ترتيب البيانات حسب التسلسل الهرمي
        sorted_data = sorted(data, key=lambda x: (
            x['company_name'], 
            x['operating_unit'], 
            x['property_build'], 
            x['property_name']
        ))
        
        # إنشاء ملف Excel
        output = io.BytesIO()
        workbook = xlsxwriter.Workbook(output, {'in_memory': True})
        worksheet = workbook.add_worksheet('تقرير الوحدات المؤجرة')
        
        # تنسيقات الخلايا المحسنة
        title_format = workbook.add_format({
            'bold': True,
            'font_size': 16,
            'align': 'center',
            'valign': 'vcenter',
            'bg_color': '#1F4E79',
            'font_color': 'white',
            'border': 2
        })
        
        date_format = workbook.add_format({
            'bold': True,
            'font_size': 11,
            'align': 'center',
            'valign': 'vcenter',
            'bg_color': '#D9E2F3',
            'border': 1
        })
        
        header_format = workbook.add_format({
            'bold': True,
            'bg_color': '#4472C4',
            'font_color': 'white',
            'border': 1,
            'align': 'center',
            'valign': 'vcenter',
            'text_wrap': True
        })
        
        # تنسيقات نظام الشجرة
        company_format = workbook.add_format({
            'bold': True,
            'bg_color': '#E2EFDA',
            'border': 1,
            'align': 'right',
            'valign': 'vcenter',
            'indent': 0
        })
        
        operating_unit_format = workbook.add_format({
            'bold': True,
            'bg_color': '#F2F2F2',
            'border': 1,
            'align': 'right',
            'valign': 'vcenter',
            'indent': 1
        })
        
        property_build_format = workbook.add_format({
            'bg_color': '#FFF2CC',
            'border': 1,
            'align': 'right',
            'valign': 'vcenter',
            'indent': 2
        })
        
        property_format = workbook.add_format({
            'bg_color': '#FCE4D6',
            'border': 1,
            'align': 'right',
            'valign': 'vcenter',
            'indent': 3
        })
        
        unit_format = workbook.add_format({
            'bg_color': '#FFFFFF',
            'border': 1,
            'align': 'center',
            'valign': 'vcenter'
        })
        
        number_format = workbook.add_format({
            'border': 1,
            'align': 'center',
            'valign': 'vcenter',
            'num_format': '#,##0.00'
        })
        
        current_row = 0
        
        # إضافة اللوجو المحسن (في المنتصف، صفين وعامودين)
        try:
            if self.company_id.logo:
                logo_data = base64.b64decode(self.company_id.logo)
                logo_io = io.BytesIO(logo_data)
                
                # حساب موضع المنتصف (عمود 6-7 من أصل 15 عمود)
                logo_col = 6
                worksheet.merge_range(current_row, logo_col, current_row + 1, logo_col + 1, '', workbook.add_format({'border': 0}))
                
                worksheet.insert_image(current_row, logo_col, 'logo.png', {
                    'image_data': logo_io,
                    'x_scale': 0.3,  # حجم أصغر
                    'y_scale': 0.3,
                    'x_offset': 15,
                    'y_offset': 5,
                    'positioning': 1
                })
                current_row += 3  # فراغ تحت اللوجو
        except:
            pass
        
        # عنوان التقرير (حجم أصغر)
        worksheet.merge_range(current_row, 0, current_row, 14, 'تقرير الوحدات المؤجرة', title_format)
        current_row += 2
        
        # معلومات التاريخ والفلاتر
        filter_info = []
        if self.date_from:
            filter_info.append(f"من تاريخ: {self.date_from}")
        if self.date_to:
            filter_info.append(f"إلى تاريخ: {self.date_to}")
        if self.company_id:
            filter_info.append(f"الشركة: {self.company_id.name}")
        if self.operating_unit_id:
            filter_info.append(f"الفرع: {self.operating_unit_id.name}")
        if self.property_build_id:
            filter_info.append(f"المجمع: {self.property_build_id.name}")
        if self.property_id:
            filter_info.append(f"العقار: {self.property_id.property_name}")
        
        if filter_info:
            filter_text = " | ".join(filter_info)
            worksheet.merge_range(current_row, 0, current_row, 14, filter_text, date_format)
            current_row += 2
        
        # تاريخ إنشاء التقرير
        report_date = f"تاريخ إنشاء التقرير: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
        worksheet.merge_range(current_row, 0, current_row, 14, report_date, date_format)
        current_row += 2
        
        # إضافة إجماليات المصروفات والإيرادات
        totals_format = workbook.add_format({
            'bold': True,
            'bg_color': '#FFE699',
            'border': 1,
            'align': 'center',
            'valign': 'vcenter',
            'num_format': '#,##0.00'
        })
        
        worksheet.write(current_row, 0, 'إجمالي المصروفات:', totals_format)
        worksheet.write(current_row, 1, self.total_expenses, totals_format)
        worksheet.write(current_row, 3, 'إجمالي الإيرادات:', totals_format)
        worksheet.write(current_row, 4, self.total_revenues, totals_format)
        current_row += 2
        
        # العناوين
        headers = [
            'الشركة', 'الفرع', 'المجمع', 'العقار', 'الحساب التحليلي', 'الوحدة',
            'اسم العميل', 'رقم العقد', 'حالة الوحدة', 'المبلغ المدفوع',
            'المبلغ المستحق', 'المصروفات', 'الإيرادات', 'تاريخ الاستلام', 'تاريخ التسليم'
        ]
        
        # حساب عرض الأعمدة ديناميكاً
        column_widths = []
        for col, header in enumerate(headers):
            width = self._get_column_width(sorted_data, col, header)
            column_widths.append(width)
            worksheet.write(current_row, col, header, header_format)
        
        current_row += 1
        
        # متغيرات لتتبع القيم السابقة لنظام الشجرة
        prev_company = None
        prev_operating_unit = None
        prev_property_build = None
        prev_property = None
        
        # كتابة البيانات مع نظام الشجرة
        for line_data in sorted_data:
            company_name = line_data['company_name']
            operating_unit = line_data['operating_unit']
            property_build = line_data['property_build']
            property_name = line_data['property_name']
            
            # كتابة الشركة (فقط إذا تغيرت)
            if company_name != prev_company:
                worksheet.write(current_row, 0, company_name, company_format)
                prev_company = company_name
                prev_operating_unit = None
                prev_property_build = None
                prev_property = None
            else:
                worksheet.write(current_row, 0, '', unit_format)
            
            # كتابة الفرع (فقط إذا تغير)
            if operating_unit != prev_operating_unit:
                worksheet.write(current_row, 1, operating_unit, operating_unit_format)
                prev_operating_unit = operating_unit
                prev_property_build = None
                prev_property = None
            else:
                worksheet.write(current_row, 1, '', unit_format)
            
            # كتابة المجمع (فقط إذا تغير)
            if property_build != prev_property_build:
                worksheet.write(current_row, 2, property_build, property_build_format)
                prev_property_build = property_build
                prev_property = None
            else:
                worksheet.write(current_row, 2, '', unit_format)
            
            # كتابة العقار (فقط إذا تغير)
            if property_name != prev_property:
                worksheet.write(current_row, 3, property_name, property_format)
                prev_property = property_name
            else:
                worksheet.write(current_row, 3, '', unit_format)
            
            # باقي البيانات
            worksheet.write(current_row, 4, line_data['analytic_account'], unit_format)
            worksheet.write(current_row, 5, line_data['unit_name'], unit_format)
            worksheet.write(current_row, 6, line_data['customer_name'], unit_format)
            worksheet.write(current_row, 7, line_data['contract_number'], unit_format)
            worksheet.write(current_row, 8, line_data['unit_state'], unit_format)
            worksheet.write(current_row, 9, line_data['amount_paid'], number_format)
            worksheet.write(current_row, 10, line_data['amount_due'], number_format)
            worksheet.write(current_row, 11, line_data['unit_expenses'], number_format)
            worksheet.write(current_row, 12, line_data['unit_revenues'], number_format)
            worksheet.write(current_row, 13, str(line_data['from_date']) if line_data['from_date'] else '', unit_format)
            worksheet.write(current_row, 14, str(line_data['to_date']) if line_data['to_date'] else '', unit_format)
            
            current_row += 1
        
        # ضبط عرض الأعمدة ديناميكياً
        for col, width in enumerate(column_widths):
            col_letter = chr(65 + col)  # A, B, C, etc.
            worksheet.set_column(f'{col_letter}:{col_letter}', width)
        
        # تجميد الصفوف العلوية والعمود الأول
        worksheet.freeze_panes(current_row - len(sorted_data), 1)
        
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
