# -*- coding: utf-8 -*-

from odoo import models, fields, api
from odoo.exceptions import ValidationError, UserError
from datetime import timedelta
from collections import defaultdict
from odoo import fields
import io
import xlsxwriter
import base64
from datetime import datetime
import logging
import json
from reportlab.lib.pagesizes import letter, landscape
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors
from reportlab.lib.units import inch
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

logger = logging.getLogger(__name__)


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
    operating_unit_id = fields.Many2one(
        'operating.unit',
        string='الفرع',
        domain="[('company_id', 'in', company_ids)]"
    )

    # حقول المقارنة بين السنوات - إصلاح أسماء الحقول
    compare_years = fields.Boolean(string='مقارنة بالسنوات السابقة')
    year_compare_count = fields.Integer(string='عدد السنوات للمقارنة', default=1)
    
    # إضافة الحقول المفقودة للتوافق مع الواجهة
    enable_yearly_comparison = fields.Boolean(
        string='تفعيل المقارنة السنوية',
        related='compare_years',
        readonly=False
    )
    comparison_years = fields.Integer(
        string='عدد السنوات للمقارنة',
        related='year_compare_count',
        readonly=False
    )
    
    # إضافة حقل بيانات المقارنة السنوية للواجهة
    yearly_comparison_data = fields.Html(
        string='بيانات المقارنة السنوية',
        compute='_compute_yearly_comparison_data',
        store=True,
        sanitize=False
    )
    
    previous_years_data = fields.Text(string='بيانات السنوات السابقة', compute='_compute_previous_years_data')

    # حقول العلاقات
    group_id = fields.Many2one(
        'account.analytic.group',
        string='مجموعة مراكز التكلفة',
        domain="[('company_id', 'in', company_ids)]"
    )

    analytic_account_id = fields.Many2one(
        'account.analytic.account',
        string='مركز التكلفة',
        domain="[('company_id', 'in', company_ids), ('active', '=', True), ('group_id', '=?', group_id), ('operating_unit_id', '=?', operating_unit_id)]"
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
        string='مراكز التكلفة',
        compute='_compute_analytic_accounts',
        store=True
    )

    @api.depends('company_ids')
    def _compute_main_company(self):
        for record in self:
            if record.company_ids and len(record.company_ids) == 1:
                record.company_id = record.company_ids[0]
            elif record.company_ids and len(record.company_ids) > 1:
                record.company_id = record.company_ids[0]
            else:
                record.company_id = False

    @api.depends('company_ids')
    def _compute_company_currency(self):
        for record in self:
            try:
                default_currency = self.env.company.currency_id
            except Exception:
                default_currency = self.env['res.currency'].search([('name', '=', 'USD')], limit=1)
                if not default_currency:
                    default_currency = self.env['res.currency'].search([], limit=1)

            record.company_currency_id = default_currency

            if not record.company_ids:
                continue

            try:
                valid_companies = [c for c in record.company_ids if c._name == 'res.company' and c.id]
                if valid_companies:
                    record.company_currency_id = valid_companies[0].currency_id
            except Exception as e:
                logger.error("Error computing company currency: %s", str(e))

    @api.onchange('company_ids')
    def _onchange_company_ids(self):
        """تحديث الخيارات المتاحة عند تغيير الشركات"""
        if self.company_ids:
            # إعادة تعيين الحقول التابعة
            self.operating_unit_id = False
            self.group_id = False
            self.analytic_account_id = False
            
            # تحديث domain للفروع
            return {
                'domain': {
                    'operating_unit_id': [('company_id', 'in', self.company_ids.ids)],
                    'group_id': [('company_id', 'in', self.company_ids.ids)],
                    'analytic_account_id': [('company_id', 'in', self.company_ids.ids), ('active', '=', True)]
                }
            }
        else:
            # إذا لم يتم اختيار شركة، إظهار جميع الخيارات
            self.operating_unit_id = False
            self.group_id = False
            self.analytic_account_id = False
            
            return {
                'domain': {
                    'operating_unit_id': [],
                    'group_id': [],
                    'analytic_account_id': [('active', '=', True)]
                }
            }

    @api.onchange('operating_unit_id')
    def _onchange_operating_unit_id(self):
        """تحديث المجموعات المتاحة عند تغيير الفرع"""
        # إعادة تعيين الحقول التابعة
        self.group_id = False
        self.analytic_account_id = False
        
        if self.operating_unit_id:
            # إظهار المجموعات المرتبطة بالفرع المحدد
            domain_group = []
            domain_analytic = [('active', '=', True)]
            
            if self.company_ids:
                domain_group.append(('company_id', 'in', self.company_ids.ids))
                domain_analytic.append(('company_id', 'in', self.company_ids.ids))
            
            # البحث عن المجموعات المرتبطة بالفرع
            analytic_accounts_in_unit = self.env['account.analytic.account'].search([
                ('operating_unit_id', '=', self.operating_unit_id.id),
                ('active', '=', True)
            ])
            
            group_ids = analytic_accounts_in_unit.mapped('group_id').ids
            if group_ids:
                domain_group.append(('id', 'in', group_ids))
            else:
                domain_group.append(('id', '=', False))  # لا توجد مجموعات
            
            domain_analytic.append(('operating_unit_id', '=', self.operating_unit_id.id))
            
            return {
                'domain': {
                    'group_id': domain_group,
                    'analytic_account_id': domain_analytic
                }
            }
        else:
            # إذا لم يتم اختيار فرع، إظهار جميع المجموعات للشركات المحددة
            domain_group = []
            domain_analytic = [('active', '=', True)]
            
            if self.company_ids:
                domain_group.append(('company_id', 'in', self.company_ids.ids))
                domain_analytic.append(('company_id', 'in', self.company_ids.ids))
            
            return {
                'domain': {
                    'group_id': domain_group,
                    'analytic_account_id': domain_analytic
                }
            }

    @api.onchange('group_id')
    def _onchange_group_id(self):
        """تحديث مراكز التكلفة المتاحة عند تغيير المجموعة"""
        # إعادة تعيين مركز التكلفة
        self.analytic_account_id = False
        
        domain_analytic = [('active', '=', True)]
        
        if self.company_ids:
            domain_analytic.append(('company_id', 'in', self.company_ids.ids))
        
        if self.operating_unit_id:
            domain_analytic.append(('operating_unit_id', '=', self.operating_unit_id.id))
        
        if self.group_id:
            # إظهار مراكز التكلفة المرتبطة بالمجموعة المحددة
            domain_analytic.append(('group_id', '=', self.group_id.id))
        
        return {
            'domain': {
                'analytic_account_id': domain_analytic
            }
        }

    @api.depends('company_ids', 'operating_unit_id', 'group_id', 'analytic_account_id')
    def _compute_analytic_accounts(self):
        """حساب مراكز التكلفة المتاحة بناءً على الاختيارات"""
        for record in self:
            try:
                domain = [('active', '=', True)]
                
                if record.company_ids:
                    domain.append(('company_id', 'in', record.company_ids.ids))
                
                if record.operating_unit_id:
                    domain.append(('operating_unit_id', '=', record.operating_unit_id.id))
                
                if record.group_id:
                    domain.append(('group_id', '=', record.group_id.id))
                
                # إذا تم تحديد مركز تكلفة واحد، استخدمه
                if record.analytic_account_id:
                    if record.analytic_account_id.id in self.env['account.analytic.account'].search(domain).ids:
                        record.analytic_account_ids = record.analytic_account_id
                    else:
                        record.analytic_account_ids = self.env['account.analytic.account']
                else:
                    # وإلا، استخدم جميع مراكز التكلفة المطابقة للمعايير
                    analytic_accounts = self.env['account.analytic.account'].search(domain)
                    record.analytic_account_ids = analytic_accounts

            except Exception as e:
                logger.error("خطأ في حساب مراكز التكلفة: %s", str(e))
                record.analytic_account_ids = self.env['account.analytic.account']

    @api.depends('compare_years', 'previous_years_data')
    def _compute_yearly_comparison_data(self):
        """حساب بيانات المقارنة السنوية لعرضها في الواجهة"""
        for record in self:
            if not record.compare_years or not record.previous_years_data:
                record.yearly_comparison_data = '<p>لا توجد بيانات مقارنة متاحة</p>'
                continue

            try:
                comparison_data = json.loads(record.previous_years_data)
                
                html_content = """
                    <style>
                        .comparison-table { width: 100%; border-collapse: collapse; margin: 20px 0; }
                        .comparison-table th { background-color: #4472C4; color: white; padding: 10px; text-align: center; }
                        .comparison-table td { padding: 8px; border: 1px solid #ddd; text-align: right; }
                        .comparison-table tr:nth-child(even) { background-color: #f9f9f9; }
                        .current-year { background-color: #d4edda; font-weight: bold; }
                    </style>
                    <h3 style="text-align: center; color: #4472C4;">مقارنة بالسنوات السابقة</h3>
                    <table class="comparison-table">
                        <thead>
                            <tr>
                                <th>السنة</th>
                                <th>المصروفات</th>
                                <th>الإيرادات</th>
                                <th>التحصيل</th>
                                <th>المديونية</th>
                            </tr>
                        </thead>
                        <tbody>
                """
                
                # إضافة بيانات السنوات السابقة
                for year_data in comparison_data:
                    html_content += f"""
                        <tr>
                            <td>{year_data['year']}</td>
                            <td>{format(year_data['expenses'], ',.2f')}</td>
                            <td>{format(year_data['revenues'], ',.2f')}</td>
                            <td>{format(year_data['collections'], ',.2f')}</td>
                            <td>{format(year_data['debts'], ',.2f')}</td>
                        </tr>
                    """
                
                # إضافة السنة الحالية
                current_year = fields.Date.from_string(record.date_from).year
                html_content += f"""
                        <tr class="current-year">
                            <td>{current_year} (الحالية)</td>
                            <td>{format(record.total_expenses, ',.2f')}</td>
                            <td>{format(record.total_revenues, ',.2f')}</td>
                            <td>{format(record.total_collections, ',.2f')}</td>
                            <td>{format(record.total_debts, ',.2f')}</td>
                        </tr>
                    </tbody>
                </table>
                """
                
                record.yearly_comparison_data = html_content
                
            except Exception as e:
                logger.error(f"Error computing yearly comparison data: {str(e)}")
                record.yearly_comparison_data = '<p>خطأ في تحميل بيانات المقارنة</p>'

    @api.depends('date_from', 'date_to', 'compare_years', 'year_compare_count')
    def _compute_previous_years_data(self):
        """حساب بيانات السنوات السابقة للمقارنة"""
        for record in self:
            if not record.compare_years or not record.date_from or not record.date_to:
                record.previous_years_data = False
                continue

            try:
                comparison_data = []
                current_year = fields.Date.from_string(record.date_from).year

                for year_offset in range(1, record.year_compare_count + 1):
                    prev_year = current_year - year_offset

                    prev_date_from = record.date_from.replace(year=prev_year)
                    prev_date_to = record.date_to.replace(year=prev_year)

                    prev_data = {
                        'year': prev_year,
                        'date_from': prev_date_from,
                        'date_to': prev_date_to,
                        'expenses': self._calculate_period_amount(record, prev_date_from, prev_date_to, 'expenses'),
                        'revenues': self._calculate_period_amount(record, prev_date_from, prev_date_to, 'revenues'),
                        'collections': self._calculate_period_amount(record, prev_date_from, prev_date_to,
                                                                     'collections'),
                        'debts': self._calculate_period_amount(record, prev_date_from, prev_date_to, 'debts')
                    }

                    comparison_data.append(prev_data)

                record.previous_years_data = json.dumps(comparison_data)
            except Exception as e:
                logger.error("Error computing previous years data: %s", str(e))
                record.previous_years_data = False

    def _calculate_period_amount(self, record, date_from, date_to, amount_type):
        """حساب المبالغ لفترة محددة"""
        try:
            company_ids = [c.id for c in record.company_ids]
            analytic_account_ids = [a.id for a in record.analytic_account_ids] if record.analytic_account_ids else []

            base_domain = [
                ('date', '>=', date_from),
                ('date', '<=', date_to),
                ('company_id', 'in', company_ids),
                ('move_id.state', '=', 'posted')
            ]

            if analytic_account_ids:
                base_domain.append(('analytic_account_id', 'in', analytic_account_ids))

            if amount_type == 'expenses':
                domain = base_domain + [('account_id.internal_group', '=', 'expense')]
                lines = self._optimize_query_performance(domain)
                return abs(sum(lines.mapped('balance')))

            elif amount_type == 'revenues':
                domain = base_domain + [('account_id.internal_group', '=', 'income')]
                lines = self._optimize_query_performance(domain)
                return abs(sum(lines.mapped('balance')))

            elif amount_type == 'collections':
                domain = base_domain + [('payment_id', '!=', False)]
                lines = self._optimize_query_performance(domain)
                return abs(sum(lines.mapped('balance')))

            elif amount_type == 'debts':
                domain = base_domain + [
                    ('move_id.move_type', 'in', ['out_invoice', 'in_invoice']),
                    ('move_id.payment_state', 'in', ['not_paid', 'partial']),
                    ('amount_residual', '>', 0)
                ]
                lines = self._optimize_query_performance(domain)
                return sum(line.amount_residual for line in lines)

            return 0.0
        except Exception as e:
            logger.error("Error calculating period amount: %s", str(e))
            return 0.0

    @api.depends('date_from', 'date_to', 'company_ids', 'analytic_account_ids', 'operating_unit_id', 'group_id', 'analytic_account_id')
    def _compute_totals(self):
        """حساب الإجماليات بدقة مع ضمان ظهور القيم الصحيحة"""
        for record in self:
            try:
                # إعادة تعيين القيم
                record.total_expenses = 0.0
                record.total_revenues = 0.0
                record.total_collections = 0.0
                record.total_debts = 0.0

                if not record.company_ids:
                    continue

                company_ids = record.company_ids.ids

                # الحصول على مراكز التكلفة المحددة أو جميعها إن لم يتم التحديد
                analytic_account_ids = record.analytic_account_ids.ids if record.analytic_account_ids else \
                    self.env['account.analytic.account'].search([
                        ('company_id', 'in', company_ids),
                        ('active', '=', True)
                    ]).ids

                if not analytic_account_ids:
                    continue

                # نطاق البحث الأساسي - إزالة الشروط المقيدة
                base_domain = [
                    ('date', '>=', record.date_from),
                    ('date', '<=', record.date_to),
                    ('company_id', 'in', company_ids),
                    ('move_id.state', '=', 'posted'),
                    ('analytic_account_id', 'in', analytic_account_ids)
                ]

                # 1. حساب المصروفات - تحسين الشروط
                expense_domain = base_domain + [
                    ('account_id.internal_group', '=', 'expense')
                ]
                expense_lines = self.env['account.move.line'].search(expense_domain)
                record.total_expenses = sum(abs(line.balance) for line in expense_lines if line.balance != 0)

                # 2. حساب الإيرادات - تحسين الشروط
                revenue_domain = base_domain + [
                    ('account_id.internal_group', '=', 'income')
                ]
                revenue_lines = self.env['account.move.line'].search(revenue_domain)
                record.total_revenues = sum(abs(line.balance) for line in revenue_lines if line.balance != 0)

                # 3. حساب التحصيل - تحسين البحث
                payment_domain = base_domain + [
                    '|',
                    ('payment_id', '!=', False),
                    ('account_id.internal_type', 'in', ['receivable', 'payable'])
                ]
                payment_lines = self.env['account.move.line'].search(payment_domain)
                collections_total = 0.0
                for line in payment_lines:
                    if line.payment_id or (line.account_id.internal_type in ['receivable', 'payable'] and line.balance > 0):
                        collections_total += abs(line.balance)
                record.total_collections = collections_total

                # 4. حساب المديونية - تحسين الحساب
                invoice_domain = [
                    ('move_id.move_type', 'in', ['out_invoice', 'in_invoice']),
                    ('move_id.payment_state', 'in', ['not_paid', 'partial']),
                    ('date', '>=', record.date_from),
                    ('date', '<=', record.date_to),
                    ('company_id', 'in', company_ids),
                    ('analytic_account_id', 'in', analytic_account_ids),
                    ('move_id.state', '=', 'posted'),
                    ('account_id.internal_type', 'in', ['receivable', 'payable'])
                ]
                invoice_lines = self.env['account.move.line'].search(invoice_domain)
                debts_total = 0.0
                for line in invoice_lines:
                    if hasattr(line, 'amount_residual') and line.amount_residual > 0:
                        debts_total += line.amount_residual
                    elif line.balance != 0:
                        debts_total += abs(line.balance)
                record.total_debts = debts_total

                # تسجيل للتحقق
                logger.info(f"""
                    === نتائج الحساب المحدثة ===
                    المصروفات: {record.total_expenses}
                    الإيرادات: {record.total_revenues}
                    التحصيل: {record.total_collections}
                    المديونية: {record.total_debts}
                    عدد مراكز التكلفة: {len(analytic_account_ids)}
                """)

            except Exception as e:
                logger.error(f"Error in _compute_totals: {str(e)}")

    def _calculate_debts(self, date_from, date_to, company_ids, analytic_account_ids):
        """حساب المديونية بدقة أكبر"""
        self.ensure_one()
        try:
            domain = [
                ('date', '>=', date_from),
                ('date', '<=', date_to),
                ('company_id', 'in', company_ids),
                ('move_id.state', '=', 'posted'),
                ('move_id.move_type', 'in', ['out_invoice', 'in_invoice']),
                ('move_id.payment_state', 'in', ['not_paid', 'partial']),
                ('amount_residual', '>', 0)
            ]

            if analytic_account_ids:
                domain.append(('analytic_account_id', 'in', analytic_account_ids))

            invoice_lines = self._optimize_query_performance(domain)
            total_debts = 0.0

            for line in invoice_lines:
                if analytic_account_ids and line.analytic_account_id.id not in analytic_account_ids:
                    continue

                total_debts += line.amount_residual

            return total_debts
        except Exception as e:
            logger.error("Error in _calculate_debts: %s", str(e))
            return 0.0

    def _optimize_query_performance(self, domain):
        """تحسين أداء استعلامات قاعدة البيانات"""
        return self.env['account.move.line'].with_context(
            prefetch_fields=False,
            prefetch=False
        ).search(domain)

    @api.depends('date_from', 'date_to', 'company_ids', 'analytic_account_ids', 'operating_unit_id', 'compare_years',
                 'previous_years_data')
    def _compute_report_lines(self):
        for record in self:
            try:
                if len(record.analytic_account_ids) > 100:
                    record.report_lines = "<p>عدد مراكز التكلفة كبير جداً. يرجى تحديد فلاتر أكثر تحديداً.</p>"
                    continue

                company_ids = [c.id for c in record.company_ids if
                               c._name == 'res.company' and c.id] if record.company_ids else []

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
                        .comparison-table { width: 80%; margin: 20px auto; border-collapse: collapse; }
                        .comparison-table th { background-color: #4472C4; color: white; padding: 8px; }
                        .comparison-table td { padding: 8px; border: 1px solid #ddd; }
                    </style>
                    <table class="table">
                        <thead>
                            <tr>
                                <th>الفرع</th>
                                <th>المجموعة الرئيسية</th>
                                <th>المجموعة الفرعية</th>
                                <th>مركز التكلفة</th>
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

                analytic_account_ids = [a.id for a in record.analytic_account_ids if
                                        a._name == 'account.analytic.account' and a.id]
                if not analytic_account_ids:
                    record.report_lines = "<p>لا توجد مراكز تكلفة صالحة</p>"
                    continue

                operating_unit_dict = defaultdict(lambda: {
                    'groups': defaultdict(lambda: {
                        'subgroups': defaultdict(lambda: {
                            'accounts': [],
                            'total_expenses': 0.0,
                            'total_revenues': 0.0,
                            'total_collections': 0.0,
                            'total_debts': 0.0
                        }),
                        'total_expenses': 0.0,
                        'total_revenues': 0.0,
                        'total_collections': 0.0,
                        'total_debts': 0.0
                    }),
                    'total_expenses': 0.0,
                    'total_revenues': 0.0,
                    'total_collections': 0.0,
                    'total_debts': 0.0
                })

                for account in record.analytic_account_ids:
                    expenses = self._calculate_analytic_amount(account, 'expenses')
                    revenues = self._calculate_analytic_amount(account, 'revenues')
                    collections = self._calculate_analytic_amount(account, 'collections')
                    debts = self._calculate_analytic_amount(account, 'debts')

                    operating_unit = account.operating_unit_id or 'بدون فرع'
                    operating_unit_name = operating_unit.name if operating_unit != 'بدون فرع' else 'بدون فرع'

                    root_group = account.group_id
                    while root_group and root_group.parent_id:
                        root_group = root_group.parent_id
                    root_group_name = root_group.name if root_group else 'بدون مجموعة رئيسية'

                    subgroup = account.group_id if account.group_id and account.group_id.parent_id == root_group else None
                    subgroup_name = subgroup.name if subgroup else 'بدون مجموعة فرعية'

                    operating_unit_dict[operating_unit_name]['groups'][root_group_name]['subgroups'][subgroup_name][
                        'accounts'].append({
                        'account': account,
                        'expenses': expenses,
                        'revenues': revenues,
                        'collections': collections,
                        'debts': debts
                    })

                    operating_unit_dict[operating_unit_name]['groups'][root_group_name]['subgroups'][subgroup_name][
                        'total_expenses'] += expenses
                    operating_unit_dict[operating_unit_name]['groups'][root_group_name]['subgroups'][subgroup_name][
                        'total_revenues'] += revenues
                    operating_unit_dict[operating_unit_name]['groups'][root_group_name]['subgroups'][subgroup_name][
                        'total_collections'] += collections
                    operating_unit_dict[operating_unit_name]['groups'][root_group_name]['subgroups'][subgroup_name][
                        'total_debts'] += debts

                    operating_unit_dict[operating_unit_name]['groups'][root_group_name]['total_expenses'] += expenses
                    operating_unit_dict[operating_unit_name]['groups'][root_group_name]['total_revenues'] += revenues
                    operating_unit_dict[operating_unit_name]['groups'][root_group_name][
                        'total_collections'] += collections
                    operating_unit_dict[operating_unit_name]['groups'][root_group_name]['total_debts'] += debts

                    operating_unit_dict[operating_unit_name]['total_expenses'] += expenses
                    operating_unit_dict[operating_unit_name]['total_revenues'] += revenues
                    operating_unit_dict[operating_unit_name]['total_collections'] += collections
                    operating_unit_dict[operating_unit_name]['total_debts'] += debts

                for operating_unit_name, operating_unit_data in operating_unit_dict.items():
                    html_lines.append(f"""
                        <tr class="section-row">
                            <td colspan="8">{operating_unit_name}</td>
                        </tr>
                    """)

                    for root_group_name, root_group_data in operating_unit_data['groups'].items():
                        html_lines.append(f"""
                            <tr class="section-row">
                                <td></td>
                                <td colspan="7">{root_group_name}</td>
                            </tr>
                        """)

                        for subgroup_name, subgroup_data in root_group_data['subgroups'].items():
                            html_lines.append(f"""
                                <tr class="section-row">
                                    <td></td>
                                    <td></td>
                                    <td colspan="6">{subgroup_name}</td>
                                </tr>
                            """)

                            for account_data in subgroup_data['accounts']:
                                account = account_data['account']
                                html_lines.append(f"""
                                    <tr>
                                        <td></td>
                                        <td></td>
                                        <td></td>
                                        <td>{account.name}</td>
                                        <td class="text-right">{format(account_data['expenses'], '.2f')}</td>
                                        <td class="text-right">{format(account_data['revenues'], '.2f')}</td>
                                        <td class="text-right">{format(account_data['collections'], '.2f')}</td>
                                        <td class="text-right">{format(account_data['debts'], '.2f')}</td>
                                    </tr>
                                """)

                            html_lines.append(f"""
                                <tr class="total-row">
                                    <td></td>
                                    <td></td>
                                    <td colspan="1">إجمالي {subgroup_name}</td>
                                    <td></td>
                                    <td class="text-right">{format(subgroup_data['total_expenses'], '.2f')}</td>
                                    <td class="text-right">{format(subgroup_data['total_revenues'], '.2f')}</td>
                                    <td class="text-right">{format(subgroup_data['total_collections'], '.2f')}</td>
                                    <td class="text-right">{format(subgroup_data['total_debts'], '.2f')}</td>
                                </tr>
                            """)

                        html_lines.append(f"""
                            <tr class="total-row">
                                <td></td>
                                <td colspan="2">إجمالي {root_group_name}</td>
                                <td></td>
                                <td class="text-right">{format(root_group_data['total_expenses'], '.2f')}</td>
                                <td class="text-right">{format(root_group_data['total_revenues'], '.2f')}</td>
                                <td class="text-right">{format(root_group_data['total_collections'], '.2f')}</td>
                                <td class="text-right">{format(root_group_data['total_debts'], '.2f')}</td>
                            </tr>
                        """)

                    html_lines.append(f"""
                        <tr class="total-row">
                            <td colspan="3">إجمالي {operating_unit_name}</td>
                            <td></td>
                            <td class="text-right">{format(operating_unit_data['total_expenses'], '.2f')}</td>
                            <td class="text-right">{format(operating_unit_data['total_revenues'], '.2f')}</td>
                            <td class="text-right">{format(operating_unit_data['total_collections'], '.2f')}</td>
                            <td class="text-right">{format(operating_unit_data['total_debts'], '.2f')}</td>
                        </tr>
                    """)

                html_lines.append(f"""
                    <tr class="total-row">
                        <td colspan="4">الإجمالي العام</td>
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

                # إضافة قسم المقارنة إذا تم تفعيله
                if record.compare_years and record.previous_years_data:
                    comparison_data = json.loads(record.previous_years_data)

                    html_lines.append("""
                        <h3 style="text-align: center; color: #4472C4; margin-top: 30px;">مقارنة بالسنوات السابقة</h3>
                        <table class="comparison-table">
                            <thead>
                                <tr>
                                    <th>السنة</th>
                                    <th>المصروفات</th>
                                    <th>الإيرادات</th>
                                    <th>التحصيل</th>
                                    <th>المديونية</th>
                                </tr>
                            </thead>
                            <tbody>
                    """)

                    for year_data in comparison_data:
                        html_lines.append(f"""
                            <tr>
                                <td>{year_data['year']}</td>
                                <td class="text-right">{format(year_data['expenses'], '.2f')}</td>
                                <td class="text-right">{format(year_data['revenues'], '.2f')}</td>
                                <td class="text-right">{format(year_data['collections'], '.2f')}</td>
                                <td class="text-right">{format(year_data['debts'], '.2f')}</td>
                            </tr>
                        """)

                    # إضافة السنة الحالية
                    html_lines.append(f"""
                        <tr style="background-color: #f2f2f2; font-weight: bold;">
                            <td>{fields.Date.from_string(record.date_from).year} (الحالية)</td>
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

    def _calculate_analytic_amount(self, account, amount_type):
        """حساب المبالغ لكل حساب تحليلي بشكل منفصل"""
        try:
            if not account or not account.id:
                return 0.0
    
            company_ids = self.company_ids.ids if self.company_ids else []
            if not company_ids:
                return 0.0
    
            base_domain = [
                ('date', '>=', self.date_from),
                ('date', '<=', self.date_to),
                ('company_id', 'in', company_ids),
                ('analytic_account_id', '=', account.id),
                ('move_id.state', '=', 'posted')
            ]
    
            if amount_type == 'expenses':
                # تحسين حساب المصروفات - إزالة شرط balance < 0
                domain = base_domain + [
                    ('account_id.internal_group', '=', 'expense')
                ]
                lines = self.env['account.move.line'].search(domain)
                total = sum(abs(line.balance) for line in lines if line.balance != 0)
                return total
    
            elif amount_type == 'revenues':
                # تحسين حساب الإيرادات - إزالة شرط balance > 0
                domain = base_domain + [
                    ('account_id.internal_group', '=', 'income')
                ]
                lines = self.env['account.move.line'].search(domain)
                total = sum(abs(line.balance) for line in lines if line.balance != 0)
                return total
    
            elif amount_type == 'collections':
                # تحسين حساب التحصيل - البحث في جميع المدفوعات
                domain = base_domain + [
                    '|',
                    ('payment_id', '!=', False),
                    ('account_id.internal_type', 'in', ['receivable', 'payable'])
                ]
                lines = self.env['account.move.line'].search(domain)
                total = 0.0
                for line in lines:
                    if line.payment_id or (line.account_id.internal_type in ['receivable', 'payable'] and line.balance > 0):
                        total += abs(line.balance)
                return total
    
            elif amount_type == 'debts':
                # تحسين حساب المديونية
                # البحث في الفواتير غير المدفوعة
                invoice_domain = [
                    ('move_id.move_type', 'in', ['out_invoice', 'in_invoice']),
                    ('move_id.payment_state', 'in', ['not_paid', 'partial']),
                    ('date', '>=', self.date_from),
                    ('date', '<=', self.date_to),
                    ('company_id', 'in', company_ids),
                    ('analytic_account_id', '=', account.id),
                    ('move_id.state', '=', 'posted'),
                    ('account_id.internal_type', 'in', ['receivable', 'payable'])
                ]
                lines = self.env['account.move.line'].search(invoice_domain)
                total = 0.0
                for line in lines:
                    if hasattr(line, 'amount_residual') and line.amount_residual > 0:
                        total += line.amount_residual
                    elif line.balance != 0:
                        total += abs(line.balance)
                return total
    
            return 0.0
    
        except Exception as e:
            logger.error(f"Error in _calculate_analytic_amount for {amount_type}: {str(e)}")
            return 0.0
    
    def _calculate_analytic_amount_for_period(self, account, amount_type, date_from, date_to):
        """حساب المبالغ لمركز تكلفة محدد في فترة محددة"""
        try:
            if not account or not account.id:
                return 0.0

            company_ids = self.company_ids.ids if self.company_ids else []
            if not company_ids:
                return 0.0

            base_domain = [
                ('date', '>=', date_from),
                ('date', '<=', date_to),
                ('company_id', 'in', company_ids),
                ('analytic_account_id', '=', account.id),
                ('move_id.state', '=', 'posted')
            ]

            if amount_type == 'expenses':
                domain = base_domain + [
                    ('account_id.internal_group', '=', 'expense')
                ]
                lines = self.env['account.move.line'].search(domain)
                return sum(abs(line.balance) for line in lines if line.balance != 0)

            elif amount_type == 'revenues':
                domain = base_domain + [
                    ('account_id.internal_group', '=', 'income')
                ]
                lines = self.env['account.move.line'].search(domain)
                return sum(abs(line.balance) for line in lines if line.balance != 0)

            elif amount_type == 'collections':
                domain = base_domain + [
                    '|',
                    ('payment_id', '!=', False),
                    ('account_id.internal_type', 'in', ['receivable', 'payable'])
                ]
                lines = self.env['account.move.line'].search(domain)
                total = 0.0
                for line in lines:
                    if line.payment_id or (line.account_id.internal_type in ['receivable', 'payable'] and line.balance > 0):
                        total += abs(line.balance)
                return total

            elif amount_type == 'debts':
                invoice_domain = [
                    ('move_id.move_type', 'in', ['out_invoice', 'in_invoice']),
                    ('move_id.payment_state', 'in', ['not_paid', 'partial']),
                    ('date', '>=', date_from),
                    ('date', '<=', date_to),
                    ('company_id', 'in', company_ids),
                    ('analytic_account_id', '=', account.id),
                    ('move_id.state', '=', 'posted'),
                    ('account_id.internal_type', 'in', ['receivable', 'payable'])
                ]
                lines = self.env['account.move.line'].search(invoice_domain)
                total = 0.0
                for line in lines:
                    if hasattr(line, 'amount_residual') and line.amount_residual > 0:
                        total += line.amount_residual
                    elif line.balance != 0:
                        total += abs(line.balance)
                return total

            return 0.0

        except Exception as e:
            logger.error(f"Error in _calculate_analytic_amount_for_period for {amount_type}: {str(e)}")
            return 0.0
    def check_data_availability(self):
        """دالة مساعدة للتحقق من توفر البيانات"""
        for record in self:
            try:
                company_ids = record.company_ids.ids if record.company_ids else []
                
                if not company_ids:
                    raise UserError("لم يتم تحديد أي شركات")
                
                analytic_account_ids = record.analytic_account_ids.ids if record.analytic_account_ids else \
                    self.env['account.analytic.account'].search([
                        ('company_id', 'in', company_ids),
                        ('active', '=', True)
                    ]).ids
                
                if not analytic_account_ids:
                    raise UserError("لا توجد مراكز تكلفة متاحة للشركات المحددة")
                
                # التحقق من وجود حركات
                move_lines = self.env['account.move.line'].search([
                    ('date', '>=', record.date_from),
                    ('date', '<=', record.date_to),
                    ('company_id', 'in', company_ids),
                    ('analytic_account_id', 'in', analytic_account_ids),
                    ('move_id.state', '=', 'posted')
                ], limit=1)
                
                if not move_lines:
                    raise UserError("لا توجد حركات مسجلة في الفترة المحددة لمراكز التكلفة المختارة")
                
                return True
                
            except Exception as e:
                logger.error(f"Data check failed: {str(e)}")
                raise UserError(f"خطأ في التحقق من البيانات: {str(e)}")        
            
    def _generate_comparison_table(self, worksheet, row, col, formats):
        """إنشاء جدول المقارنة التفصيلي في تقرير Excel"""
        if not self.compare_years or not self.previous_years_data:
            return row

        comparison_data = json.loads(self.previous_years_data)
        
        # عنوان جدول المقارنة
        worksheet.merge_range(row, col, row, col + 7, "مقارنة بالسنوات السابقة", formats['section_format'])
        row += 2
        
        # إنشاء جدول المقارنة لكل مركز تكلفة
        analytic_domain = [('company_id', 'in', self.company_ids.ids)]
        if self.operating_unit_id:
            analytic_domain.append(('operating_unit_id', '=', self.operating_unit_id.id))
        if self.group_id:
            analytic_domain.append(('group_id', '=', self.group_id.id))
        if self.analytic_account_ids:
            analytic_domain.append(('id', 'in', self.analytic_account_ids.ids))

        analytic_accounts = self.env['account.analytic.account'].search(analytic_domain, order='operating_unit_id, group_id, name')
        
        if not analytic_accounts:
            return row
        
        # رؤوس الأعمدة للمقارنة
        headers = ['مركز التكلفة']
        for year_data in comparison_data:
            headers.extend([f'{year_data["year"]} - مصروفات', f'{year_data["year"]} - إيرادات', 
                           f'{year_data["year"]} - تحصيل', f'{year_data["year"]} - مديونية'])
        
        current_year = fields.Date.from_string(self.date_from).year
        headers.extend([f'{current_year} - مصروفات', f'{current_year} - إيرادات', 
                       f'{current_year} - تحصيل', f'{current_year} - مديونية'])
        
        # كتابة رؤوس الأعمدة
        for i, header in enumerate(headers):
            worksheet.write(row, col + i, header, formats['header_format'])
        row += 1
        
        # تجميع البيانات حسب الهيكل الهرمي
        operating_unit_dict = defaultdict(lambda: {
            'groups': defaultdict(lambda: {
                'subgroups': defaultdict(lambda: {
                    'accounts': []
                })
            })
        })
        
        for account in analytic_accounts:
            operating_unit = account.operating_unit_id or 'بدون فرع'
            operating_unit_name = operating_unit.name if operating_unit != 'بدون فرع' else 'بدون فرع'
            
            root_group = account.group_id
            while root_group and root_group.parent_id:
                root_group = root_group.parent_id
            root_group_name = root_group.name if root_group else 'بدون مجموعة رئيسية'
            
            subgroup = account.group_id if account.group_id and account.group_id.parent_id == root_group else None
            subgroup_name = subgroup.name if subgroup else 'بدون مجموعة فرعية'
            
            operating_unit_dict[operating_unit_name]['groups'][root_group_name]['subgroups'][subgroup_name]['accounts'].append(account)
        
        # إنشاء تنسيقات الألوان
        main_group_format = formats['workbook'].add_format({
            'bold': True,
            'border': 1,
            'align': 'right',
            'bg_color': '#90EE90',  # أخضر فاتح
            'font_size': 10,
            'font_name': 'Arial'
        })
        
        sub_account_format = formats['workbook'].add_format({
            'border': 1,
            'align': 'right',
            'font_size': 10,
            'font_name': 'Arial'
        })
        
        # عرض البيانات
        for operating_unit_name, operating_unit_data in operating_unit_dict.items():
            for root_group_name, root_group_data in operating_unit_data['groups'].items():
                # عرض المجموعة الرئيسية بلون أخضر فاتح
                worksheet.write(row, col, f"{operating_unit_name} - {root_group_name}", main_group_format)
                
                # حساب إجماليات المجموعة الرئيسية
                group_totals = {'current': {'expenses': 0, 'revenues': 0, 'collections': 0, 'debts': 0}}
                for year_data in comparison_data:
                    group_totals[year_data['year']] = {'expenses': 0, 'revenues': 0, 'collections': 0, 'debts': 0}
                
                col_index = col + 1
                
                # حساب وعرض بيانات السنوات السابقة للمجموعة
                for year_data in comparison_data:
                    prev_year = year_data['year']
                    prev_date_from = self.date_from.replace(year=prev_year)
                    prev_date_to = self.date_to.replace(year=prev_year)
                    
                    # حساب إجماليات المجموعة للسنة السابقة
                    group_accounts = []
                    for subgroup_data in root_group_data['subgroups'].values():
                        group_accounts.extend(subgroup_data['accounts'])
                    
                    group_expenses = sum(self._calculate_analytic_amount_for_period(acc, 'expenses', prev_date_from, prev_date_to) for acc in group_accounts)
                    group_revenues = sum(self._calculate_analytic_amount_for_period(acc, 'revenues', prev_date_from, prev_date_to) for acc in group_accounts)
                    group_collections = sum(self._calculate_analytic_amount_for_period(acc, 'collections', prev_date_from, prev_date_to) for acc in group_accounts)
                    group_debts = sum(self._calculate_analytic_amount_for_period(acc, 'debts', prev_date_from, prev_date_to) for acc in group_accounts)
                    
                    worksheet.write(row, col_index, group_expenses, main_group_format)
                    worksheet.write(row, col_index + 1, group_revenues, main_group_format)
                    worksheet.write(row, col_index + 2, group_collections, main_group_format)
                    worksheet.write(row, col_index + 3, group_debts, main_group_format)
                    col_index += 4
                
                # عرض بيانات السنة الحالية للمجموعة
                group_accounts = []
                for subgroup_data in root_group_data['subgroups'].values():
                    group_accounts.extend(subgroup_data['accounts'])
                
                current_expenses = sum(self._calculate_analytic_amount(acc, 'expenses') for acc in group_accounts)
                current_revenues = sum(self._calculate_analytic_amount(acc, 'revenues') for acc in group_accounts)
                current_collections = sum(self._calculate_analytic_amount(acc, 'collections') for acc in group_accounts)
                current_debts = sum(self._calculate_analytic_amount(acc, 'debts') for acc in group_accounts)
                
                worksheet.write(row, col_index, current_expenses, main_group_format)
                worksheet.write(row, col_index + 1, current_revenues, main_group_format)
                worksheet.write(row, col_index + 2, current_collections, main_group_format)
                worksheet.write(row, col_index + 3, current_debts, main_group_format)
                row += 1
                
                # عرض مراكز التكلفة الفرعية بدون لون
                for subgroup_name, subgroup_data in root_group_data['subgroups'].items():
                    for account in subgroup_data['accounts']:
                        worksheet.write(row, col, f"  {account.name}", sub_account_format)
                        
                        col_index = col + 1
                        
                        # بيانات السنوات السابقة
                        for year_data in comparison_data:
                            prev_year = year_data['year']
                            prev_date_from = self.date_from.replace(year=prev_year)
                            prev_date_to = self.date_to.replace(year=prev_year)
                            
                            expenses = self._calculate_analytic_amount_for_period(account, 'expenses', prev_date_from, prev_date_to)
                            revenues = self._calculate_analytic_amount_for_period(account, 'revenues', prev_date_from, prev_date_to)
                            collections = self._calculate_analytic_amount_for_period(account, 'collections', prev_date_from, prev_date_to)
                            debts = self._calculate_analytic_amount_for_period(account, 'debts', prev_date_from, prev_date_to)
                            
                            worksheet.write(row, col_index, expenses, sub_account_format)
                            worksheet.write(row, col_index + 1, revenues, sub_account_format)
                            worksheet.write(row, col_index + 2, collections, sub_account_format)
                            worksheet.write(row, col_index + 3, debts, sub_account_format)
                            col_index += 4
                        
                        # بيانات السنة الحالية
                        current_expenses = self._calculate_analytic_amount(account, 'expenses')
                        current_revenues = self._calculate_analytic_amount(account, 'revenues')
                        current_collections = self._calculate_analytic_amount(account, 'collections')
                        current_debts = self._calculate_analytic_amount(account, 'debts')
                        
                        worksheet.write(row, col_index, current_expenses, sub_account_format)
                        worksheet.write(row, col_index + 1, current_revenues, sub_account_format)
                        worksheet.write(row, col_index + 2, current_collections, sub_account_format)
                        worksheet.write(row, col_index + 3, current_debts, sub_account_format)
                        row += 1
        
        return row + 2

    def generate_excel_report(self):
        """إنشاء وتنزيل تقرير Excel لمراكز التكلفة"""
        self.ensure_one()

        output = io.BytesIO()
        workbook = xlsxwriter.Workbook(output, {
            'in_memory': True,
            'right_to_left': True,
            'strings_to_numbers': True,
            'remove_timezone': True,
            'default_date_format': 'dd/mm/yyyy'
        })

        title_format = workbook.add_format({
            'bold': True,
            'font_size': 16,
            'align': 'center',
            'valign': 'vcenter',
            'font_color': '#4472C4',
            'border': 1,
            'font_name': 'Arial'
        })

        header_format = workbook.add_format({
            'bold': True,
            'font_size': 12,
            'align': 'center',
            'valign': 'vcenter',
            'bg_color': '#4472C4',
            'font_color': 'white',
            'border': 1,
            'text_wrap': True,
            'font_name': 'Arial'
        })

        currency_format = workbook.add_format({
            'num_format': '#,##0.00',
            'border': 1,
            'align': 'right',
            'font_size': 10,
            'font_name': 'Arial'
        })

        text_format = workbook.add_format({
            'border': 1,
            'align': 'right',
            'font_size': 10,
            'font_name': 'Arial'
        })

        total_format = workbook.add_format({
            'bold': True,
            'num_format': '#,##0.00',
            'border': 1,
            'align': 'right',
            'bg_color': '#D9E1F2',
            'font_size': 10,
            'font_name': 'Arial'
        })

        section_format = workbook.add_format({
            'bold': True,
            'border': 1,
            'align': 'right',
            'bg_color': '#E6F2FF',
            'font_size': 10,
            'font_name': 'Arial'
        })

        label_format = workbook.add_format({
            'bold': True,
            'border': 1,
            'align': 'right',
            'font_size': 10,
            'font_name': 'Arial'
        })

        worksheet = workbook.add_worksheet('تقرير مراكز التكلفة')
        worksheet.right_to_left()

        worksheet.set_column('A:A', 30)
        worksheet.set_column('B:B', 20)
        worksheet.set_column('C:C', 20)
        worksheet.set_column('D:D', 30)
        worksheet.set_column('E:E', 15)
        worksheet.set_column('F:F', 15)
        worksheet.set_column('G:G', 20)
        worksheet.set_column('H:H', 20)

        row = 0

        worksheet.merge_range(row, 0, row, 7, 'تقرير مراكز التكلفة', title_format)
        row += 1

        if self.company_id:
            worksheet.merge_range(row, 0, row, 7,
                                  f'الشركة: {self.company_id.name}',
                                  workbook.add_format({
                                      'align': 'center',
                                      'font_size': 12,
                                      'border': 0,
                                      'font_name': 'Arial'
                                  }))
            row += 1

        if self.operating_unit_id:
            worksheet.merge_range(row, 0, row, 7,
                                  f'الفرع: {self.operating_unit_id.name}',
                                  workbook.add_format({
                                      'align': 'center',
                                      'font_size': 12,
                                      'border': 0,
                                      'font_name': 'Arial'
                                  }))
            row += 1

        if self.group_id:
            worksheet.merge_range(row, 0, row, 7,
                                  f'المجموعة: {self.group_id.name}',
                                  workbook.add_format({
                                      'align': 'center',
                                      'font_size': 12,
                                      'border': 0,
                                      'font_name': 'Arial'
                                  }))
            row += 1

        worksheet.merge_range(row, 0, row, 7,
                              f'من {self.date_from} إلى {self.date_to}',
                              workbook.add_format({
                                  'align': 'center',
                                  'font_size': 12,
                                  'border': 0,
                                  'font_name': 'Arial'
                              }))
        row += 2

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

        headers = [
            'الفرع',
            'المجموعة الرئيسية',
            'المجموعة الفرعية',
            'مركز التكلفة',
            'المصروفات',
            'الإيرادات',
            'التحصيل (المدفوعات)',
            'المديونية (المتبقي)'
        ]

        for col_num, header in enumerate(headers):
            worksheet.write(row, col_num, header, header_format)
        row += 1

        analytic_domain = [('company_id', 'in', self.company_ids.ids)]
        if self.operating_unit_id:
            analytic_domain.append(('operating_unit_id', '=', self.operating_unit_id.id))
        if self.group_id:
            analytic_domain.append(('group_id', '=', self.group_id.id))
        if self.analytic_account_ids:
            analytic_domain.append(('id', 'in', self.analytic_account_ids.ids))

        analytic_accounts = self.env['account.analytic.account'].search(analytic_domain,
                                                                        order='operating_unit_id, group_id, name')

        operating_unit_dict = defaultdict(lambda: {
            'groups': defaultdict(lambda: {
                'subgroups': defaultdict(lambda: {
                    'accounts': [],
                    'total_expenses': 0.0,
                    'total_revenues': 0.0,
                    'total_collections': 0.0,
                    'total_debts': 0.0
                }),
                'total_expenses': 0.0,
                'total_revenues': 0.0,
                'total_collections': 0.0,
                'total_debts': 0.0
            }),
            'total_expenses': 0.0,
            'total_revenues': 0.0,
            'total_collections': 0.0,
            'total_debts': 0.0
        })

        for account in analytic_accounts:
            expenses = self._calculate_analytic_amount(account, 'expenses')
            revenues = self._calculate_analytic_amount(account, 'revenues')
            collections = self._calculate_analytic_amount(account, 'collections')
            debts = self._calculate_analytic_amount(account, 'debts')

            operating_unit = account.operating_unit_id or 'بدون فرع'
            operating_unit_name = operating_unit.name if operating_unit != 'بدون فرع' else 'بدون فرع'

            root_group = account.group_id
            while root_group and root_group.parent_id:
                root_group = root_group.parent_id
            root_group_name = root_group.name if root_group else 'بدون مجموعة رئيسية'

            subgroup = account.group_id if account.group_id and account.group_id.parent_id == root_group else None
            subgroup_name = subgroup.name if subgroup else 'بدون مجموعة فرعية'

            operating_unit_dict[operating_unit_name]['groups'][root_group_name]['subgroups'][subgroup_name][
                'accounts'].append({
                'account': account,
                'expenses': expenses,
                'revenues': revenues,
                'collections': collections,
                'debts': debts
            })

            operating_unit_dict[operating_unit_name]['groups'][root_group_name]['subgroups'][subgroup_name][
                'total_expenses'] += expenses
            operating_unit_dict[operating_unit_name]['groups'][root_group_name]['subgroups'][subgroup_name][
                'total_revenues'] += revenues
            operating_unit_dict[operating_unit_name]['groups'][root_group_name]['subgroups'][subgroup_name][
                'total_collections'] += collections
            operating_unit_dict[operating_unit_name]['groups'][root_group_name]['subgroups'][subgroup_name][
                'total_debts'] += debts

            operating_unit_dict[operating_unit_name]['groups'][root_group_name]['total_expenses'] += expenses
            operating_unit_dict[operating_unit_name]['groups'][root_group_name]['total_revenues'] += revenues
            operating_unit_dict[operating_unit_name]['groups'][root_group_name]['total_collections'] += collections
            operating_unit_dict[operating_unit_name]['groups'][root_group_name]['total_debts'] += debts

            operating_unit_dict[operating_unit_name]['total_expenses'] += expenses
            operating_unit_dict[operating_unit_name]['total_revenues'] += revenues
            operating_unit_dict[operating_unit_name]['total_collections'] += collections
            operating_unit_dict[operating_unit_name]['total_debts'] += debts

        # إضافة تنسيق للمجموعات الرئيسية
        main_group_format = workbook.add_format({
            'bold': True,
            'border': 1,
            'align': 'right',
            'bg_color': '#90EE90',  # أخضر فاتح
            'font_size': 10,
            'font_name': 'Arial'
        })

        for operating_unit_name, operating_unit_data in operating_unit_dict.items():
            worksheet.write(row, 0, operating_unit_name, section_format)
            worksheet.merge_range(row, 1, row, 7, "", section_format)
            row += 1

            for root_group_name, root_group_data in operating_unit_data['groups'].items():
                # استخدام التنسيق الأخضر للمجموعة الرئيسية
                worksheet.write(row, 1, root_group_name, main_group_format)
                worksheet.merge_range(row, 2, row, 7, "", main_group_format)
                row += 1

                for subgroup_name, subgroup_data in root_group_data['subgroups'].items():
                    worksheet.write(row, 2, subgroup_name, section_format)
                    worksheet.merge_range(row, 3, row, 7, "", section_format)
                    row += 1

                    for account_data in subgroup_data['accounts']:
                        account = account_data['account']
                        # مراكز التكلفة الفرعية بدون لون خاص
                        worksheet.write(row, 3, account.name, text_format)
                        worksheet.write(row, 4, account_data['expenses'], currency_format)
                        worksheet.write(row, 5, account_data['revenues'], currency_format)
                        worksheet.write(row, 6, account_data['collections'], currency_format)
                        worksheet.write(row, 7, account_data['debts'], currency_format)
                        row += 1

                    # إجمالي المجموعة الفرعية
                    worksheet.write(row, 2, f'إجمالي {subgroup_name}', total_format)
                    worksheet.write(row, 4, subgroup_data['total_expenses'], total_format)
                    worksheet.write(row, 5, subgroup_data['total_revenues'], total_format)
                    worksheet.write(row, 6, subgroup_data['total_collections'], total_format)
                    worksheet.write(row, 7, subgroup_data['total_debts'], total_format)
                    row += 1

                # إجمالي المجموعة الرئيسية بالتنسيق الأخضر
                worksheet.write(row, 1, f'إجمالي {root_group_name}', main_group_format)
                worksheet.write(row, 4, root_group_data['total_expenses'], main_group_format)
                worksheet.write(row, 5, root_group_data['total_revenues'], main_group_format)
                worksheet.write(row, 6, root_group_data['total_collections'], main_group_format)
                worksheet.write(row, 7, root_group_data['total_debts'], main_group_format)
                row += 1

            # إجمالي الفرع
            worksheet.write(row, 0, f'إجمالي {operating_unit_name}', total_format)
            worksheet.write(row, 4, operating_unit_data['total_expenses'], total_format)
            worksheet.write(row, 5, operating_unit_data['total_revenues'], total_format)
            worksheet.write(row, 6, operating_unit_data['total_collections'], total_format)
            worksheet.write(row, 7, operating_unit_data['total_debts'], total_format)
            row += 1

        worksheet.write(row, 0, 'الإجمالي العام', total_format)
        worksheet.write(row, 4, self.total_expenses, total_format)
        worksheet.write(row, 5, self.total_revenues, total_format)
        worksheet.write(row, 6, self.total_collections, total_format)
        worksheet.write(row, 7, self.total_debts, total_format)

        # إضافة جدول المقارنة
        row = self._generate_comparison_table(
            worksheet,
            row + 2,
            0,
            {
                'section_format': section_format,
                'header_format': header_format,
                'text_format': text_format,
                'currency_format': currency_format,
                'total_format': total_format,
                'workbook': workbook  # إضافة workbook للتنسيقات
            }
        )

        workbook.close()
        output.seek(0)

        attachment = self.env['ir.attachment'].create({
            'name': f"تقرير_مراكز_التكلفة_{self.date_from}_إلى_{self.date_to}.xlsx",
            'type': 'binary',
            'datas': base64.b64encode(output.getvalue()),
            'res_model': 'analytic.account.report',
            'res_id': self.id,
            'mimetype': 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        })

        return {
            'type': 'ir.actions.act_url',
            'url': f'/web/content/{attachment.id}?download=true',
            'target': 'self',
        }

    def generate_pdf_report(self):
        """إنشاء تقرير PDF لتقرير مراكز التكلفة"""
        self.ensure_one()
        try:
            output = io.BytesIO()
            doc = SimpleDocTemplate(output, pagesize=landscape(letter), rightMargin=20, leftMargin=20, topMargin=30,
                                    bottomMargin=30)

            try:
                pdfmetrics.registerFont(TTFont('Arabic', 'arial.ttf'))
            except:
                logger.warning("Failed to register Arabic font, using default")

            styles = getSampleStyleSheet()
            title_style = ParagraphStyle(
                'Title',
                parent=styles['Title'],
                fontName='Arabic',
                fontSize=16,
                alignment=1,
                textColor=colors.HexColor('#4472C4')
            )

            header_style = ParagraphStyle(
                'Header',
                parent=styles['Normal'],
                fontName='Arabic',
                fontSize=12,
                alignment=1,
                textColor=colors.white,
                backColor=colors.HexColor('#4472C4')
            )

            normal_style = ParagraphStyle(
                'Normal',
                parent=styles['Normal'],
                fontName='Arabic',
                fontSize=10,
                alignment=2
            )

            currency_style = ParagraphStyle(
                'Currency',
                parent=styles['Normal'],
                fontName='Arabic',
                fontSize=10,
                alignment=2
            )

            total_style = ParagraphStyle(
                'Total',
                parent=styles['Normal'],
                fontName='Arabic',
                fontSize=10,
                alignment=2,
                fontWeight='bold',
                backColor=colors.HexColor('#D9E1F2')
            )

            section_style = ParagraphStyle(
                'Section',
                parent=styles['Normal'],
                fontName='Arabic',
                fontSize=10,
                alignment=2,
                fontWeight='bold',
                backColor=colors.HexColor('#E6F2FF')
            )

            elements = []

            title = Paragraph("تقرير مراكز التكلفة", title_style)
            elements.append(title)

            if self.company_ids:
                companies = ", ".join(self.company_ids.mapped('name'))
                company_info = Paragraph(f"الشركات: {companies}", normal_style)
                elements.append(company_info)

            if self.operating_unit_id:
                operating_unit_info = Paragraph(f"الفرع: {self.operating_unit_id.name}", normal_style)
                elements.append(operating_unit_info)

            if self.group_id:
                group_info = Paragraph(f"المجموعة: {self.group_id.name}", normal_style)
                elements.append(group_info)

            date_range = Paragraph(f"من {self.date_from} إلى {self.date_to}", normal_style)
            elements.append(date_range)

            elements.append(Spacer(1, 20))

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

            report_header = [
                'الفرع',
                'المجموعة الرئيسية',
                'المجموعة الفرعية',
                'مركز التكلفة',
                'المصروفات',
                'الإيرادات',
                'التحصيل (المدفوعات)',
                'المديونية (المتبقي)'
            ]

            report_data = [report_header]

            company_ids = [c.id for c in self.company_ids if c._name == 'res.company' and c.id]
            if not company_ids:
                return {
                    'file_name': f"تقرير_مراكز_التكلفة_{self.date_from}_إلى_{self.date_to}.pdf",
                    'file_content': b'',
                    'file_type': 'application/pdf'
                }

            analytic_domain = [('company_id', 'in', company_ids)]

            if self.operating_unit_id:
                analytic_domain.append(('operating_unit_id', '=', self.operating_unit_id.id))
            if self.group_id:
                analytic_domain.append(('group_id', '=', self.group_id.id))
            if self.analytic_account_ids:
                analytic_account_ids = [a.id for a in self.analytic_account_ids if
                                        a._name == 'account.analytic.account' and a.id]
                if analytic_account_ids:
                    analytic_domain.append(('id', 'in', analytic_account_ids))

            analytic_accounts = self.env['account.analytic.account'].search(analytic_domain)

            operating_unit_dict = defaultdict(lambda: {
                'groups': defaultdict(lambda: {
                    'subgroups': defaultdict(lambda: {
                        'accounts': [],
                        'total_expenses': 0.0,
                        'total_revenues': 0.0,
                        'total_collections': 0.0,
                        'total_debts': 0.0
                    }),
                    'total_expenses': 0.0,
                    'total_revenues': 0.0,
                    'total_collections': 0.0,
                    'total_debts': 0.0
                }),
                'total_expenses': 0.0,
                'total_revenues': 0.0,
                'total_collections': 0.0,
                'total_debts': 0.0
            })

            for account in analytic_accounts:
                expenses = self._calculate_analytic_amount(account, 'expenses')
                revenues = self._calculate_analytic_amount(account, 'revenues')
                collections = self._calculate_analytic_amount(account, 'collections')
                debts = self._calculate_analytic_amount(account, 'debts')

                operating_unit = account.operating_unit_id or 'بدون فرع'
                operating_unit_name = operating_unit.name if operating_unit != 'بدون فرع' else 'بدون فرع'

                root_group = account.group_id
                while root_group and root_group.parent_id:
                    root_group = root_group.parent_id
                root_group_name = root_group.name if root_group else 'بدون مجموعة رئيسية'

                subgroup = account.group_id if account.group_id and account.group_id.parent_id == root_group else None
                subgroup_name = subgroup.name if subgroup else 'بدون مجموعة فرعية'

                operating_unit_dict[operating_unit_name]['groups'][root_group_name]['subgroups'][subgroup_name][
                    'accounts'].append({
                    'account': account,
                    'expenses': expenses,
                    'revenues': revenues,
                    'collections': collections,
                    'debts': debts
                })

                operating_unit_dict[operating_unit_name]['groups'][root_group_name]['subgroups'][subgroup_name][
                    'total_expenses'] += expenses
                operating_unit_dict[operating_unit_name]['groups'][root_group_name]['subgroups'][subgroup_name][
                    'total_revenues'] += revenues
                operating_unit_dict[operating_unit_name]['groups'][root_group_name]['subgroups'][subgroup_name][
                    'total_collections'] += collections
                operating_unit_dict[operating_unit_name]['groups'][root_group_name]['subgroups'][subgroup_name][
                    'total_debts'] += debts

                operating_unit_dict[operating_unit_name]['groups'][root_group_name]['total_expenses'] += expenses
                operating_unit_dict[operating_unit_name]['groups'][root_group_name]['total_revenues'] += revenues
                operating_unit_dict[operating_unit_name]['groups'][root_group_name]['total_collections'] += collections
                operating_unit_dict[operating_unit_name]['groups'][root_group_name]['total_debts'] += debts

                operating_unit_dict[operating_unit_name]['total_expenses'] += expenses
                operating_unit_dict[operating_unit_name]['total_revenues'] += revenues
                operating_unit_dict[operating_unit_name]['total_collections'] += collections
                operating_unit_dict[operating_unit_name]['total_debts'] += debts

            for operating_unit_name, operating_unit_data in operating_unit_dict.items():
                report_data.append([
                    operating_unit_name, '', '', '', '', '', '', ''
                ])

                for root_group_name, root_group_data in operating_unit_data['groups'].items():
                    report_data.append([
                        '', root_group_name, '', '', '', '', '', ''
                    ])

                    for subgroup_name, subgroup_data in root_group_data['subgroups'].items():
                        report_data.append([
                            '', '', subgroup_name, '', '', '', '', ''
                        ])

                        for account_data in subgroup_data['accounts']:
                            account = account_data['account']
                            report_data.append([
                                '', '', '', account.name,
                                format(round(account_data['expenses'], 2), ',.2f'),
                                format(round(account_data['revenues'], 2), ',.2f'),
                                format(round(account_data['collections'], 2), ',.2f'),
                                format(round(account_data['debts'], 2), ',.2f')
                            ])

                        report_data.append([
                            '', '', f'إجمالي {subgroup_name}', '',
                            format(round(subgroup_data['total_expenses'], 2), ',.2f'),
                            format(round(subgroup_data['total_revenues'], 2), ',.2f'),
                            format(round(subgroup_data['total_collections'], 2), ',.2f'),
                            format(round(subgroup_data['total_debts'], 2), ',.2f')
                        ])

                    report_data.append([
                        '', f'إجمالي {root_group_name}', '', '',
                        format(round(root_group_data['total_expenses'], 2), ',.2f'),
                        format(round(root_group_data['total_revenues'], 2), ',.2f'),
                        format(round(root_group_data['total_collections'], 2), ',.2f'),
                        format(round(root_group_data['total_debts'], 2), ',.2f')
                    ])

                report_data.append([
                    f'إجمالي {operating_unit_name}', '', '', '',
                    format(round(operating_unit_data['total_expenses'], 2), ',.2f'),
                    format(round(operating_unit_data['total_revenues'], 2), ',.2f'),
                    format(round(operating_unit_data['total_collections'], 2), ',.2f'),
                    format(round(operating_unit_data['total_debts'], 2), ',.2f')
                ])

            report_data.append([
                'الإجمالي العام', '', '', '',
                format(round(self.total_expenses, 2), ',.2f'),
                format(round(self.total_revenues, 2), ',.2f'),
                format(round(self.total_collections, 2), ',.2f'),
                format(round(self.total_debts, 2), ',.2f')
            ])

            report_table = Table(report_data, colWidths=[60, 60, 60, 90, 50, 50, 50, 50])
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
                ('FONTWEIGHT', (0, 0), (0, -1), 'BOLD'),
                ('BACKGROUND', (1, 0), (1, -1), colors.HexColor('#E6F2FF')),
                ('FONTWEIGHT', (1, 0), (1, -1), 'BOLD'),
                ('BACKGROUND', (2, 0), (2, -1), colors.HexColor('#E6F2FF')),
                ('FONTWEIGHT', (2, 0), (2, -1), 'BOLD')
            ]))

            elements.append(report_table)

            # إضافة قسم المقارنة إذا تم تفعيله
            if self.compare_years and self.previous_years_data:
                comparison_data = json.loads(self.previous_years_data)

                elements.append(Spacer(1, 20))
                elements.append(Paragraph("مقارنة بالسنوات السابقة", title_style))
                elements.append(Spacer(1, 10))

                comparison_table_data = [
                    ['السنة', 'المصروفات', 'الإيرادات', 'التحصيل', 'المديونية']
                ]

                for year_data in comparison_data:
                    comparison_table_data.append([
                        str(year_data['year']),
                        format(round(year_data['expenses'], 2), ',.2f'),
                        format(round(year_data['revenues'], 2), ',.2f'),
                        format(round(year_data['collections'], 2), ',.2f'),
                        format(round(year_data['debts'], 2), ',.2f')
                    ])

                comparison_table_data.append([
                    f"{fields.Date.from_string(self.date_from).year} (الحالية)",
                    format(round(self.total_expenses, 2), ',.2f'),
                    format(round(self.total_revenues, 2), ',.2f'),
                    format(round(self.total_collections, 2), ',.2f'),
                    format(round(self.total_debts, 2), ',.2f')
                ])

                comparison_table = Table(comparison_table_data, colWidths=[60, 60, 60, 60, 60])
                comparison_table.setStyle(TableStyle([
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
                    ('FONTWEIGHT', (0, -1), (-1, -1), 'BOLD')
                ]))

                elements.append(comparison_table)

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
        return self.generate_excel_report()

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

        if self.operating_unit_id:
            domain.append(('account_id.operating_unit_id', '=', self.operating_unit_id.id))
        if self.group_id:
            domain.append(('account_id.group_id', '=', self.group_id.id))
        if self.analytic_account_ids:
            analytic_account_ids = [a.id for a in self.analytic_account_ids if
                                    a._name == 'account.analytic.account' and a.id]
            if analytic_account_ids:
                domain.append(('account_id', 'in', analytic_account_ids))

        action['domain'] = domain
        action['context'] = {
            'search_default_group_by_account': 1,
            'create': False
        }
        return action

    @api.model
    def get_available_groups_for_operating_unit(self, operating_unit_id, company_ids):
        """الحصول على المجموعات المتاحة لفرع معين"""
        if not operating_unit_id or not company_ids:
            return self.env['account.analytic.group']

        analytic_accounts = self.env['account.analytic.account'].search([
            ('operating_unit_id', '=', operating_unit_id),
            ('company_id', 'in', company_ids),
            ('group_id', '!=', False)
        ])

        group_ids = analytic_accounts.mapped('group_id.id')
        return self.env['account.analytic.group'].browse(group_ids)

    @api.model
    def get_available_accounts_for_group_and_unit(self, group_id, operating_unit_id, company_ids):
        """الحصول على مراكز التكلفة المتاحة لمجموعة وفرع معينين"""
        domain = [('company_id', 'in', company_ids), ('active', '=', True)]

        if group_id:
            domain.append(('group_id', '=', group_id))

        if operating_unit_id:
            domain.append(('operating_unit_id', '=', operating_unit_id))

        return self.env['account.analytic.account'].search(domain)

    @api.constrains('year_compare_count')
    def _check_year_compare_count(self):
        """التحقق من صحة عدد السنوات للمقارنة"""
        for record in self:
            if record.compare_years and (record.year_compare_count < 1 or record.year_compare_count > 5):
                raise ValidationError("عدد السنوات للمقارنة يجب أن يكون بين 1 و 5")

    def debug_data(self):
        """دالة للتشخيص وفحص البيانات"""
        self.ensure_one()

        logger.info("=== تشخيص البيانات ===")
        logger.info(f"الفترة: من {self.date_from} إلى {self.date_to}")
        logger.info(f"الشركات: {[c.name for c in self.company_ids]}")
        logger.info(f"الفرع: {self.operating_unit_id.name if self.operating_unit_id else 'غير محدد'}")
        logger.info(f"مراكز التكلفة: {len(self.analytic_account_ids)}")

        domain = [
            ('date', '>=', self.date_from),
            ('date', '<=', self.date_to),
            ('company_id', 'in', self.company_ids.ids),
            ('move_id.state', '=', 'posted')
        ]

        if self.operating_unit_id:
            domain.append(('analytic_account_id.operating_unit_id', '=', self.operating_unit_id.id))

        all_lines = self.env['account.move.line'].search(domain)
        logger.info(f"إجمالي القيود في الفترة: {len(all_lines)}")

        lines_with_analytic = all_lines.filtered(lambda l: l.analytic_account_id)
        logger.info(f"القيود المرتبطة بمراكز تكلفة: {len(lines_with_analytic)}")

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

    def check_analytic_accounts_availability(self):
        """دالة للتحقق من توفر مراكز التكلفة"""
        self.ensure_one()

        logger.info("=== فحص توفر مراكز التكلفة ===")

        all_accounts = self.env['account.analytic.account'].search([])
        active_accounts = self.env['account.analytic.account'].search([('active', '=', True)])

        logger.info(f"إجمالي مراكز التكلفة: {len(all_accounts)}")
        logger.info(f"مراكز التكلفة النشطة: {len(active_accounts)}")

        if self.company_ids:
            for company in self.company_ids:
                company_accounts = self.env['account.analytic.account'].search([
                    ('active', '=', True),
                    ('company_id', '=', company.id)
                ])
                logger.info(f"مراكز التكلفة للشركة {company.name}: {len(company_accounts)}")

        if self.operating_unit_id:
            unit_accounts = self.env['account.analytic.account'].search([
                ('active', '=', True),
                ('operating_unit_id', '=', self.operating_unit_id.id)
            ])
            logger.info(f"مراكز التكلفة للفرع {self.operating_unit_id.name}: {len(unit_accounts)}")

        if self.group_id:
            group_accounts = self.env['account.analytic.account'].search([
                ('active', '=', True),
                ('group_id', '=', self.group_id.id)
            ])
            logger.info(f"مراكز التكلفة للمجموعة {self.group_id.name}: {len(group_accounts)}")

        return {
            'total_accounts': len(all_accounts),
            'active_accounts': len(active_accounts),
            'computed_accounts': len(self.analytic_account_ids)
        }

    def debug_data_calculation(self):
        """دالة تشخيص لفحص البيانات والتأكد من صحة الحسابات"""
        for record in self:
            company_ids = record.company_ids.ids if record.company_ids else []
            analytic_account_ids = record.analytic_account_ids.ids if record.analytic_account_ids else []
            
            logger.info(f"""
            === تشخيص البيانات ===
            الشركات المحددة: {company_ids}
            مراكز التكلفة: {len(analytic_account_ids)}
            من تاريخ: {record.date_from}
            إلى تاريخ: {record.date_to}
            """)
            
            # فحص وجود حركات في الفترة
            total_lines = self.env['account.move.line'].search_count([
                ('date', '>=', record.date_from),
                ('date', '<=', record.date_to),
                ('company_id', 'in', company_ids),
                ('move_id.state', '=', 'posted')
            ])
            
            logger.info(f"إجمالي الحركات في الفترة: {total_lines}")
            
            # فحص الحركات مع مراكز التكلفة
            analytic_lines = self.env['account.move.line'].search_count([
                ('date', '>=', record.date_from),
                ('date', '<=', record.date_to),
                ('company_id', 'in', company_ids),
                ('analytic_account_id', 'in', analytic_account_ids),
                ('move_id.state', '=', 'posted')
            ])
            
            logger.info(f"الحركات مع مراكز التكلفة: {analytic_lines}")
            
            return True
