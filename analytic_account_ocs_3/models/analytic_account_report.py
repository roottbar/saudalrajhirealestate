# -*- coding: utf-8 -*-

from odoo import models, fields, api
from odoo.exceptions import ValidationError
from datetime import timedelta
from collections import defaultdict
import io
import xlsxwriter
import base64
from datetime import datetime
import logging
from reportlab.lib.pagesizes import letter, landscape
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors
from reportlab.lib.units import inch
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

logger = logging.getLogger(__name__)


from odoo.http import request
import base64
import io
import xlsxwriter

class AnalyticAccountReport(models.Model):
    _name = 'analytic.account.report'
    _description = 'تقرير مراكز التكلفة'
    _rec_name = 'group_id'
    _order = 'date_from desc'

    # الحقول الأساسية
    name = fields.Char(string='اسم التقرير', default='تقرير جديد')
    state = fields.Selection([
        ('draft', 'مسودة'),
        ('confirmed', 'مؤكد'),
        ('done', 'منتهي')
    ], string='الحالة', default='draft')
    date_from = fields.Date(string='من تاريخ', default=fields.Date.today(), required=True)
    date_to = fields.Date(string='إلى تاريخ', default=fields.Date.today(), required=True)
    company_ids = fields.Many2many(
        'res.company', 
        string='الشركات',
        default=lambda self: [self.env.company.id]
    )
    company_id = fields.Many2one(
        'res.company', 
        string='Company',
        compute='_compute_main_company',
        store=True
    )

    # حقول العلاقات
    group_id = fields.Many2one(
        'account.analytic.group',
        string='مجموعة مراكز التكلفة',
        domain="[('company_id', 'in', company_ids)]"
    )

    analytic_account_id = fields.Many2one(
        'account.analytic.account',
        string='مركز التكلفة',
        domain="[('company_id', 'in', company_ids), ('group_id', '=?', group_id)]"
    )
    
    company_currency_id = fields.Many2one(
        'res.currency', 
        string='العملة',
        compute='_compute_company_currency',
        store=True
    )

    # الحقول المحسوبة
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
    total_collections = fields.Monetary(
        string='إجمالي التحصيل (المدفوعات)',
        currency_field='company_currency_id',
        compute='_compute_totals'
    )
    total_debts = fields.Monetary(
        string='إجمالي المديونية (المتبقي)',
        currency_field='company_currency_id',
        compute='_compute_totals'
    )
    report_lines = fields.Html(
        string='تفاصيل التقرير',
        compute='_compute_report_lines',
        store=True,
        sanitize=False
    )
    analytic_account_ids = fields.Many2many(
        'account.analytic.account', 
        string='Analytic Accounts',
        compute='_compute_analytic_accounts',
        store=True
    )

    # def action_generate_excel_report(self):
    #     output = io.BytesIO()
    #     workbook = xlsxwriter.Workbook(output, {'in_memory': True})
    #     worksheet = workbook.add_worksheet('تقرير مراكز التكلفة')
    #     # مثال: كتابة رؤوس الأعمدة
    #     worksheet.write(0, 0, 'الاسم')
    #     worksheet.write(0, 1, 'الإيرادات')
    #     worksheet.write(0, 2, 'المصروفات')
    #     # مثال: كتابة بيانات التقرير
    #     row = 1
    #     for rec in self:
    #         worksheet.write(row, 0, rec.name)
    #         worksheet.write(row, 1, rec.total_revenues)
    #         worksheet.write(row, 2, rec.total_expenses)
    #         row += 1
    #     workbook.close()
    #     output.seek(0)
    #     file_data = output.read()
    #     output.close()
    #     attachment = self.env['ir.attachment'].create({
    #         'name': 'تقرير مراكز التكلفة.xlsx',
    #         'type': 'binary',
    #         'datas': base64.b64encode(file_data),
    #         'res_model': self._name,
    #         'res_id': self.id,
    #         'mimetype': 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    #     })
    #     download_url = '/web/content/%s?download=true' % (attachment.id)
    #     return {
    #         'type': 'ir.actions.act_url',
    #         'url': download_url,
    #         'target': 'new',
    #     }

    @api.depends('company_ids')
    def _compute_main_company(self):
        for record in self:
            # إذا كان هناك شركة واحدة فقط، استخدمها
            if record.company_ids and len(record.company_ids) == 1:
                record.company_id = record.company_ids[0]
            # إذا كان هناك عدة شركات، استخدم الأولى
            elif record.company_ids and len(record.company_ids) > 1:
                record.company_id = record.company_ids[0]
            else:
                # تجنب استعلامات قاعدة البيانات أثناء المعاملات الفاشلة
                # ببساطة اتركه فارغاً أو استخدم قيمة افتراضية
                record.company_id = False

    @api.depends('company_ids')
    def _compute_company_currency(self):
        for record in self:
            try:
                # Initialize with default company currency
                default_currency = self.env.company.currency_id
            except Exception:
                # Fallback to base currency if company access fails
                default_currency = self.env['res.currency'].search([('name', '=', 'USD')], limit=1)
                if not default_currency:
                    default_currency = self.env['res.currency'].search([], limit=1)
            
            record.company_currency_id = default_currency
            
            # Only proceed if we have valid company_ids
            if not record.company_ids:
                continue
                
            try:
                # Safely get the first valid company
                valid_companies = [c for c in record.company_ids if c._name == 'res.company' and c.id]
                if valid_companies:
                    record.company_currency_id = valid_companies[0].currency_id
            except Exception as e:
                logger.error("Error computing company currency: %s", str(e))
                # Keep the default currency set above

    @api.depends('group_id', 'analytic_account_id', 'company_ids')
    def _compute_analytic_accounts(self):
        for record in self:
            try:
                domain = []
                
                # Add company filter if available - safely handle company_ids
                if record.company_ids:
                    company_ids = [c.id for c in record.company_ids if hasattr(c, 'id') and c.id]
                    if company_ids:
                        # Check if analytic account has company_id field
                        account_model = self.env['account.analytic.account']
                        if hasattr(account_model, '_fields') and 'company_id' in account_model._fields:
                            domain.append(('company_id', 'in', company_ids))

                # Remove branch filter - no longer needed
                        
                # Add group filter if available
                if record.group_id and hasattr(record.group_id, 'id') and record.group_id.id:
                    domain.append(('group_id', '=', record.group_id.id))
                    
                # Add specific account filter if available
                if record.analytic_account_id and hasattr(record.analytic_account_id, 'id') and record.analytic_account_id.id:
                    domain.append(('id', '=', record.analytic_account_id.id))

                # If no domain, get all analytic accounts
                if not domain:
                    domain = []

                analytic_accounts = self.env['account.analytic.account'].search(domain)
                record.analytic_account_ids = analytic_accounts
            except Exception as e:
                logger.error("Error computing analytic accounts: %s", str(e))
                record.analytic_account_ids = self.env['account.analytic.account']

    @api.depends('date_from', 'date_to', 'company_ids', 'analytic_account_ids')
    def _compute_totals(self):
        for record in self:
            try:
                if not record.company_ids or not record.analytic_account_ids:
                    record.total_expenses = 0.0
                    record.total_revenues = 0.0
                    record.total_collections = 0.0
                    record.total_debts = 0.0
                    continue

                company_ids = [c.id for c in record.company_ids if hasattr(c, 'id') and c.id]
                analytic_account_ids = [a.id for a in record.analytic_account_ids if hasattr(a, 'id') and a.id]
                
                if not company_ids or not analytic_account_ids:
                    record.total_expenses = 0.0
                    record.total_revenues = 0.0
                    record.total_collections = 0.0
                    record.total_debts = 0.0
                    continue

                # البحث عن جميع القيود المحاسبية في الفترة المحددة
                domain = [
                    ('date', '>=', record.date_from),
                    ('date', '<=', record.date_to),
                    ('company_id', 'in', company_ids),
                    ('move_id.state', '=', 'posted'),
                    ('analytic_account_id', 'in', analytic_account_ids)
                ]
                
                move_lines = self.env['account.move.line'].search(domain)
                
                logger.info(f"عدد القيود الموجودة: {len(move_lines)}")
                
                # حساب المصروفات والإيرادات من الرصيد
                total_expenses = 0.0
                total_revenues = 0.0
                
                for line in move_lines:
                    if line.balance < 0:  # مصروفات (رصيد سالب)
                        total_expenses += abs(line.balance)
                    elif line.balance > 0:  # إيرادات (رصيد موجب)
                        total_revenues += line.balance
                
                # حساب المحصلات (المدفوعات)
                payment_domain = [
                    ('date', '>=', record.date_from),
                    ('date', '<=', record.date_to),
                    ('company_id', 'in', company_ids),
                    ('move_id.state', '=', 'posted'),
                    ('analytic_account_id', 'in', analytic_account_ids),
                    ('move_id.move_type', 'in', ['out_payment', 'in_payment'])
                ]
                
                payment_lines = self.env['account.move.line'].search(payment_domain)
                total_collections = sum(abs(line.balance) for line in payment_lines)
                
                # حساب الديون (الفواتير غير المدفوعة)
                invoice_domain = [
                    ('date', '>=', record.date_from),
                    ('date', '<=', record.date_to),
                    ('company_id', 'in', company_ids),
                    ('move_id.state', '=', 'posted'),
                    ('analytic_account_id', 'in', analytic_account_ids),
                    ('move_id.move_type', 'in', ['out_invoice', 'in_invoice']),
                    ('move_id.payment_state', 'in', ['not_paid', 'partial'])
                ]
                
                debt_lines = self.env['account.move.line'].search(invoice_domain)
                total_debts = sum(line.amount_residual for line in debt_lines if line.amount_residual > 0)
                
                # تسجيل النتائج
                logger.info(f"المصروفات: {total_expenses}")
                logger.info(f"الإيرادات: {total_revenues}")
                logger.info(f"المحصلات: {total_collections}")
                logger.info(f"الديون: {total_debts}")
                
                record.total_expenses = total_expenses
                record.total_revenues = total_revenues
                record.total_collections = total_collections
                record.total_debts = total_debts
                    
            except Exception as e:
                logger.error("خطأ في حساب الإجماليات: %s", str(e))
                record.total_expenses = 0.0
                record.total_revenues = 0.0
                record.total_collections = 0.0
                record.total_debts = 0.0

    @api.depends('date_from', 'date_to', 'company_ids', 'analytic_account_ids')
    def _compute_report_lines(self):
        for record in self:
            try:
                if len(record.analytic_account_ids) > 100:
                    record.report_lines = "<p>عدد مراكز التكلفة كبير جداً. يرجى تحديد فلاتر أكثر تحديداً.</p>"
                    continue
                
                company_ids = [c.id for c in record.company_ids if c._name == 'res.company' and c.id] if record.company_ids else []
                
                # إضافة تسجيل للتشخيص
                logger.info(f"Computing report lines for {len(record.analytic_account_ids)} accounts, {len(company_ids)} companies")
                
                html_lines = []
                html_lines.append("""
                    <style>
                        .total-row { background-color: #f2f2f2; font-weight: bold; }
                        .section-row { background-color: #e6f2ff; font-weight: bold; }
                        .table { width: 100%; border-collapse: collapse; direction: rtl; }
                        .table th { padding: 8px; border: 1px solid #ddd; background-color: #4472C4; color: white; }
                        .table td { padding: 8px; border: 1px solid #ddd; }
                        .text-right { text-align: right; }
                        .text-center { text-align: center; }
                        .document-link { color: #4472C4; text-decoration: none; }
                        .document-link:hover { text-decoration: underline; }
                    </style>
                    <table class="table">
                        <thead>
                            <tr>
                                <th>مركز التكلفة</th>
                                <th>المجموعة</th>
                                <th>الشريك</th>
                                <th>المصروفات</th>
                                <th>الإيرادات</th>
                                <th>التحصيل (المدفوعات)</th>
                                <th>المديونية (المتبقي)</th>
                            </tr>
                        </thead>
                        <tbody>
                """)

                if not record.analytic_account_ids or not company_ids:
                    record.report_lines = "<p>لا توجد بيانات لعرضها. تأكد من اختيار مراكز التكلفة والشركات.</p>"
                    continue
                    
                analytic_account_ids = [a.id for a in record.analytic_account_ids if a._name == 'account.analytic.account' and a.id]
                if not analytic_account_ids:
                    record.report_lines = "<p>لا توجد مراكز تكلفة صالحة</p>"
                    continue
                    
                # جلب جميع البيانات مرة واحدة مع تحسين الاستعلام
                base_domain = [
                    ('date', '>=', record.date_from),
                    ('date', '<=', record.date_to),
                    ('company_id', 'in', company_ids),
                    ('move_id.state', '=', 'posted'),
                    ('analytic_account_id', 'in', analytic_account_ids),
                    ('analytic_account_id', '!=', False)  # تأكد من وجود مركز تكلفة
                ]
                
                all_lines = self.env['account.move.line'].search(base_domain)
                logger.info(f"Found {len(all_lines)} account move lines matching criteria")
                
                # تجميع البيانات حسب مركز التكلفة
                account_data = {}
                for line in all_lines:
                    account_id = line.analytic_account_id.id
                    if account_id not in account_data:
                        account_data[account_id] = {
                            'expenses': 0.0,
                            'revenues': 0.0,
                            'collections': 0.0,
                            'debts': 0.0
                        }
                    
                    # حساب المصروفات والإيرادات
                    if line.balance < 0:
                        account_data[account_id]['expenses'] += abs(line.balance)
                    elif line.balance > 0:
                        account_data[account_id]['revenues'] += line.balance
                        
                    # حساب التحصيل - تحسين المنطق
                    if line.move_id.move_type in ['out_payment', 'in_payment'] or \
                       (line.move_id.move_type in ['out_invoice', 'in_invoice'] and line.move_id.payment_state == 'paid'):
                        account_data[account_id]['collections'] += abs(line.balance)
                        
                    # حساب المديونية
                    if line.move_id.move_type in ['out_invoice', 'in_invoice'] and \
                       line.move_id.payment_state in ['not_paid', 'partial'] and \
                       line.amount_residual > 0:
                        account_data[account_id]['debts'] += line.amount_residual

                # تجميع النتائج حسب المجموعة ومركز التكلفة
                group_dict = defaultdict(lambda: {
                    'accounts': [],
                    'total_expenses': 0.0,
                    'total_revenues': 0.0,
                    'total_collections': 0.0,
                    'total_debts': 0.0
                })

                for account in record.analytic_account_ids:
                    data = account_data.get(account.id, {
                        'expenses': 0.0,
                        'revenues': 0.0,
                        'collections': 0.0,
                        'debts': 0.0
                    })
                    
                    partner = account.partner_id or False

                    group_dict[account.group_id]['accounts'].append({
                        'account': account,
                        'partner': partner,
                        'expenses': data['expenses'],
                        'revenues': data['revenues'],
                        'collections': data['collections'],
                        'debts': data['debts']
                    })

                    group_dict[account.group_id]['total_expenses'] += data['expenses']
                    group_dict[account.group_id]['total_revenues'] += data['revenues']
                    group_dict[account.group_id]['total_collections'] += data['collections']
                    group_dict[account.group_id]['total_debts'] += data['debts']

                # عرض النتائج حسب المجموعة
                for group, data in group_dict.items():
                    if not group:
                        continue

                    html_lines.append(f"""
                        <tr class="section-row">
                            <td colspan="7">{group.name}</td>
                        </tr>
                    """)

                    for account_data in data['accounts']:
                        account = account_data['account']
                        partner_name = account_data['partner'].name if account_data['partner'] else ''
                        html_lines.append(f"""
                            <tr>
                                <td>{account.name}</td>
                                <td>{account.group_id.name if account.group_id else ''}</td>
                                <td>{partner_name}</td>
                                <td class="text-right">{format(account_data['expenses'], '.2f')}</td>
                                <td class="text-right">{format(account_data['revenues'], '.2f')}</td>
                                <td class="text-right">{format(account_data['collections'], '.2f')}</td>
                                <td class="text-right">{format(account_data['debts'], '.2f')}</td>
                            </tr>
                        """)

                    html_lines.append(f"""
                        <tr class="total-row">
                            <td colspan="3">إجمالي المجموعة</td>
                            <td class="text-right">{format(data['total_expenses'], '.2f')}</td>
                            <td class="text-right">{format(data['total_revenues'], '.2f')}</td>
                            <td class="text-right">{format(data['total_collections'], '.2f')}</td>
                            <td class="text-right">{format(data['total_debts'], '.2f')}</td>
                        </tr>
                    """)

                html_lines.append(f"""
                    <tr class="total-row">
                        <td colspan="3">الإجمالي العام</td>
                        <td class="text-right">{format(record.total_expenses, '.2f')}</td>
                        <td class="text-right">{format(record.total_revenues, '.2f')}</td>
                        <td class="text-right">{format(record.total_collections, '.2f')}</td>
                        <td class="text-right">{format(record.total_debts, '.2f')}</td>
                    </tr>
                """)

                html_lines.append("""
                        </tbody>
                    </table>
                """)

                record.report_lines = '\n'.join(html_lines)
            except Exception as e:
                logger.error("Error computing report lines: %s", str(e))
                record.report_lines = "<p>حدث خطأ أثناء توليد التقرير</p>"

    @api.onchange('company_ids')
    def _onchange_company_ids(self):
        for record in self:
            try:
                if not record.company_ids:
                    continue

                company_ids = [c.id for c in record.company_ids if hasattr(c, 'id') and c.id]
                if not company_ids:
                    continue

                # Remove branch handling - no longer needed

                if record.group_id and hasattr(record.group_id, 'id') and record.group_id.id:
                    if not hasattr(record.group_id, 'company_id') or not record.group_id.company_id:
                        record.group_id = False
                    elif record.group_id.company_id.id not in company_ids:
                        record.group_id = False

                if record.analytic_account_id and hasattr(record.analytic_account_id, 'id') and record.analytic_account_id.id:
                    if not hasattr(record.analytic_account_id, 'company_id') or not record.analytic_account_id.company_id:
                        record.analytic_account_id = False
                    elif record.analytic_account_id.company_id.id not in company_ids:
                        record.analytic_account_id = False

            except Exception as e:
                logger.error("Error in _onchange_company_ids: %s", str(e))

    @api.onchange('group_id')
    def _onchange_group_id(self):
        for record in self:
            try:
                if record.group_id and record.analytic_account_id:
                    if record.analytic_account_id.group_id != record.group_id:
                        record.analytic_account_id = False
            except Exception as e:
                logger.error("Error in _onchange_group_id: %s", str(e))
                record.analytic_account_id = False

    @api.constrains('company_ids', 'group_id', 'analytic_account_id')
    def _check_company_consistency(self):
        for record in self:
            if not record.company_ids:
                continue
                
            company_ids = [c.id for c in record.company_ids if hasattr(c, 'id') and c.id]
            if not company_ids:
                continue

            # Remove branch validation - no longer needed

            if record.group_id and hasattr(record.group_id, 'id') and record.group_id.id:
                if not hasattr(record.group_id, 'company_id') or not record.group_id.company_id:
                    raise ValidationError("المجموعة المحددة لا تحتوي على شركة")
                elif record.group_id.company_id.id not in company_ids:
                    raise ValidationError("المجموعة المحددة لا تنتمي لأي من الشركات المحددة")
                    
            if record.analytic_account_id and record.analytic_account_id.id:
                if record.analytic_account_id.company_id.id not in company_ids:
                    raise ValidationError("مركز التكلفة المحدد لا ينتمي لأي من الشركات المحددة")

    @api.onchange('date_from')
    def _onchange_date_from(self):
        if self.date_from and not self.date_to:
            self.date_to = self.date_from

    @api.constrains('date_from', 'date_to')
    def _check_dates(self):
        for record in self:
            if record.date_from and record.date_to and record.date_from > record.date_to:
                raise ValidationError("تاريخ البداية يجب أن يكون قبل تاريخ النهاية")
    def generate_excel_report(self):
        """إنشاء تقرير Excel لتقرير مراكز التكلفة"""
        self.ensure_one()
        # إنشاء كتاب Excel
        output = io.BytesIO()
        workbook = xlsxwriter.Workbook(output, {
            'in_memory': True,
            'right_to_left': True,
            'strings_to_numbers': True,
            'remove_timezone': True
        })
        
        # إعداد التنسيقات
        title_format = workbook.add_format({
            'bold': True,
            'font_size': 16,
            'align': 'center',
            'valign': 'vcenter',
            'font_color': '#4472C4',
            'border': 1
        })
        
        header_format = workbook.add_format({
            'bold': True,
            'font_size': 12,
            'align': 'center',
            'valign': 'vcenter',
            'bg_color': '#4472C4',
            'font_color': 'white',
            'border': 1,
            'text_wrap': True
        })
        
        currency_format = workbook.add_format({
            'num_format': '#,##0.00',
            'border': 1,
            'align': 'right',
            'font_size': 10
        })
        
        text_format = workbook.add_format({
            'border': 1,
            'align': 'right',
            'font_size': 10
        })
        
        total_format = workbook.add_format({
            'bold': True,
            'num_format': '#,##0.00',
            'border': 1,
            'align': 'right',
            'bg_color': '#D9E1F2',
            'font_size': 10
        })
        
        section_format = workbook.add_format({
            'bold': True,
            'border': 1,
            'align': 'right',
            'bg_color': '#E6F2FF',
            'font_size': 10
        })
        
        label_format = workbook.add_format({
            'bold': True,
            'border': 1,
            'align': 'right',
            'font_size': 10
        })
    
        worksheet = workbook.add_worksheet('تقرير مراكز التكلفة')
        worksheet.right_to_left()
        
        # إعداد أعمدة الورقة
        worksheet.set_column('A:A', 25)  # عمود المجموعة/مركز التكلفة
        worksheet.set_column('B:B', 15)  # عمود المصروفات
        worksheet.set_column('C:C', 15)  # عمود الإيرادات
        worksheet.set_column('D:D', 15)  # عمود التحصيل
        worksheet.set_column('E:E', 15)  # عمود المديونية
        
        # بدء كتابة البيانات
        row = 0
        
        # إضافة عنوان التقرير
        worksheet.merge_range(row, 0, row, 4, 'تقرير مراكز التكلفة', title_format)
        row += 1
        
        # إضافة معلومات الشركة والفترة الزمنية
        if self.company_id:
            worksheet.merge_range(row, 0, row, 4, 
                                f'الشركة: {self.company_id.name}', 
                                workbook.add_format({
                                    'align': 'center',
                                    'font_size': 12,
                                    'border': 0
                                }))
            row += 1
        
        if self.group_id:
            worksheet.merge_range(row, 0, row, 4, 
                                f'المجموعة: {self.group_id.name}', 
                                workbook.add_format({
                                    'align': 'center',
                                    'font_size': 12,
                                    'border': 0
                                }))
            row += 1
        
        worksheet.merge_range(row, 0, row, 4,
                             f'من {self.date_from} إلى {self.date_to}',
                             workbook.add_format({
                                 'align': 'center',
                                 'font_size': 12,
                                 'border': 0
                             }))
        row += 2
        
        # إضافة ملخص التقرير
        worksheet.write(row, 0, 'إجمالي المصروفات', label_format)
        worksheet.write(row, 1, self.total_expenses, currency_format)
        row += 1
        
        worksheet.write(row, 0, 'إجمالي الإيرادات', label_format)
        worksheet.write(row, 1, self.total_revenues, currency_format)
        row += 1
        
        worksheet.write(row, 0, 'إجمالي التحصيل (المدفوعات)', label_format)
        worksheet.write(row, 1, self.total_collections, currency_format)
        row += 1
        
        worksheet.write(row, 0, 'إجمالي المديونية (المتبقي)', label_format)
        worksheet.write(row, 1, self.total_debts, currency_format)
        row += 2
        
        # عناوين الأعمدة
        headers = [
            'مركز التكلفة',
            'المصروفات',
            'الإيرادات',
            'التحصيل (المدفوعات)',
            'المديونية (المتبقي)'
        ]
        
        for col, header in enumerate(headers):
            worksheet.write(row, col, header, header_format)
        row += 1
        
        # جلب البيانات من قاعدة البيانات
        analytic_domain = [('company_id', 'in', self.company_ids.ids)]
        if self.group_id:
            analytic_domain.append(('group_id', '=', self.group_id.id))
        if self.analytic_account_ids:
            analytic_domain.append(('id', 'in', self.analytic_account_ids.ids))
        
        analytic_accounts = self.env['account.analytic.account'].search(analytic_domain, order='group_id, name')
        
        # تجميع البيانات حسب المجموعة
        groups = {}
        for account in analytic_accounts:
            group_name = account.group_id.name if account.group_id else 'بدون مجموعة'
            if group_name not in groups:
                groups[group_name] = []
            groups[group_name].append(account)
        
        # كتابة البيانات في Excel
        for group_name, accounts in groups.items():
            group_expenses = 0
            group_revenues = 0
            group_collections = 0
            group_debts = 0
            
            # عنوان المجموعة
            worksheet.write(row, 0, group_name, section_format)
            worksheet.merge_range(row, 1, row, 4, '', section_format)
            row += 1
            
            # بيانات كل حساب
            for account in accounts:
                # حساب القيم لكل حساب تحليلي
                expenses = self._calculate_analytic_amount(account, 'expenses')
                revenues = self._calculate_analytic_amount(account, 'revenues')
                collections = self._calculate_analytic_amount(account, 'collections')
                debts = self._calculate_analytic_amount(account, 'debts')
                
                worksheet.write(row, 0, account.name, text_format)
                worksheet.write(row, 1, expenses, currency_format)
                worksheet.write(row, 2, revenues, currency_format)
                worksheet.write(row, 3, collections, currency_format)
                worksheet.write(row, 4, debts, currency_format)
                row += 1
                
                # تجميع إجماليات المجموعة
                group_expenses += expenses
                group_revenues += revenues
                group_collections += collections
                group_debts += debts
            
            # إجمالي المجموعة
            worksheet.write(row, 0, 'إجمالي المجموعة', total_format)
            worksheet.write(row, 1, group_expenses, total_format)
            worksheet.write(row, 2, group_revenues, total_format)
            worksheet.write(row, 3, group_collections, total_format)
            worksheet.write(row, 4, group_debts, total_format)
            row += 1
        
        # الإجمالي العام
        worksheet.write(row, 0, 'الإجمالي العام', total_format)
        worksheet.write(row, 1, self.total_expenses, total_format)
        worksheet.write(row, 2, self.total_revenues, total_format)
        worksheet.write(row, 3, self.total_collections, total_format)
        worksheet.write(row, 4, self.total_debts, total_format)
        
        # إغلاق الكتاب
        workbook.close()
        output.seek(0)
        
        return {
            'file_name': f"تقرير_مراكز_التكلفة_{self.date_from}_إلى_{self.date_to}.xlsx",
            'file_content': output.read(),
            'file_type': 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        }

    def _calculate_analytic_amount(self, account, amount_type):
        """حساب المبالغ لكل حساب تحليلي"""
        domain = [
            ('date', '>=', self.date_from),
            ('date', '<=', self.date_to),
            ('company_id', 'in', self.company_ids.ids),
            ('move_id.state', '=', 'posted'),
            ('analytic_account_id', '=', account.id)
        ]
        
        # إضافة تسجيل للتشخيص
        logger.info(f"Calculating {amount_type} for account {account.name} with domain: {domain}")
        
        if amount_type == 'expenses':
            domain.append(('balance', '<', 0))
            lines = self.env['account.move.line'].search(domain)
            result = abs(sum(lines.mapped('balance')))
            logger.info(f"Expenses for {account.name}: {result} (from {len(lines)} lines)")
            return result
        
        elif amount_type == 'revenues':
            domain.append(('balance', '>', 0))
            lines = self.env['account.move.line'].search(domain)
            result = sum(lines.mapped('balance'))
            logger.info(f"Revenues for {account.name}: {result} (from {len(lines)} lines)")
            return result
        
        elif amount_type == 'collections':
            # تصحيح منطق التحصيل - البحث عن المدفوعات الفعلية
            domain_payments = domain + [
                ('move_id.move_type', 'in', ['out_payment', 'in_payment']),
                ('balance', '!=', 0)
            ]
            payment_lines = self.env['account.move.line'].search(domain_payments)
            
            # أو البحث عن الفواتير المدفوعة
            domain_paid_invoices = domain + [
                ('move_id.move_type', 'in', ['out_invoice', 'in_invoice']),
                ('move_id.payment_state', '=', 'paid'),
                ('balance', '!=', 0)
            ]
            paid_invoice_lines = self.env['account.move.line'].search(domain_paid_invoices)
            
            result = abs(sum(payment_lines.mapped('balance'))) + abs(sum(paid_invoice_lines.mapped('balance')))
            logger.info(f"Collections for {account.name}: {result} (payments: {len(payment_lines)}, paid invoices: {len(paid_invoice_lines)})")
            return result
        
        elif amount_type == 'debts':
            domain += [
                ('move_id.move_type', 'in', ['out_invoice', 'in_invoice']),
                ('move_id.payment_state', 'in', ['not_paid', 'partial']),
                ('amount_residual', '>', 0)
            ]
            lines = self.env['account.move.line'].search(domain)
            result = sum(lines.mapped('amount_residual'))
            logger.info(f"Debts for {account.name}: {result} (from {len(lines)} lines)")
            return result
        
        return 0.0

    def generate_pdf_report(self):
        """إنشاء تقرير PDF لتقرير مراكز التكلفة"""
        self.ensure_one()
        try:
            # إنشاء مستند PDF
            output = io.BytesIO()
            doc = SimpleDocTemplate(output, pagesize=landscape(letter), rightMargin=20, leftMargin=20, topMargin=30,
                                    bottomMargin=30)

            # تسجيل خط عربي إذا لزم الأمر
            try:
                pdfmetrics.registerFont(TTFont('Arabic', 'arial.ttf'))
            except:
                logger.warning("Failed to register Arabic font, using default")

            # أنماط النص
            styles = getSampleStyleSheet()
            title_style = ParagraphStyle(
                'Title',
                parent=styles['Title'],
                fontName='Arabic',
                fontSize=16,
                alignment=1,  # 1=center
                textColor=colors.HexColor('#4472C4')
            )

            header_style = ParagraphStyle(
                'Header',
                parent=styles['Normal'],
                fontName='Arabic',
                fontSize=12,
                alignment=1,  # 1=center
                textColor=colors.white,
                backColor=colors.HexColor('#4472C4')
            )

            normal_style = ParagraphStyle(
                'Normal',
                parent=styles['Normal'],
                fontName='Arabic',
                fontSize=10,
                alignment=2  # 2=right
            )

            currency_style = ParagraphStyle(
                'Currency',
                parent=styles['Normal'],
                fontName='Arabic',
                fontSize=10,
                alignment=2  # 2=right
            )

            total_style = ParagraphStyle(
                'Total',
                parent=styles['Normal'],
                fontName='Arabic',
                fontSize=10,
                alignment=2,  # 2=right
                fontWeight='bold',
                backColor=colors.HexColor('#D9E1F2')
            )

            section_style = ParagraphStyle(
                'Section',
                parent=styles['Normal'],
                fontName='Arabic',
                fontSize=10,
                alignment=2,  # 2=right
                fontWeight='bold',
                backColor=colors.HexColor('#E6F2FF')
            )

            # عناصر التقرير
            elements = []

            # إضافة عنوان التقرير
            title = Paragraph("تقرير مراكز التكلفة", title_style)
            elements.append(title)

            # إضافة معلومات الشركات المختارة
            if self.company_ids:
                companies = ", ".join(self.company_ids.mapped('name'))
                company_info = Paragraph(f"الشركات: {companies}", normal_style)
                elements.append(company_info)

            # Remove branch handling - no longer needed

            # إضافة معلومات المجموعة
            if self.group_id:
                group_info = Paragraph(f"المجموعة: {self.group_id.name}", normal_style)
                elements.append(group_info)

            # إضافة الفترة الزمنية
            date_range = Paragraph(f"من {self.date_from} إلى {self.date_to}", normal_style)
            elements.append(date_range)

            elements.append(Spacer(1, 20))

            # إضافة ملخص التقرير
            summary_data = [
                ['إجمالي المصروفات', format(round(self.total_expenses, 2), ',.2f')],
                ['إجمالي الإيرادات', format(round(self.total_revenues, 2), ',.2f')],
                ['إجمالي التحصيل (المدفوعات)', format(round(self.total_collections, 2), ',.2f')],
                ['إجمالي المديونية (المتبقي)', format(round(self.total_debts, 2), ',.2f')]
            ]

            summary_table = Table(summary_data, colWidths=[200, 100])
            summary_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor('#f2f2f2')),
                ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
                ('ALIGN', (0, 0), (-1, -1), 'RIGHT'),
                ('FONTNAME', (0, 0), (-1, -1), 'Arabic'),
                ('FONTSIZE', (0, 0), (-1, -1), 10),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 5),
                ('TOPPADDING', (0, 0), (-1, -1), 5),
                ('GRID', (0, 0), (-1, -1), 1, colors.black)
            ]))

            elements.append(summary_table)
            elements.append(Spacer(1, 20))

            # إضافة تفاصيل التقرير
            report_header = [
                'المجموعة',
                'مركز التكلفة',
                'الشريك',
                'المصروفات',
                'الإيرادات',
                'التحصيل (المدفوعات)',
                'المديونية (المتبقي)'
            ]

            report_data = [report_header]

            # البحث عن جميع مراكز التكلفة المطلوبة
            company_ids = [c.id for c in self.company_ids if c._name == 'res.company' and c.id]
            if not company_ids:
                return {
                    'file_name': f"تقرير_مراكز_التكلفة_{self.date_from}_إلى_{self.date_to}.pdf",
                    'file_content': b'',
                    'file_type': 'application/pdf'
                }
            
            analytic_domain = [('company_id', 'in', company_ids)]
            
            # Remove branch handling - no longer needed
            if self.group_id and self.group_id.id:
                analytic_domain.append(('group_id', '=', self.group_id.id))
            if self.analytic_account_ids:
                analytic_account_ids = [a.id for a in self.analytic_account_ids if a._name == 'account.analytic.account' and a.id]
                if analytic_account_ids:
                    analytic_domain.append(('id', 'in', analytic_account_ids))

            analytic_accounts = self.env['account.analytic.account'].search(analytic_domain)

            # تجميع النتائج حسب المجموعة
            group_dict = defaultdict(lambda: {
                'accounts': [],
                'total_expenses': 0.0,
                'total_revenues': 0.0,
                'total_collections': 0.0,
                'total_debts': 0.0
            })

            for account in analytic_accounts:
                # حساب المصروفات لهذا المركز
                expenses_domain = [
                    ('date', '>=', self.date_from),
                    ('date', '<=', self.date_to),
                    ('company_id', 'in', company_ids),
                    ('move_id.state', '=', 'posted'),
                    ('analytic_account_id', '=', account.id),
                    ('balance', '<', 0)
                ]
                # Remove branch handling - no longer needed
                expense_lines = self.env['account.move.line'].search(expenses_domain)
                account_expenses = abs(sum(line.balance for line in expense_lines))

                # حساب الإيرادات لهذا المركز
                revenues_domain = [
                    ('date', '>=', self.date_from),
                    ('date', '<=', self.date_to),
                    ('company_id', 'in', company_ids),
                    ('move_id.state', '=', 'posted'),
                    ('analytic_account_id', '=', account.id),
                    ('balance', '>', 0)
                ]
                # Remove branch handling - no longer needed
                revenue_lines = self.env['account.move.line'].search(revenues_domain)
                account_revenues = sum(line.balance for line in revenue_lines)

                # حساب التحصيل لهذا المركز
                payments_domain = [
                    ('date', '>=', self.date_from),
                    ('date', '<=', self.date_to),
                    ('company_id', 'in', company_ids),
                    ('move_id.state', '=', 'posted'),
                    ('analytic_account_id', '=', account.id),
                    ('payment_id', '!=', False)
                ]
                # Remove branch handling - no longer needed
                payment_lines = self.env['account.move.line'].search(payments_domain)
                account_collections = abs(sum(line.balance for line in payment_lines))

                # حساب المديونية لهذا المركز
                invoices_domain = [
                    ('date', '>=', self.date_from),
                    ('date', '<=', self.date_to),
                    ('company_id', 'in', company_ids),
                    ('move_id.state', '=', 'posted'),
                    ('analytic_account_id', '=', account.id),
                    ('move_id.move_type', 'in', ['out_invoice', 'in_invoice']),
                    ('move_id.payment_state', '!=', 'paid'),
                    ('balance', '>', 0)
                ]
                # Remove branch handling - no longer needed
                invoice_lines = self.env['account.move.line'].search(invoices_domain)
                account_debts = sum(line.amount_residual for line in invoice_lines)

                # الحصول على الشريك من حساب التحليلي
                partner = account.partner_id or False

                # تخزين النتائج
                group_dict[account.group_id]['accounts'].append({
                    'account': account,
                    'partner': partner,
                    'expenses': account_expenses,
                    'revenues': account_revenues,
                    'collections': account_collections,
                    'debts': account_debts
                })

                # تحديث إجماليات المجموعة
                group_dict[account.group_id]['total_expenses'] += account_expenses
                group_dict[account.group_id]['total_revenues'] += account_revenues
                group_dict[account.group_id]['total_collections'] += account_collections
                group_dict[account.group_id]['total_debts'] += account_debts

            # عرض النتائج حسب المجموعة
            for group, data in group_dict.items():
                # عنوان المجموعة
                report_data.append([
                    group.name if group else 'بدون مجموعة', '', '', '', '', '', ''
                ])

                # تفاصيل مراكز التكلفة في هذه المجموعة
                for account_data in data['accounts']:
                    account = account_data['account']
                    partner_name = account_data['partner'].name if account_data['partner'] else ''
                    report_data.append([
                        '',
                        account.name,
                        partner_name,
                        format(round(account_data['expenses'], 2), ',.2f'),
                        format(round(account_data['revenues'], 2), ',.2f'),
                        format(round(account_data['collections'], 2), ',.2f'),
                        format(round(account_data['debts'], 2), ',.2f')
                    ])

                # إجمالي المجموعة
                report_data.append([
                    '',
                    'إجمالي المجموعة',
                    '',
                    format(round(data['total_expenses'], 2), ',.2f'),
                    format(round(data['total_revenues'], 2), ',.2f'),
                    format(round(data['total_collections'], 2), ',.2f'),
                    format(round(data['total_debts'], 2), ',.2f')
                ])

            # إجمالي عام
            report_data.append([
                '',
                'الإجمالي العام',
                '',
                format(round(self.total_expenses, 2), ',.2f'),
                format(round(self.total_revenues, 2), ',.2f'),
                format(round(self.total_collections, 2), ',.2f'),
                format(round(self.total_debts, 2), ',.2f')
            ])

            # إنشاء جدول التقرير
            report_table = Table(report_data, colWidths=[60, 90, 70, 50, 50, 50, 50])
            report_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#4472C4')),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
                ('ALIGN', (0, 0), (-1, -1), 'RIGHT'),
                ('FONTNAME', (0, 0), (-1, -1), 'Arabic'),
                ('FONTSIZE', (0, 0), (-1, -1), 8),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 5),
                ('TOPPADDING', (0, 0), (-1, 0), 5),
                ('BACKGROUND', (0, 1), (-1, -1), colors.white),
                ('GRID', (0, 0), (-1, -1), 1, colors.black),
                ('BACKGROUND', (0, -1), (-1, -1), colors.HexColor('#D9E1F2')),
                ('FONTWEIGHT', (0, -1), (-1, -1), 'BOLD'),
                ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#E6F2FF')),
                ('FONTWEIGHT', (0, 0), (0, -1), 'BOLD')
            ]))

            elements.append(report_table)

            # بناء مستند PDF
            doc.build(elements)
            output.seek(0)

            return {
                'file_name': f"تقرير_مراكز_التكلفة_{self.date_from}_إلى_{self.date_to}.pdf",
                'file_content': output.read(),
                'file_type': 'application/pdf'
            }
        except Exception as e:
            logger.error("Failed to generate PDF report: %s", str(e))
            raise

    def action_generate_excel_report(self):
        output = io.BytesIO()
        workbook = xlsxwriter.Workbook(output, {'in_memory': True})
        worksheet = workbook.add_worksheet('تقرير مراكز التكلفة')
        # مثال: كتابة رؤوس الأعمدة
        worksheet.write(0, 0, 'الاسم')
        worksheet.write(0, 1, 'الإيرادات')
        worksheet.write(0, 2, 'المصروفات')
        # مثال: كتابة بيانات التقرير
        row = 1
        for rec in self:
            worksheet.write(row, 0, rec.name)
            worksheet.write(row, 1, rec.total_revenues)
            worksheet.write(row, 2, rec.total_expenses)
            row += 1
        workbook.close()
        output.seek(0)
        file_data = output.read()
        output.close()
        attachment = self.env['ir.attachment'].create({
            'name': 'تقرير مراكز التكلفة.xlsx',
            'type': 'binary',
            'datas': base64.b64encode(file_data),
            'res_model': self._name,
            'res_id': self.id,
            'mimetype': 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        })
        download_url = '/web/content/%s?download=true' % (attachment.id)
        return {
            'type': 'ir.actions.act_url',
            'url': download_url,
            'target': 'new',
        }

    def action_generate_pdf_report(self):
        """إجراء لإنشاء وتنزيل تقرير PDF"""
        self.ensure_one()
        try:
            report_data = self.generate_pdf_report()

            attachment = self.env['ir.attachment'].create({
                'name': report_data['file_name'],
                'datas': base64.b64encode(report_data['file_content']),
                'res_model': 'analytic.account.report',
                'res_id': self.id,
                'type': 'binary'
            })

            return {
                'type': 'ir.actions.act_url',
                'url': '/web/content/%s?download=true' % attachment.id,
                'target': 'self',
            }
        except Exception as e:
            logger.error("Failed to generate PDF report: %s", str(e))
            raise

    def action_view_analytic_lines(self):
        """عرض حركات مراكز التكلفة"""
        self.ensure_one()
        action = self.env.ref('analytic.account_analytic_line_action').read()[0]
        company_ids = [c.id for c in self.company_ids if c._name == 'res.company' and c.id]
        if not company_ids:
            action['domain'] = [('id', '=', False)]
            return action
            
        domain = [
            ('date', '>=', self.date_from),
            ('date', '<=', self.date_to),
            ('company_id', 'in', company_ids),
            ('account_id', '!=', False)
        ]
        # Remove branch handling - no longer needed
        if self.group_id and self.group_id.id:
            domain.append(('account_id.group_id', '=', self.group_id.id))
        if self.analytic_account_ids:
            analytic_account_ids = [a.id for a in self.analytic_account_ids if a._name == 'account.analytic.account' and a.id]
            if analytic_account_ids:
                domain.append(('account_id', 'in', analytic_account_ids))
        action['domain'] = domain
        action['context'] = {
            'search_default_group_by_account': 1,
            'create': False
        }
        return action

    def debug_data(self):
        """دالة للتشخيص وفحص البيانات"""
        self.ensure_one()
        
        logger.info("=== تشخيص البيانات ===")
        logger.info(f"الفترة: من {self.date_from} إلى {self.date_to}")
        logger.info(f"الشركات: {[c.name for c in self.company_ids]}")
        logger.info(f"مراكز التكلفة: {len(self.analytic_account_ids)}")
        
        # فحص وجود قيود يومية
        domain = [
            ('date', '>=', self.date_from),
            ('date', '<=', self.date_to),
            ('company_id', 'in', self.company_ids.ids),
            ('move_id.state', '=', 'posted')
        ]
        
        all_lines = self.env['account.move.line'].search(domain)
        logger.info(f"إجمالي القيود في الفترة: {len(all_lines)}")
        
        lines_with_analytic = all_lines.filtered(lambda l: l.analytic_account_id)
        logger.info(f"القيود المرتبطة بمراكز تكلفة: {len(lines_with_analytic)}")
        
        # فحص كل مركز تكلفة
        for account in self.analytic_account_ids:
            account_lines = lines_with_analytic.filtered(lambda l: l.analytic_account_id.id == account.id)
            logger.info(f"مركز التكلفة {account.name}: {len(account_lines)} قيد")
            
            if account_lines:
                total_debit = sum(line.debit for line in account_lines)
                total_credit = sum(line.credit for line in account_lines)
                total_balance = sum(line.balance for line in account_lines)
                logger.info(f"  - إجمالي المدين: {total_debit}")
                logger.info(f"  - إجمالي الدائن: {total_credit}")
                logger.info(f"  - إجمالي الرصيد: {total_balance}")
