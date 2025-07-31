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
    _rec_name = 'display_name'
    _order = 'date_from desc'
    
    display_name = fields.Char(string='Name', compute='_compute_display_name', store=True)
    
    @api.depends('group_id', 'date_from', 'date_to', 'company_ids')
    def _compute_display_name(self):
        for record in self:
            try:
                name_parts = []
                if record.group_id and hasattr(record.group_id, 'name') and record.group_id.name:
                    name_parts.append(record.group_id.name)
                else:
                    name_parts.append('تقرير مراكز التكلفة')
                
                if record.date_from and record.date_to:
                    name_parts.append(f"({record.date_from} - {record.date_to})")
                
                record.display_name = ' '.join(name_parts)
            except Exception as e:
                logger.error("Error computing display name: %s", str(e))
                record.display_name = f'تقرير مراكز التكلفة - {record.id or "جديد"}'

    # الحقول الأساسية
    date_from = fields.Date(string='من تاريخ', default=fields.Date.today(), required=True)
    date_to = fields.Date(string='إلى تاريخ', default=fields.Date.today(), required=True)
    company_ids = fields.Many2many('res.company', string='الشركات', default=lambda self: self.env.company)
    company_id = fields.Many2one('res.company', string='Company', default=lambda self: self.env.company)

    # حقول العلاقات
    branch_id = fields.Many2one(
        'res.branch',
        string='الفرع'
    )

    group_id = fields.Many2one(
        'account.analytic.group',
        string='مجموعة مراكز التكلفة'
    )

    analytic_account_id = fields.Many2one(
        'account.analytic.account',
        string='مركز التكلفة'
    )
    company_currency_id = fields.Many2one(
        'res.currency', string='العملة',
        compute='_compute_company_currency', store=True
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
        string='إجمالي التحصيل',
        currency_field='company_currency_id',
        compute='_compute_totals'
    )
    total_debts = fields.Monetary(
        string='إجمالي المديونية',
        currency_field='company_currency_id',
        compute='_compute_totals'
    )
    report_lines = fields.Html(
        string='تفاصيل التقرير',
        compute='_compute_report_lines',
        sanitize=False
    )
    analytic_account_ids = fields.Many2many('account.analytic.account', string='Analytic Accounts', compute='_compute_analytic_accounts')

    @api.depends('company_ids')
    def _compute_company_currency(self):
        for record in self:
            try:
                if record.company_ids and len(record.company_ids) == 1 and record.company_ids[0].currency_id:
                    record.company_currency_id = record.company_ids[0].currency_id
                else:
                    # Fallback to environment company currency or base currency
                    record.company_currency_id = self.env.company.currency_id or self.env.ref('base.USD')
            except Exception as e:
                logger.error("Error computing company currency: %s", str(e))
                # Fallback to base currency if all else fails
                try:
                    record.company_currency_id = self.env.ref('base.USD')
                except:
                    record.company_currency_id = self.env['res.currency'].search([('name', '=', 'USD')], limit=1)

    @api.depends('group_id', 'analytic_account_id', 'company_ids', 'branch_id')
    def _compute_analytic_accounts(self):
        for record in self:
            # Always initialize with empty recordset
            record.analytic_account_ids = self.env['account.analytic.account']
            
            try:
                domain = []
                
                # Add company filter if available
                if record.company_ids and record.company_ids.ids:
                    # Check if analytic account has company_id field
                    account_model = self.env['account.analytic.account']
                    if hasattr(account_model, '_fields') and 'company_id' in account_model._fields:
                        domain.append(('company_id', 'in', record.company_ids.ids))

                # Add branch filter if available and the field exists
                if record.branch_id and hasattr(record.branch_id, 'id') and record.branch_id.id:
                    account_model = self.env['account.analytic.account']
                    if hasattr(account_model, '_fields') and 'branch_id' in account_model._fields:
                        domain.append(('branch_id', '=', record.branch_id.id))
                        
                # Add group filter if available
                if record.group_id and hasattr(record.group_id, 'id') and record.group_id.id:
                    domain.append(('group_id', '=', record.group_id.id))
                    
                # Add specific account filter if available
                if record.analytic_account_id and hasattr(record.analytic_account_id, 'id') and record.analytic_account_id.id:
                    domain.append(('id', '=', record.analytic_account_id.id))

                # Search for analytic accounts with the domain
                if domain:
                    analytic_accounts = self.env['account.analytic.account'].search(domain)
                    record.analytic_account_ids = analytic_accounts
                    
            except Exception as e:
                logger.error("Error computing analytic accounts: %s", str(e))
                # Ensure we always have a valid recordset
                record.analytic_account_ids = self.env['account.analytic.account']

    @api.depends('date_from', 'date_to', 'company_ids', 'analytic_account_ids', 'branch_id')
    def _compute_totals(self):
        for record in self:
            # Initialize all fields with default values
            record.total_expenses = 0.0
            record.total_revenues = 0.0
            record.total_collections = 0.0
            record.total_debts = 0.0
            
            try:
                # Skip computation if essential data is missing
                if not record.company_ids or not record.analytic_account_ids:
                    continue

                # حساب المصروفات (حركات ذات رصيد مدين)
                expenses_domain = [
                    ('date', '>=', record.date_from),
                    ('date', '<=', record.date_to),
                    ('company_id', 'in', record.company_ids.ids),
                    ('move_id.state', '=', 'posted'),
                    ('analytic_account_id', 'in', record.analytic_account_ids.ids),
                    ('balance', '<', 0)
                ]
                # Add branch filter only if the field exists on account.move.line
                if record.branch_id:
                    move_line_model = self.env['account.move.line']
                    if hasattr(move_line_model, '_fields') and 'branch_id' in move_line_model._fields:
                        expenses_domain.append(('branch_id', '=', record.branch_id.id))

                expense_lines = self.env['account.move.line'].search(expenses_domain)
                record.total_expenses = abs(sum(line.balance for line in expense_lines))

                # حساب الإيرادات (حركات ذات رصيد دائن)
                revenues_domain = [
                    ('date', '>=', record.date_from),
                    ('date', '<=', record.date_to),
                    ('company_id', 'in', record.company_ids.ids),
                    ('move_id.state', '=', 'posted'),
                    ('analytic_account_id', 'in', record.analytic_account_ids.ids),
                    ('balance', '>', 0)
                ]
                if record.branch_id:
                    move_line_model = self.env['account.move.line']
                    if hasattr(move_line_model, '_fields') and 'branch_id' in move_line_model._fields:
                        revenues_domain.append(('branch_id', '=', record.branch_id.id))

                revenue_lines = self.env['account.move.line'].search(revenues_domain)
                record.total_revenues = sum(line.balance for line in revenue_lines)

                # حساب التحصيل (مدفوعات مرتبطة بمراكز التكلفة)
                payments_domain = [
                    ('date', '>=', record.date_from),
                    ('date', '<=', record.date_to),
                    ('company_id', 'in', record.company_ids.ids),
                    ('move_id.state', '=', 'posted'),
                    ('analytic_account_id', 'in', record.analytic_account_ids.ids),
                    ('payment_id', '!=', False)
                ]
                if record.branch_id:
                    move_line_model = self.env['account.move.line']
                    if hasattr(move_line_model, '_fields') and 'branch_id' in move_line_model._fields:
                        payments_domain.append(('branch_id', '=', record.branch_id.id))

                payment_lines = self.env['account.move.line'].search(payments_domain)
                record.total_collections = abs(sum(line.balance for line in payment_lines))

                # حساب المديونية (فواتير غير مدفوعة مرتبطة بمراكز التكلفة)
                invoices_domain = [
                    ('date', '>=', record.date_from),
                    ('date', '<=', record.date_to),
                    ('company_id', 'in', record.company_ids.ids),
                    ('move_id.state', '=', 'posted'),
                    ('analytic_account_id', 'in', record.analytic_account_ids.ids),
                    ('move_id.move_type', 'in', ['out_invoice', 'in_invoice']),
                    ('move_id.payment_state', '!=', 'paid')
                ]
                if record.branch_id:
                    move_line_model = self.env['account.move.line']
                    if hasattr(move_line_model, '_fields') and 'branch_id' in move_line_model._fields:
                        invoices_domain.append(('branch_id', '=', record.branch_id.id))

                invoice_lines = self.env['account.move.line'].search(invoices_domain)
                record.total_debts = abs(sum(line.amount_residual for line in invoice_lines))
            
            except Exception as e:
                logger.error("Error computing totals: %s", str(e))
                record.total_expenses = 0.0
                record.total_revenues = 0.0
                record.total_collections = 0.0
                record.total_debts = 0.0

    @api.depends('date_from', 'date_to', 'company_ids', 'analytic_account_ids', 'branch_id')
    def _compute_report_lines(self):
        for record in self:
            # Initialize with empty report
            record.report_lines = "<p>لا توجد بيانات لعرضها</p>"
            
            try:
                if not record.company_ids or not record.analytic_account_ids:
                    continue
                    
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
                                <th>التحصيل</th>
                                <th>المديونية</th>
                            </tr>
                        </thead>
                        <tbody>
                """)

                # تجميع النتائج حسب المجموعة ومركز التكلفة
                group_dict = defaultdict(lambda: {
                    'accounts': [],
                    'total_expenses': 0.0,
                    'total_revenues': 0.0,
                    'total_collections': 0.0,
                    'total_debts': 0.0
                })

                for account in record.analytic_account_ids:
                    # حساب المصروفات لهذا المركز
                    expenses_domain = [
                        ('date', '>=', record.date_from),
                        ('date', '<=', record.date_to),
                        ('company_id', 'in', record.company_ids.ids),
                        ('move_id.state', '=', 'posted'),
                        ('analytic_account_id', '=', account.id),
                        ('balance', '<', 0)
                    ]
                    if record.branch_id:
                        expenses_domain.append(('branch_id', '=', record.branch_id.id))
                    expense_lines = self.env['account.move.line'].search(expenses_domain)
                    account_expenses = abs(sum(line.balance for line in expense_lines))

                    # حساب الإيرادات لهذا المركز
                    revenues_domain = [
                        ('date', '>=', record.date_from),
                        ('date', '<=', record.date_to),
                        ('company_id', 'in', record.company_ids.ids),
                        ('move_id.state', '=', 'posted'),
                        ('analytic_account_id', '=', account.id),
                        ('balance', '>', 0)
                    ]
                    if record.branch_id:
                        revenues_domain.append(('branch_id', '=', record.branch_id.id))
                    revenue_lines = self.env['account.move.line'].search(revenues_domain)
                    account_revenues = sum(line.balance for line in revenue_lines)

                    # حساب التحصيل لهذا المركز
                    payments_domain = [
                        ('date', '>=', record.date_from),
                        ('date', '<=', record.date_to),
                        ('company_id', 'in', record.company_ids.ids),
                        ('move_id.state', '=', 'posted'),
                        ('analytic_account_id', '=', account.id),
                        ('payment_id', '!=', False)
                    ]
                    if record.branch_id:
                        payments_domain.append(('branch_id', '=', record.branch_id.id))
                    payment_lines = self.env['account.move.line'].search(payments_domain)
                    account_collections = abs(sum(line.balance for line in payment_lines))

                    # حساب المديونية لهذا المركز
                    invoices_domain = [
                        ('date', '>=', record.date_from),
                        ('date', '<=', record.date_to),
                        ('company_id', 'in', record.company_ids.ids),
                        ('move_id.state', '=', 'posted'),
                        ('analytic_account_id', '=', account.id),
                        ('move_id.move_type', 'in', ['out_invoice', 'in_invoice']),
                        ('move_id.payment_state', '!=', 'paid')
                    ]
                    if record.branch_id:
                        invoices_domain.append(('branch_id', '=', record.branch_id.id))
                    invoice_lines = self.env['account.move.line'].search(invoices_domain)
                    account_debts = abs(sum(line.amount_residual for line in invoice_lines))

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
                    if not group:
                        continue

                    # عنوان المجموعة
                    html_lines.append(f"""
                        <tr class="section-row">
                            <td colspan="7">{group.name}</td>
                        </tr>
                    """)

                    # تفاصيل مراكز التكلفة في هذه المجموعة
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

                    # إجمالي المجموعة
                    html_lines.append(f"""
                        <tr class="total-row">
                            <td colspan="3">إجمالي المجموعة</td>
                            <td class="text-right">{format(data['total_expenses'], '.2f')}</td>
                            <td class="text-right">{format(data['total_revenues'], '.2f')}</td>
                            <td class="text-right">{format(data['total_collections'], '.2f')}</td>
                            <td class="text-right">{format(data['total_debts'], '.2f')}</td>
                        </tr>
                    """)

                # إجمالي عام
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
                record.report_lines = f"<p>حدث خطأ في إنشاء التقرير: {str(e)}</p>"

    @api.onchange('company_ids')
    def _onchange_company_ids(self):
        try:
            if not self.company_ids:
                return

            company_ids = self.company_ids.ids if self.company_ids else []

            # Reset dependent fields if they don't belong to selected companies
            if self.branch_id and hasattr(self.branch_id, 'company_id') and self.branch_id.company_id:
                if self.branch_id.company_id.id not in company_ids:
                    self.branch_id = False

            if self.group_id and hasattr(self.group_id, 'company_id') and self.group_id.company_id:
                if self.group_id.company_id.id not in company_ids:
                    self.group_id = False

            if self.analytic_account_id and hasattr(self.analytic_account_id, 'company_id') and self.analytic_account_id.company_id:
                if self.analytic_account_id.company_id.id not in company_ids:
                    self.analytic_account_id = False

        except Exception as e:
            logger.error("Error in _onchange_company_ids: %s", str(e))

    @api.onchange('group_id')
    def _onchange_group_id(self):
        try:
            # Reset analytic account if it doesn't belong to the selected group
            if self.group_id and self.analytic_account_id and hasattr(self.analytic_account_id, 'group_id'):
                if self.analytic_account_id.group_id != self.group_id:
                    self.analytic_account_id = False
        except Exception as e:
            logger.error("Error in _onchange_group_id: %s", str(e))

    @api.constrains('company_ids', 'branch_id', 'group_id', 'analytic_account_id')
    def _check_company_consistency(self):
        for record in self:
            if not record.company_ids:
                continue

            company_ids = record.company_ids.ids
            # Check branch only if it has company_id field
            if record.branch_id and hasattr(record.branch_id, 'company_id') and record.branch_id.company_id:
                if record.branch_id.company_id.id not in company_ids:
                    raise ValidationError("الفرع المحدد لا ينتمي لأي من الشركات المحددة")
            # Check group only if it has company_id field
            if record.group_id and hasattr(record.group_id, 'company_id') and record.group_id.company_id:
                if record.group_id.company_id.id not in company_ids:
                    raise ValidationError("المجموعة المحددة لا تنتمي لأي من الشركات المحددة")
            # Check analytic account only if it has company_id field
            if record.analytic_account_id and hasattr(record.analytic_account_id, 'company_id') and record.analytic_account_id.company_id:
                if record.analytic_account_id.company_id.id not in company_ids:
                    raise ValidationError("مركز التكلفة المحدد لا ينتمي لأي من الشركات المحددة")

    @api.onchange('analytic_account_id')
    def _onchange_analytic_account_id(self):
        # Trigger recomputation of related fields
        pass

    @api.onchange('branch_id')
    def _onchange_branch_id(self):
        # Trigger recomputation of related fields
        pass

    @api.onchange('date_from')
    def _onchange_date_from(self):
        if self.date_from and not self.date_to:
            self.date_to = self.date_from

    @api.model
    def _get_branch_domain(self, company_ids):
        """Get domain for branch field based on companies"""
        if not company_ids:
            return []
        
        # Check if res.branch model has company_id field
        branch_model = self.env['res.branch']
        if hasattr(branch_model, '_fields') and 'company_id' in branch_model._fields:
            return [('company_id', 'in', company_ids)]
        return []

    @api.model
    def _get_group_domain(self, company_ids):
        """Get domain for analytic group field based on companies"""
        if not company_ids:
            return []
        
        # Check if account.analytic.group model has company_id field
        group_model = self.env['account.analytic.group']
        if hasattr(group_model, '_fields') and 'company_id' in group_model._fields:
            return [('company_id', 'in', company_ids)]
        return []

    @api.model
    def _get_analytic_account_domain(self, company_ids, group_id=None):
        """Get domain for analytic account field based on companies and group"""
        domain = []
        if company_ids:
            # Check if account.analytic.account model has company_id field
            account_model = self.env['account.analytic.account']
            if hasattr(account_model, '_fields') and 'company_id' in account_model._fields:
                domain.append(('company_id', 'in', company_ids))
        
        if group_id:
            domain.append(('group_id', '=', group_id))
        
        return domain

    @api.constrains('date_from', 'date_to')
    def _check_dates(self):
        for record in self:
            if record.date_from and record.date_to and record.date_from > record.date_to:
                raise ValidationError("تاريخ البداية يجب أن يكون قبل تاريخ النهاية")

    @api.model
    def create(self, vals):
        """Override create to ensure proper initialization"""
        # Ensure default company if not set
        if not vals.get('company_ids') and not vals.get('company_id'):
            vals['company_ids'] = [(6, 0, [self.env.company.id])]
        
        return super(AnalyticAccountReport, self).create(vals)

    def write(self, vals):
        """Override write to prevent invalid field values"""
        try:
            return super(AnalyticAccountReport, self).write(vals)
        except Exception as e:
            logger.error("Error writing analytic account report: %s", str(e))
            # Remove problematic fields and try again
            safe_vals = vals.copy()
            for field in ['branch_id', 'group_id', 'analytic_account_id']:
                if field in safe_vals and not safe_vals[field]:
                    safe_vals[field] = False
            return super(AnalyticAccountReport, self).write(safe_vals)

    def generate_excel_report(self):
        """إنشاء تقرير Excel لتقرير مراكز التكلفة"""
        self.ensure_one()
        # إنشاء كتاب Excel
        output = io.BytesIO()
        workbook = xlsxwriter.Workbook(output, {'in_memory': True, 'right_to_left': True})
        worksheet = workbook.add_worksheet('تقرير مراكز التكلفة')
        worksheet.right_to_left()

        # تنسيقات الخلايا
        title_format = workbook.add_format({
            'bold': True, 'align': 'center', 'valign': 'vcenter',
            'font_size': 16, 'font_color': '#4472C4'
        })
        header_format = workbook.add_format({
            'bold': True, 'align': 'center', 'valign': 'vcenter',
            'bg_color': '#4472C4', 'font_color': 'white', 'border': 1,
            'font_size': 12, 'text_wrap': True
        })
        currency_format = workbook.add_format({
            'num_format': '#,##0.00', 'border': 1, 'align': 'right'
        })
        text_format = workbook.add_format({'border': 1, 'align': 'right'})
        total_format = workbook.add_format({
            'bold': True, 'num_format': '#,##0.00', 'border': 1,
            'align': 'right', 'bg_color': '#D9E1F2'
        })
        label_format = workbook.add_format({
            'bold': True, 'align': 'right', 'border': 1
        })
        section_format = workbook.add_format({
            'bold': True, 'align': 'right', 'border': 1,
            'bg_color': '#E6F2FF'
        })

        # إضافة شعار الشركة
        row = 0
        if len(self.company_ids) == 1 and self.company_ids[0].logo:
            try:
                image_data = io.BytesIO(base64.b64decode(self.company_ids[0].logo))
                worksheet.merge_range(row, 4, row + 1, 4, '')
                worksheet.insert_image(row, 4, 'logo.png', {
                    'image_data': image_data,
                    'x_scale': 0.15,
                    'y_scale': 0.15,
                    'x_offset': 10,
                    'y_offset': 10,
                    'object_position': 3,
                    'positioning': 1
                })
                worksheet.set_row(row, 80)
                row += 1
                worksheet.set_row(row, 15)
                row += 1
            except Exception as e:
                logger.error(f"Failed to insert company logo: {str(e)}")
                pass

        # إضافة عنوان التقرير
        worksheet.merge_range(row, 0, row, 6, 'تقرير مراكز التكلفة', title_format)
        row += 1

        # إضافة معلومات الشركات المختارة
        if self.company_ids:
            companies = ", ".join(self.company_ids.mapped('name'))
            worksheet.merge_range(row, 0, row, 6, f'الشركات: {companies}',
                                  workbook.add_format({'align': 'center', 'font_size': 12}))
            row += 1

        # إضافة معلومات الفرع إن وجد
        if self.branch_id:
            worksheet.merge_range(row, 0, row, 6, f'الفرع: {self.branch_id.name}',
                                  workbook.add_format({'align': 'center', 'font_size': 12}))
            row += 1

        if self.group_id:
            worksheet.merge_range(row, 0, row, 6, f'المجموعة: {self.group_id.name}',
                                  workbook.add_format({'align': 'center', 'font_size': 12}))
            row += 1
        worksheet.merge_range(row, 0, row, 6, f'من {self.date_from} إلى {self.date_to}',
                              workbook.add_format({'align': 'center', 'font_size': 12}))
        row += 2

        # إضافة ملخص التقرير
        worksheet.write(row, 0, 'إجمالي المصروفات', label_format)
        worksheet.write(row, 1, round(self.total_expenses, 2), currency_format)
        row += 1

        worksheet.write(row, 0, 'إجمالي الإيرادات', label_format)
        worksheet.write(row, 1, round(self.total_revenues, 2), currency_format)
        row += 1

        worksheet.write(row, 0, 'إجمالي التحصيل', label_format)
        worksheet.write(row, 1, round(self.total_collections, 2), currency_format)
        row += 1

        worksheet.write(row, 0, 'إجمالي المديونية', label_format)
        worksheet.write(row, 1, round(self.total_debts, 2), currency_format)
        row += 2

        # إنشاء صف العناوين
        headers = [
            'المجموعة',
            'مركز التكلفة',
            'الشريك',
            'المصروفات',
            'الإيرادات',
            'التحصيل',
            'المديونية'
        ]

        for col, header in enumerate(headers):
            worksheet.write(row, col, header, header_format)
        row += 1

        # البحث عن جميع مراكز التكلفة المطلوبة
        analytic_domain = [('company_id', 'in', self.company_ids.ids)]
        if self.branch_id:
            analytic_domain.append(('branch_id', '=', self.branch_id.id))
        if self.group_id:
            analytic_domain.append(('group_id', '=', self.group_id.id))
        if self.analytic_account_ids:
            analytic_domain.append(('id', 'in', self.analytic_account_ids.ids))

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
                ('company_id', 'in', self.company_ids.ids),
                ('move_id.state', '=', 'posted'),
                ('analytic_account_id', '=', account.id),
                ('balance', '<', 0)
            ]
            if self.branch_id:
                expenses_domain.append(('branch_id', '=', self.branch_id.id))
            expense_lines = self.env['account.move.line'].search(expenses_domain)
            account_expenses = abs(sum(line.balance for line in expense_lines))

            # حساب الإيرادات لهذا المركز
            revenues_domain = [
                ('date', '>=', self.date_from),
                ('date', '<=', self.date_to),
                ('company_id', 'in', self.company_ids.ids),
                ('move_id.state', '=', 'posted'),
                ('analytic_account_id', '=', account.id),
                ('balance', '>', 0)
            ]
            if self.branch_id:
                revenues_domain.append(('branch_id', '=', self.branch_id.id))
            revenue_lines = self.env['account.move.line'].search(revenues_domain)
            account_revenues = sum(line.balance for line in revenue_lines)

            # حساب التحصيل لهذا المركز
            payments_domain = [
                ('date', '>=', self.date_from),
                ('date', '<=', self.date_to),
                ('company_id', 'in', self.company_ids.ids),
                ('move_id.state', '=', 'posted'),
                ('analytic_account_id', '=', account.id),
                ('payment_id', '!=', False)
            ]
            if self.branch_id:
                payments_domain.append(('branch_id', '=', self.branch_id.id))
            payment_lines = self.env['account.move.line'].search(payments_domain)
            account_collections = abs(sum(line.balance for line in payment_lines))

            # حساب المديونية لهذا المركز
            invoices_domain = [
                ('date', '>=', self.date_from),
                ('date', '<=', self.date_to),
                ('company_id', 'in', self.company_ids.ids),
                ('move_id.state', '=', 'posted'),
                ('analytic_account_id', '=', account.id),
                ('move_id.move_type', 'in', ['out_invoice', 'in_invoice']),
                ('move_id.payment_state', '!=', 'paid')
            ]
            if self.branch_id:
                invoices_domain.append(('branch_id', '=', self.branch_id.id))
            invoice_lines = self.env['account.move.line'].search(invoices_domain)
            account_debts = abs(sum(line.amount_residual for line in invoice_lines))

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
            worksheet.write(row, 0, group.name if group else 'بدون مجموعة', section_format)
            worksheet.merge_range(row, 1, row, 6, '', section_format)
            row += 1

            # تفاصيل مراكز التكلفة في هذه المجموعة
            for account_data in data['accounts']:
                account = account_data['account']
                partner_name = account_data['partner'].name if account_data['partner'] else ''
                worksheet.write(row, 0, '', text_format)
                worksheet.write(row, 1, account.name, text_format)
                worksheet.write(row, 2, partner_name, text_format)
                worksheet.write(row, 3, round(account_data['expenses'], 2), currency_format)
                worksheet.write(row, 4, round(account_data['revenues'], 2), currency_format)
                worksheet.write(row, 5, round(account_data['collections'], 2), currency_format)
                worksheet.write(row, 6, round(account_data['debts'], 2), currency_format)
                row += 1

            # إجمالي المجموعة
            worksheet.write(row, 0, '', total_format)
            worksheet.write(row, 1, 'إجمالي المجموعة', total_format)
            worksheet.write(row, 2, '', total_format)
            worksheet.write(row, 3, round(data['total_expenses'], 2), total_format)
            worksheet.write(row, 4, round(data['total_revenues'], 2), total_format)
            worksheet.write(row, 5, round(data['total_collections'], 2), total_format)
            worksheet.write(row, 6, round(data['total_debts'], 2), total_format)
            row += 1

        # إجمالي عام
        worksheet.write(row, 0, '', total_format)
        worksheet.write(row, 1, 'الإجمالي العام', total_format)
        worksheet.write(row, 2, '', total_format)
        worksheet.write(row, 3, round(self.total_expenses, 2), total_format)
        worksheet.write(row, 4, round(self.total_revenues, 2), total_format)
        worksheet.write(row, 5, round(self.total_collections, 2), total_format)
        worksheet.write(row, 6, round(self.total_debts, 2), total_format)
        row += 1

        # ضبط عرض الأعمدة
        worksheet.set_column(0, 0, 25)  # المجموعة
        worksheet.set_column(1, 1, 30)  # مركز التكلفة
        worksheet.set_column(2, 2, 25)  # الشريك
        worksheet.set_column(3, 6, 15)  # الأرقام

        # إغلاق الكتاب وحفظه
        workbook.close()
        output.seek(0)

        return {
            'file_name': f"تقرير_مراكز_التكلفة_{self.date_from}_إلى_{self.date_to}.xlsx",
            'file_content': output.read(),
            'file_type': 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
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

            # إضافة معلومات الفرع إن وجد
            if self.branch_id:
                branch_info = Paragraph(f"الفرع: {self.branch_id.name}", normal_style)
                elements.append(branch_info)

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
                ['إجمالي التحصيل', format(round(self.total_collections, 2), ',.2f')],
                ['إجمالي المديونية', format(round(self.total_debts, 2), ',.2f')]
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
                'التحصيل',
                'المديونية'
            ]

            report_data = [report_header]

            # البحث عن جميع مراكز التكلفة المطلوبة
            analytic_domain = [('company_id', 'in', self.company_ids.ids)]
            if self.branch_id:
                analytic_domain.append(('branch_id', '=', self.branch_id.id))
            if self.group_id:
                analytic_domain.append(('group_id', '=', self.group_id.id))
            if self.analytic_account_ids:
                analytic_domain.append(('id', 'in', self.analytic_account_ids.ids))

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
                    ('company_id', 'in', self.company_ids.ids),
                    ('move_id.state', '=', 'posted'),
                    ('analytic_account_id', '=', account.id),
                    ('balance', '<', 0)
                ]
                if self.branch_id:
                    expenses_domain.append(('branch_id', '=', self.branch_id.id))
                expense_lines = self.env['account.move.line'].search(expenses_domain)
                account_expenses = abs(sum(line.balance for line in expense_lines))

                # حساب الإيرادات لهذا المركز
                revenues_domain = [
                    ('date', '>=', self.date_from),
                    ('date', '<=', self.date_to),
                    ('company_id', 'in', self.company_ids.ids),
                    ('move_id.state', '=', 'posted'),
                    ('analytic_account_id', '=', account.id),
                    ('balance', '>', 0)
                ]
                if self.branch_id:
                    revenues_domain.append(('branch_id', '=', self.branch_id.id))
                revenue_lines = self.env['account.move.line'].search(revenues_domain)
                account_revenues = sum(line.balance for line in revenue_lines)

                # حساب التحصيل لهذا المركز
                payments_domain = [
                    ('date', '>=', self.date_from),
                    ('date', '<=', self.date_to),
                    ('company_id', 'in', self.company_ids.ids),
                    ('move_id.state', '=', 'posted'),
                    ('analytic_account_id', '=', account.id),
                    ('payment_id', '!=', False)
                ]
                if self.branch_id:
                    payments_domain.append(('branch_id', '=', self.branch_id.id))
                payment_lines = self.env['account.move.line'].search(payments_domain)
                account_collections = abs(sum(line.balance for line in payment_lines))

                # حساب المديونية لهذا المركز
                invoices_domain = [
                    ('date', '>=', self.date_from),
                    ('date', '<=', self.date_to),
                    ('company_id', 'in', self.company_ids.ids),
                    ('move_id.state', '=', 'posted'),
                    ('analytic_account_id', '=', account.id),
                    ('move_id.move_type', 'in', ['out_invoice', 'in_invoice']),
                    ('move_id.payment_state', '!=', 'paid')
                ]
                if self.branch_id:
                    invoices_domain.append(('branch_id', '=', self.branch_id.id))
                invoice_lines = self.env['account.move.line'].search(invoices_domain)
                account_debts = abs(sum(line.amount_residual for line in invoice_lines))

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
        """إجراء لإنشاء وتنزيل التقرير"""
        self.ensure_one()
        try:
            report_data = self.generate_excel_report()

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
            logger.error("Failed to generate account statement report: %s", str(e))
            raise

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
        domain = [
            ('date', '>=', self.date_from),
            ('date', '<=', self.date_to),
            ('company_id', 'in', self.company_ids.ids),
            ('account_id', '!=', False)
        ]
        if self.branch_id:
            domain.append(('branch_id', '=', self.branch_id.id))
        if self.group_id:
            domain.append(('account_id.group_id', '=', self.group_id.id))
        if self.analytic_account_ids:
            domain.append(('account_id', 'in', self.analytic_account_ids.ids))
        action['domain'] = domain
        action['context'] = {
            'search_default_group_by_account': 1,
            'create': False
        }
        return action
