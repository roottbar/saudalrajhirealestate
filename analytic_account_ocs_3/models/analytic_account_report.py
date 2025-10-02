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
        string='Analytic Accounts',
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

    @api.depends('group_id', 'analytic_account_id', 'company_ids', 'operating_unit_id')
    def _compute_analytic_accounts(self):
        """حساب مراكز التكلفة بناءً على المعايير المحددة مع التسلسل الهرمي"""
        for record in self:
            try:
                domain = [('active', '=', True)]
                
                # 1. تصفية حسب الشركات (إجباري)
                if record.company_ids:
                    company_ids = [c.id for c in record.company_ids if hasattr(c, 'id') and c.id]
                    if company_ids:
                        domain.append(('company_id', 'in', company_ids))
                    else:
                        record.analytic_account_ids = self.env['account.analytic.account']
                        continue
                else:
                    # إذا لم يتم اختيار شركات، استخدم الشركة الحالية
                    domain.append(('company_id', '=', self.env.company.id))

                # 2. تصفية حسب الفرع (اختياري)
                if record.operating_unit_id and hasattr(record.operating_unit_id, 'id') and record.operating_unit_id.id:
                    domain.append(('operating_unit_id', '=', record.operating_unit_id.id))
                    
                # 3. تصفية حسب المجموعة (اختياري)
                if record.group_id and hasattr(record.group_id, 'id') and record.group_id.id:
                    # إذا تم اختيار مجموعة، عرض مراكز التكلفة في هذه المجموعة أو مجموعاتها الفرعية
                    group_ids = [record.group_id.id]
                    # إضافة المجموعات الفرعية
                    child_groups = self.env['account.analytic.group'].search([('parent_id', 'child_of', record.group_id.id)])
                    group_ids.extend(child_groups.ids)
                    domain.append(('group_id', 'in', group_ids))
                        
                # 4. تصفية حسب مركز التكلفة المحدد (اختياري)
                if record.analytic_account_id and hasattr(record.analytic_account_id, 'id') and record.analytic_account_id.id:
                    domain.append(('id', '=', record.analytic_account_id.id))

                analytic_accounts = self.env['account.analytic.account'].search(domain)
                record.analytic_account_ids = analytic_accounts
                
                # تسجيل معلومات التشخيص
                logger.info(f"=== تشخيص مراكز التكلفة للسجل {record.id} ===")
                logger.info(f"الشركات المختارة: {[c.name for c in record.company_ids] if record.company_ids else ['الشركة الحالية']}")
                logger.info(f"الفرع المختار: {record.operating_unit_id.name if record.operating_unit_id else 'جميع الفروع'}")
                logger.info(f"المجموعة المختارة: {record.group_id.name if record.group_id else 'جميع المجموعات'}")
                logger.info(f"مركز التكلفة المحدد: {record.analytic_account_id.name if record.analytic_account_id else 'جميع مراكز التكلفة'}")
                logger.info(f"Domain المستخدم: {domain}")
                logger.info(f"عدد مراكز التكلفة الموجودة: {len(analytic_accounts)}")
                
                if analytic_accounts:
                    logger.info(f"أسماء مراكز التكلفة: {[acc.name for acc in analytic_accounts[:5]]}{'...' if len(analytic_accounts) > 5 else ''}")
                else:
                    logger.warning("لم يتم العثور على أي مراكز تكلفة تطابق المعايير المحددة")
                    
            except Exception as e:
                logger.error("خطأ في حساب مراكز التكلفة: %s", str(e))
                record.analytic_account_ids = self.env['account.analytic.account']

    @api.depends('date_from', 'date_to', 'company_ids', 'analytic_account_ids', 'operating_unit_id', 'group_id', 'analytic_account_id')
    def _compute_totals(self):
        for record in self:
            try:
                if not record.company_ids:
                    record.total_expenses = 0.0
                    record.total_revenues = 0.0
                    record.total_collections = 0.0
                    record.total_debts = 0.0
                    continue

                company_ids = [c.id for c in record.company_ids]
                
                # استخدام مراكز التكلفة المحسوبة أو جميع مراكز التكلفة للشركة
                if record.analytic_account_ids:
                    analytic_account_ids = [a.id for a in record.analytic_account_ids]
                else:
                    # إذا لم توجد مراكز تكلفة محسوبة، استخدم جميع مراكز التكلفة للشركة
                    all_accounts = self.env['account.analytic.account'].search([
                        ('company_id', 'in', company_ids),
                        ('active', '=', True)
                    ])
                    analytic_account_ids = all_accounts.ids
                
                if not analytic_account_ids:
                    record.total_expenses = 0.0
                    record.total_revenues = 0.0
                    record.total_collections = 0.0
                    record.total_debts = 0.0
                    continue
                
                # بناء Domain أساسي للبحث
                base_domain = [
                    ('date', '>=', record.date_from),
                    ('date', '<=', record.date_to),
                    ('company_id', 'in', company_ids),
                    ('analytic_account_id', 'in', analytic_account_ids),
                    ('move_id.state', '=', 'posted')
                ]
                
                # حساب المصروفات
                expense_domain = base_domain + [('account_id.internal_group', '=', 'expense')]
                expense_lines = self.env['account.move.line'].search(expense_domain)
                record.total_expenses = sum(expense_lines.mapped('balance'))
                
                # حساب الإيرادات
                revenue_domain = base_domain + [('account_id.internal_group', '=', 'income')]
                revenue_lines = self.env['account.move.line'].search(revenue_domain)
                record.total_revenues = sum(revenue_lines.mapped('balance'))
                
                # حساب التحصيلات
                payment_domain = base_domain + [('payment_id', '!=', False)]
                payment_lines = self.env['account.move.line'].search(payment_domain)
                record.total_collections = sum(abs(line.balance) for line in payment_lines)
                
                # حساب الديون
                invoice_domain = base_domain + [
                    ('move_id.move_type', 'in', ['out_invoice', 'in_invoice']),
                    ('move_id.payment_state', 'in', ['not_paid', 'partial'])
                ]
                invoice_lines = self.env['account.move.line'].search(invoice_domain)
                record.total_debts = sum(line.amount_residual for line in invoice_lines)
                
                logger.info(f"حساب الإجماليات - الشركات: {len(company_ids)}, مراكز التكلفة: {len(analytic_account_ids)}")
                logger.info(f"المصروفات: {record.total_expenses}, الإيرادات: {record.total_revenues}")
                logger.info(f"التحصيلات: {record.total_collections}, الديون: {record.total_debts}")
                
            except Exception as e:
                logger.error("Error in _compute_totals: %s", str(e))
                record.total_expenses = 0.0
                record.total_revenues = 0.0
                record.total_collections = 0.0
                record.total_debts = 0.0

    @api.depends('date_from', 'date_to', 'company_ids', 'analytic_account_ids', 'operating_unit_id')
    def _compute_report_lines(self):
        for record in self:
            try:
                if len(record.analytic_account_ids) > 100:
                    record.report_lines = "<p>عدد مراكز التكلفة كبير جداً. يرجى تحديد فلاتر أكثر تحديداً.</p>"
                    continue
                
                company_ids = [c.id for c in record.company_ids if c._name == 'res.company' and c.id] if record.company_ids else []
                
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
                
                analytic_account_ids = [a.id for a in record.analytic_account_ids if a._name == 'account.analytic.account' and a.id]
                if not analytic_account_ids:
                    record.report_lines = "<p>لا توجد مراكز تكلفة صالحة</p>"
                    continue
                    
                # تجميع البيانات حسب الفرع والمجموعات
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
                    # حساب القيم لكل حساب تحليلي
                    expenses = self._calculate_analytic_amount(account, 'expenses')
                    revenues = self._calculate_analytic_amount(account, 'revenues')
                    collections = self._calculate_analytic_amount(account, 'collections')
                    debts = self._calculate_analytic_amount(account, 'debts')
                    
                    # الحصول على الفرع
                    operating_unit = account.operating_unit_id or 'بدون فرع'
                    operating_unit_name = operating_unit.name if operating_unit != 'بدون فرع' else 'بدون فرع'
                    
                    # الحصول على المجموعة الرئيسية (المستوى الأول)
                    root_group = account.group_id
                    while root_group and root_group.parent_id:
                        root_group = root_group.parent_id
                    root_group_name = root_group.name if root_group else 'بدون مجموعة رئيسية'
                    
                    # الحصول على المجموعة الفرعية (المستوى الثاني)
                    subgroup = account.group_id if account.group_id and account.group_id.parent_id == root_group else None
                    subgroup_name = subgroup.name if subgroup else 'بدون مجموعة فرعية'
                    
                    # تخزين البيانات في الهيكل الهرمي
                    operating_unit_dict[operating_unit_name]['groups'][root_group_name]['subgroups'][subgroup_name]['accounts'].append({
                        'account': account,
                        'expenses': expenses,
                        'revenues': revenues,
                        'collections': collections,
                        'debts': debts
                    })
                    
                    # تحديث الإجماليات
                    operating_unit_dict[operating_unit_name]['groups'][root_group_name]['subgroups'][subgroup_name]['total_expenses'] += expenses
                    operating_unit_dict[operating_unit_name]['groups'][root_group_name]['subgroups'][subgroup_name]['total_revenues'] += revenues
                    operating_unit_dict[operating_unit_name]['groups'][root_group_name]['subgroups'][subgroup_name]['total_collections'] += collections
                    operating_unit_dict[operating_unit_name]['groups'][root_group_name]['subgroups'][subgroup_name]['total_debts'] += debts
                    
                    operating_unit_dict[operating_unit_name]['groups'][root_group_name]['total_expenses'] += expenses
                    operating_unit_dict[operating_unit_name]['groups'][root_group_name]['total_revenues'] += revenues
                    operating_unit_dict[operating_unit_name]['groups'][root_group_name]['total_collections'] += collections
                    operating_unit_dict[operating_unit_name]['groups'][root_group_name]['total_debts'] += debts
                    
                    operating_unit_dict[operating_unit_name]['total_expenses'] += expenses
                    operating_unit_dict[operating_unit_name]['total_revenues'] += revenues
                    operating_unit_dict[operating_unit_name]['total_collections'] += collections
                    operating_unit_dict[operating_unit_name]['total_debts'] += debts

                # عرض النتائج حسب التسلسل الهرمي
                for operating_unit_name, operating_unit_data in operating_unit_dict.items():
                    # عنوان الفرع
                    html_lines.append(f"""
                        <tr class="section-row">
                            <td colspan="8">{operating_unit_name}</td>
                        </tr>
                    """)

                    for root_group_name, root_group_data in operating_unit_data['groups'].items():
                        # عنوان المجموعة الرئيسية
                        html_lines.append(f"""
                            <tr class="section-row">
                                <td></td>
                                <td colspan="7">{root_group_name}</td>
                            </tr>
                        """)

                        for subgroup_name, subgroup_data in root_group_data['subgroups'].items():
                            # عنوان المجموعة الفرعية
                            html_lines.append(f"""
                                <tr class="section-row">
                                    <td></td>
                                    <td></td>
                                    <td colspan="6">{subgroup_name}</td>
                                </tr>
                            """)

                            # بيانات مراكز التكلفة
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

                            # إجمالي المجموعة الفرعية
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

                        # إجمالي المجموعة الرئيسية
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

                    # إجمالي الفرع
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

                # الإجمالي العام
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

                record.report_lines = '\n'.join(html_lines)
            except Exception as e:
                logger.error("Error computing report lines: %s", str(e))
                record.report_lines = "<p>حدث خطأ أثناء توليد التقرير</p>"

    @api.onchange('company_ids')
    def _onchange_company_ids(self):
        """تحديث الفروع والمجموعات ومراكز التكلفة عند تغيير الشركات"""
        if self.company_ids:
            company_ids = [c.id for c in self.company_ids]
            
            # إعادة تعيين الحقول إذا لم تعد صالحة
            if self.operating_unit_id and self.operating_unit_id.company_id.id not in company_ids:
                self.operating_unit_id = False
                
            if self.group_id and self.group_id.company_id.id not in company_ids:
                self.group_id = False
                
            if self.analytic_account_id and self.analytic_account_id.company_id.id not in company_ids:
                self.analytic_account_id = False
                
            return {
                'domain': {
                    'operating_unit_id': [('company_id', 'in', company_ids)],
                    'group_id': [('company_id', 'in', company_ids)],
                    'analytic_account_id': [('company_id', 'in', company_ids), ('active', '=', True)]
                }
            }
        else:
            # إذا لم يتم اختيار شركات، إعادة تعيين جميع الحقول
            self.operating_unit_id = False
            self.group_id = False
            self.analytic_account_id = False
            
            return {
                'domain': {
                    'operating_unit_id': [('id', '=', False)],
                    'group_id': [('id', '=', False)],
                    'analytic_account_id': [('id', '=', False)]
                }
            }

    @api.onchange('operating_unit_id')
    def _onchange_operating_unit_id(self):
        """تحديث المجموعات المتاحة عند تغيير الفرع"""
        company_ids = [c.id for c in self.company_ids] if self.company_ids else [self.env.company.id]
        
        if self.operating_unit_id:
            # البحث عن المجموعات التي لها مراكز تكلفة مرتبطة بالفرع المختار
            analytic_accounts = self.env['account.analytic.account'].search([
                ('operating_unit_id', '=', self.operating_unit_id.id),
                ('company_id', 'in', company_ids),
                ('active', '=', True)
            ])
            
            group_ids = analytic_accounts.mapped('group_id').ids
            
            # تصفية المجموعات
            group_domain = [('company_id', 'in', company_ids)]
            if group_ids:
                group_domain.append(('id', 'in', group_ids))
                
            # إعادة تعيين المجموعة ومركز التكلفة إذا لم تعد صالحة
            if self.group_id and self.group_id.id not in group_ids:
                self.group_id = False
            if self.analytic_account_id and self.analytic_account_id.operating_unit_id != self.operating_unit_id:
                self.analytic_account_id = False
                
            return {
                'domain': {
                    'group_id': group_domain,
                    'analytic_account_id': [
                        ('operating_unit_id', '=', self.operating_unit_id.id),
                        ('company_id', 'in', company_ids),
                        ('active', '=', True)
                    ]
                }
            }
        else:
            # إذا لم يتم اختيار فرع، عرض جميع المجموعات ومراكز التكلفة للشركة
            return {
                'domain': {
                    'group_id': [('company_id', 'in', company_ids)],
                    'analytic_account_id': [('company_id', 'in', company_ids), ('active', '=', True)]
                }
            }

    @api.onchange('group_id')
    def _onchange_group_id(self):
        """تحديث مراكز التكلفة المتاحة عند تغيير المجموعة"""
        company_ids = [c.id for c in self.company_ids] if self.company_ids else [self.env.company.id]
        
        if self.group_id:
            # تصفية مراكز التكلفة حسب المجموعة والفرع والشركة
            domain = [
                ('group_id', 'child_of', self.group_id.id),  # تشمل المجموعات الفرعية
                ('company_id', 'in', company_ids),
                ('active', '=', True)
            ]
            
            if self.operating_unit_id:
                domain.append(('operating_unit_id', '=', self.operating_unit_id.id))
                
            # إعادة تعيين مركز التكلفة إذا لم يعد صالحاً
            if self.analytic_account_id:
                valid_accounts = self.env['account.analytic.account'].search(domain)
                if self.analytic_account_id not in valid_accounts:
                    self.analytic_account_id = False
                    
            return {
                'domain': {
                    'analytic_account_id': domain
                }
            }
        else:
            # إذا لم يتم اختيار مجموعة، عرض جميع مراكز التكلفة حسب الفرع والشركة
            domain = [
                ('company_id', 'in', company_ids),
                ('active', '=', True)
            ]
            
            if self.operating_unit_id:
                domain.append(('operating_unit_id', '=', self.operating_unit_id.id))
                
            return {
                'domain': {
                    'analytic_account_id': domain
                }
            }

    @api.constrains('company_ids', 'group_id', 'analytic_account_id', 'operating_unit_id')
    def _check_company_consistency(self):
        """التحقق من تطابق الشركات مع الحقول المرتبطة"""
        for record in self:
            if not record.company_ids:
                continue
                
            company_ids = [c.id for c in record.company_ids if hasattr(c, 'id') and c.id]
            if not company_ids:
                continue

            # التحقق من الفرع
            if record.operating_unit_id and record.operating_unit_id.id:
                if hasattr(record.operating_unit_id, 'company_id') and record.operating_unit_id.company_id:
                    if record.operating_unit_id.company_id.id not in company_ids:
                        raise ValidationError("الفرع المحدد لا ينتمي لأي من الشركات المحددة")

            # التحقق من المجموعة
            if record.group_id and hasattr(record.group_id, 'id') and record.group_id.id:
                if not hasattr(record.group_id, 'company_id') or not record.group_id.company_id:
                    raise ValidationError("المجموعة المحددة لا تحتوي على شركة")
                elif record.group_id.company_id.id not in company_ids:
                    raise ValidationError("المجموعة المحددة لا تنتمي لأي من الشركات المحددة")
                    
            # التحقق من مركز التكلفة
            if record.analytic_account_id and record.analytic_account_id.id:
                if hasattr(record.analytic_account_id, 'company_id') and record.analytic_account_id.company_id:
                    if record.analytic_account_id.company_id.id not in company_ids:
                        raise ValidationError("مركز التكلفة المحدد لا ينتمي لأي من الشركات المحددة")
                        
                # التحقق من تطابق الفرع
                if record.operating_unit_id and hasattr(record.analytic_account_id, 'operating_unit_id'):
                    if record.analytic_account_id.operating_unit_id != record.operating_unit_id:
                        raise ValidationError("مركز التكلفة المحدد لا ينتمي للفرع المختار")
                        
                # التحقق من تطابق المجموعة
                if record.group_id and hasattr(record.analytic_account_id, 'group_id'):
                    if record.analytic_account_id.group_id != record.group_id:
                        raise ValidationError("مركز التكلفة المحدد لا ينتمي للمجموعة المختارة")

    @api.onchange('date_from')
    def _onchange_date_from(self):
        if self.date_from and not self.date_to:
            self.date_to = self.date_from

    @api.constrains('date_from', 'date_to')
    def _check_dates(self):
        for record in self:
            if record.date_from and record.date_to and record.date_from > record.date_to:
                raise ValidationError("تاريخ البداية يجب أن يكون قبل تاريخ النهاية")

    def _calculate_analytic_amount(self, account, amount_type):
        """حساب المبلغ لحساب تحليلي محدد"""
        try:
            if not account or not account.id:
                return 0.0
                
            company_ids = [c.id for c in self.company_ids if hasattr(c, 'id') and c.id]
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
                # المصروفات - البحث في حسابات المصروفات
                domain = base_domain + [
                    ('account_id.user_type_id.name', 'in', ['Expenses', 'Cost of Revenue'])
                ]
                lines = self.env['account.move.line'].search(domain)
                return sum(abs(line.debit - line.credit) for line in lines if line.debit > line.credit)
                
            elif amount_type == 'revenues':
                # الإيرادات - البحث في حسابات الإيرادات
                domain = base_domain + [
                    ('account_id.user_type_id.name', 'in', ['Income', 'Other Income'])
                ]
                lines = self.env['account.move.line'].search(domain)
                return sum(abs(line.credit - line.debit) for line in lines if line.credit > line.debit)
                
            elif amount_type == 'collections':
                # التحصيلات - البحث في المدفوعات
                domain = base_domain + [
                    ('payment_id', '!=', False)
                ]
                lines = self.env['account.move.line'].search(domain)
                return sum(abs(line.credit) for line in lines)
                
            elif amount_type == 'debts':
                # الديون - البحث في الفواتير غير المدفوعة
                domain = base_domain + [
                    ('move_id.move_type', 'in', ['out_invoice', 'in_invoice']),
                    ('move_id.payment_state', 'in', ['not_paid', 'partial'])
                ]
                lines = self.env['account.move.line'].search(domain)
                return sum(line.amount_residual for line in lines if line.amount_residual > 0)
                
            return 0.0
            
        except Exception as e:
            logger.error(f"Error calculating {amount_type} for account {account.name}: {str(e)}")
            return 0.0

    def generate_excel_report(self):
        """إنشاء وتنزيل تقرير Excel لمراكز التكلفة"""
        self.ensure_one()
        
        # إنشاء كتاب Excel
        output = io.BytesIO()
        workbook = xlsxwriter.Workbook(output, {
            'in_memory': True,
            'right_to_left': True,
            'strings_to_numbers': True,
            'remove_timezone': True,
            'default_date_format': 'dd/mm/yyyy'
        })
        
        # إعداد التنسيقات مع دعم اللغة العربية
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
        
        # إعداد أعمدة الورقة
        worksheet.set_column('A:A', 30)  # عمود الفرع/المجموعة/مركز التكلفة
        worksheet.set_column('B:B', 20)  # عمود المجموعة الرئيسية
        worksheet.set_column('C:C', 20)  # عمود المجموعة الفرعية
        worksheet.set_column('D:D', 30)  # عمود مركز التكلفة
        worksheet.set_column('E:E', 15)  # عمود المصروفات
        worksheet.set_column('F:F', 15)  # عمود الإيرادات
        worksheet.set_column('G:G', 20)  # عمود التحصيل
        worksheet.set_column('H:H', 20)  # عمود المديونية
        
        # بدء كتابة البيانات
        row = 0
        
        # إضافة عنوان التقرير
        worksheet.merge_range(row, 0, row, 7, 'تقرير مراكز التكلفة', title_format)
        row += 1
        
        # إضافة معلومات الشركة والفترة الزمنية
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
            'الفرع',
            'المجموعة الرئيسية',
            'المجموعة الفرعية',
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
        if self.operating_unit_id:
            analytic_domain.append(('operating_unit_id', '=', self.operating_unit_id.id))
        if self.group_id:
            analytic_domain.append(('group_id', '=', self.group_id.id))
        if self.analytic_account_ids:
            analytic_domain.append(('id', 'in', self.analytic_account_ids.ids))
        
        analytic_accounts = self.env['account.analytic.account'].search(analytic_domain, order='operating_unit_id, group_id, name')
        
        # تجميع البيانات حسب الفرع والمجموعات
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
            # حساب القيم لكل حساب تحليلي
            expenses = self._calculate_analytic_amount(account, 'expenses')
            revenues = self._calculate_analytic_amount(account, 'revenues')
            collections = self._calculate_analytic_amount(account, 'collections')
            debts = self._calculate_analytic_amount(account, 'debts')
            
            # الحصول على الفرع
            operating_unit = account.operating_unit_id or 'بدون فرع'
            operating_unit_name = operating_unit.name if operating_unit != 'بدون فرع' else 'بدون فرع'
            
            # الحصول على المجموعة الرئيسية (المستوى الأول)
            root_group = account.group_id
            while root_group and root_group.parent_id:
                root_group = root_group.parent_id
            root_group_name = root_group.name if root_group else 'بدون مجموعة رئيسية'
            
            # الحصول على المجموعة الفرعية (المستوى الثاني)
            subgroup = account.group_id if account.group_id and account.group_id.parent_id == root_group else None
            subgroup_name = subgroup.name if subgroup else 'بدون مجموعة فرعية'
            
            # تخزين البيانات في الهيكل الهرمي
            operating_unit_dict[operating_unit_name]['groups'][root_group_name]['subgroups'][subgroup_name]['accounts'].append({
                'account': account,
                'expenses': expenses,
                'revenues': revenues,
                'collections': collections,
                'debts': debts
            })
            
            # تحديث الإجماليات
            operating_unit_dict[operating_unit_name]['groups'][root_group_name]['subgroups'][subgroup_name]['total_expenses'] += expenses
            operating_unit_dict[operating_unit_name]['groups'][root_group_name]['subgroups'][subgroup_name]['total_revenues'] += revenues
            operating_unit_dict[operating_unit_name]['groups'][root_group_name]['subgroups'][subgroup_name]['total_collections'] += collections
            operating_unit_dict[operating_unit_name]['groups'][root_group_name]['subgroups'][subgroup_name]['total_debts'] += debts
            
            operating_unit_dict[operating_unit_name]['groups'][root_group_name]['total_expenses'] += expenses
            operating_unit_dict[operating_unit_name]['groups'][root_group_name]['total_revenues'] += revenues
            operating_unit_dict[operating_unit_name]['groups'][root_group_name]['total_collections'] += collections
            operating_unit_dict[operating_unit_name]['groups'][root_group_name]['total_debts'] += debts
            
            operating_unit_dict[operating_unit_name]['total_expenses'] += expenses
            operating_unit_dict[operating_unit_name]['total_revenues'] += revenues
            operating_unit_dict[operating_unit_name]['total_collections'] += collections
            operating_unit_dict[operating_unit_name]['total_debts'] += debts

        # كتابة البيانات في Excel حسب التسلسل الهرمي
        for operating_unit_name, operating_unit_data in operating_unit_dict.items():
            # عنوان الفرع
            worksheet.write(row, 0, operating_unit_name, section_format)
            worksheet.merge_range(row, 1, row, 7, '', section_format)
            row += 1

            for root_group_name, root_group_data in operating_unit_data['groups'].items():
                # عنوان المجموعة الرئيسية
                worksheet.write(row, 1, root_group_name, section_format)
                worksheet.merge_range(row, 2, row, 7, '', section_format)
                row += 1

                for subgroup_name, subgroup_data in root_group_data['subgroups'].items():
                    # عنوان المجموعة الفرعية
                    worksheet.write(row, 2, subgroup_name, section_format)
                    worksheet.merge_range(row, 3, row, 7, '', section_format)
                    row += 1

                    # بيانات مراكز التكلفة
                    for account_data in subgroup_data['accounts']:
                        account = account_data['account']
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

                # إجمالي المجموعة الرئيسية
                worksheet.write(row, 1, f'إجمالي {root_group_name}', total_format)
                worksheet.write(row, 4, root_group_data['total_expenses'], total_format)
                worksheet.write(row, 5, root_group_data['total_revenues'], total_format)
                worksheet.write(row, 6, root_group_data['total_collections'], total_format)
                worksheet.write(row, 7, root_group_data['total_debts'], total_format)
                row += 1

            # إجمالي الفرع
            worksheet.write(row, 0, f'إجمالي {operating_unit_name}', total_format)
            worksheet.write(row, 4, operating_unit_data['total_expenses'], total_format)
            worksheet.write(row, 5, operating_unit_data['total_revenues'], total_format)
            worksheet.write(row, 6, operating_unit_data['total_collections'], total_format)
            worksheet.write(row, 7, operating_unit_data['total_debts'], total_format)
            row += 1
        
        # الإجمالي العام
        worksheet.write(row, 0, 'الإجمالي العام', total_format)
        worksheet.write(row, 4, self.total_expenses, total_format)
        worksheet.write(row, 5, self.total_revenues, total_format)
        worksheet.write(row, 6, self.total_collections, total_format)
        worksheet.write(row, 7, self.total_debts, total_format)
        
        # إغلاق الكتاب
        workbook.close()
        output.seek(0)
        
        # إنشاء المرفق وإرجاع إجراء التنزيل
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

            # إضافة معلومات الفرع
            if self.operating_unit_id:
                operating_unit_info = Paragraph(f"الفرع: {self.operating_unit_id.name}", normal_style)
                elements.append(operating_unit_info)

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

            # البحث عن جميع مراكز التكلفة المطلوبة
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
                analytic_account_ids = [a.id for a in self.analytic_account_ids if a._name == 'account.analytic.account' and a.id]
                if analytic_account_ids:
                    analytic_domain.append(('id', 'in', analytic_account_ids))

            analytic_accounts = self.env['account.analytic.account'].search(analytic_domain)

            # تجميع النتائج حسب الفرع والمجموعات
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
                # حساب المصروفات لهذا المركز
                expenses_domain = [
                    ('date', '>=', self.date_from),
                    ('date', '<=', self.date_to),
                    ('company_id', 'in', company_ids),
                    ('move_id.state', '=', 'posted'),
                    ('analytic_account_id', '=', account.id),
                    ('balance', '<', 0)
                ]
                if self.operating_unit_id:
                    expenses_domain.append(('analytic_account_id.operating_unit_id', '=', self.operating_unit_id.id))
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
                if self.operating_unit_id:
                    revenues_domain.append(('analytic_account_id.operating_unit_id', '=', self.operating_unit_id.id))
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
                if self.operating_unit_id:
                    payments_domain.append(('analytic_account_id.operating_unit_id', '=', self.operating_unit_id.id))
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
                if self.operating_unit_id:
                    invoices_domain.append(('analytic_account_id.operating_unit_id', '=', self.operating_unit_id.id))
                invoice_lines = self.env['account.move.line'].search(invoices_domain)
                account_debts = sum(line.amount_residual for line in invoice_lines)

                # الحصول على الفرع
                operating_unit = account.operating_unit_id or 'بدون فرع'
                operating_unit_name = operating_unit.name if operating_unit != 'بدون فرع' else 'بدون فرع'
                
                # الحصول على المجموعة الرئيسية (المستوى الأول)
                root_group = account.group_id
                while root_group and root_group.parent_id:
                    root_group = root_group.parent_id
                root_group_name = root_group.name if root_group else 'بدون مجموعة رئيسية'
                
                # الحصول على المجموعة الفرعية (المستوى الثاني)
                subgroup = account.group_id if account.group_id and account.group_id.parent_id == root_group else None
                subgroup_name = subgroup.name if subgroup else 'بدون مجموعة فرعية'

                # تخزين النتائج
                operating_unit_dict[operating_unit_name]['groups'][root_group_name]['subgroups'][subgroup_name]['accounts'].append({
                    'account': account,
                    'expenses': account_expenses,
                    'revenues': account_revenues,
                    'collections': account_collections,
                    'debts': account_debts
                })

                # تحديث إجماليات المجموعة
                operating_unit_dict[operating_unit_name]['groups'][root_group_name]['subgroups'][subgroup_name]['total_expenses'] += account_expenses
                operating_unit_dict[operating_unit_name]['groups'][root_group_name]['subgroups'][subgroup_name]['total_revenues'] += account_revenues
                operating_unit_dict[operating_unit_name]['groups'][root_group_name]['subgroups'][subgroup_name]['total_collections'] += account_collections
                operating_unit_dict[operating_unit_name]['groups'][root_group_name]['subgroups'][subgroup_name]['total_debts'] += account_debts
                
                operating_unit_dict[operating_unit_name]['groups'][root_group_name]['total_expenses'] += account_expenses
                operating_unit_dict[operating_unit_name]['groups'][root_group_name]['total_revenues'] += account_revenues
                operating_unit_dict[operating_unit_name]['groups'][root_group_name]['total_collections'] += account_collections
                operating_unit_dict[operating_unit_name]['groups'][root_group_name]['total_debts'] += account_debts
                
                operating_unit_dict[operating_unit_name]['total_expenses'] += account_expenses
                operating_unit_dict[operating_unit_name]['total_revenues'] += account_revenues
                operating_unit_dict[operating_unit_name]['total_collections'] += account_collections
                operating_unit_dict[operating_unit_name]['total_debts'] += account_debts

            # عرض النتائج حسب التسلسل الهرمي
            for operating_unit_name, operating_unit_data in operating_unit_dict.items():
                # عنوان الفرع
                report_data.append([
                    operating_unit_name, '', '', '', '', '', '', ''
                ])

                for root_group_name, root_group_data in operating_unit_data['groups'].items():
                    # عنوان المجموعة الرئيسية
                    report_data.append([
                        '', root_group_name, '', '', '', '', '', ''
                    ])

                    for subgroup_name, subgroup_data in root_group_data['subgroups'].items():
                        # عنوان المجموعة الفرعية
                        report_data.append([
                            '', '', subgroup_name, '', '', '', '', ''
                        ])

                        # تفاصيل مراكز التكلفة في هذه المجموعة
                        for account_data in subgroup_data['accounts']:
                            account = account_data['account']
                            report_data.append([
                                '', '', '', account.name,
                                format(round(account_data['expenses'], 2), ',.2f'),
                                format(round(account_data['revenues'], 2), ',.2f'),
                                format(round(account_data['collections'], 2), ',.2f'),
                                format(round(account_data['debts'], 2), ',.2f')
                            ])

                        # إجمالي المجموعة الفرعية
                        report_data.append([
                            '', '', f'إجمالي {subgroup_name}', '',
                            format(round(subgroup_data['total_expenses'], 2), ',.2f'),
                            format(round(subgroup_data['total_revenues'], 2), ',.2f'),
                            format(round(subgroup_data['total_collections'], 2), ',.2f'),
                            format(round(subgroup_data['total_debts'], 2), ',.2f')
                        ])

                    # إجمالي المجموعة الرئيسية
                    report_data.append([
                        '', f'إجمالي {root_group_name}', '', '',
                        format(round(root_group_data['total_expenses'], 2), ',.2f'),
                        format(round(root_group_data['total_revenues'], 2), ',.2f'),
                        format(round(root_group_data['total_collections'], 2), ',.2f'),
                        format(round(root_group_data['total_debts'], 2), ',.2f')
                    ])

                # إجمالي الفرع
                report_data.append([
                    f'إجمالي {operating_unit_name}', '', '', '',
                    format(round(operating_unit_data['total_expenses'], 2), ',.2f'),
                    format(round(operating_unit_data['total_revenues'], 2), ',.2f'),
                    format(round(operating_unit_data['total_collections'], 2), ',.2f'),
                    format(round(operating_unit_data['total_debts'], 2), ',.2f')
                ])

            # الإجمالي العام
            report_data.append([
                'الإجمالي العام', '', '', '',
                format(round(self.total_expenses, 2), ',.2f'),
                format(round(self.total_revenues, 2), ',.2f'),
                format(round(self.total_collections, 2), ',.2f'),
                format(round(self.total_debts, 2), ',.2f')
            ])

            # إنشاء جدول التقرير
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
            analytic_account_ids = [a.id for a in self.analytic_account_ids if a._name == 'account.analytic.account' and a.id]
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
            
        # البحث عن المجموعات التي تحتوي على مراكز تكلفة في هذا الفرع
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

    def debug_data(self):
        """دالة للتشخيص وفحص البيانات"""
        self.ensure_one()
        
        logger.info("=== تشخيص البيانات ===")
        logger.info(f"الفترة: من {self.date_from} إلى {self.date_to}")
        logger.info(f"الشركات: {[c.name for c in self.company_ids]}")
        logger.info(f"الفرع: {self.operating_unit_id.name if self.operating_unit_id else 'غير محدد'}")
        logger.info(f"مراكز التكلفة: {len(self.analytic_account_ids)}")
        
        # فحص وجود قيود يومية
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

    def check_analytic_accounts_availability(self):
        """دالة للتحقق من توفر مراكز التكلفة"""
        self.ensure_one()
        
        logger.info("=== فحص توفر مراكز التكلفة ===")
        
        # فحص إجمالي مراكز التكلفة
        all_accounts = self.env['account.analytic.account'].search([])
        active_accounts = self.env['account.analytic.account'].search([('active', '=', True)])
        
        logger.info(f"إجمالي مراكز التكلفة: {len(all_accounts)}")
        logger.info(f"مراكز التكلفة النشطة: {len(active_accounts)}")
        
        # فحص حسب الشركة
        if self.company_ids:
            for company in self.company_ids:
                company_accounts = self.env['account.analytic.account'].search([
                    ('active', '=', True),
                    ('company_id', '=', company.id)
                ])
                logger.info(f"مراكز التكلفة للشركة {company.name}: {len(company_accounts)}")
        
        # فحص حسب الفرع
        if self.operating_unit_id:
            unit_accounts = self.env['account.analytic.account'].search([
                ('active', '=', True),
                ('operating_unit_id', '=', self.operating_unit_id.id)
            ])
            logger.info(f"مراكز التكلفة للفرع {self.operating_unit_id.name}: {len(unit_accounts)}")
        
        # فحص حسب المجموعة
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
