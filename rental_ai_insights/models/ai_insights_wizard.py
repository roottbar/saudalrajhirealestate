# -*- coding: utf-8 -*-

from odoo import models, fields, api
from .ai_utils import group_by_year, group_by_month, simple_linear_forecast


class RentalAIInsightsWizard(models.TransientModel):
    _name = 'rental.ai.insights.wizard'
    _description = 'Rental AI Insights Wizard'

    company_id = fields.Many2one('res.company', string='الشركة', default=lambda self: self.env.company)
    branch_id = fields.Many2one('res.branch', string='الفرع')
    property_id = fields.Many2one('rent.property', string='العقار')
    analytic_account_id = fields.Many2one('account.analytic.account', string='الحساب التحليلي')
    partner_id = fields.Many2one('res.partner', string='اسم العميل')
    contract_number = fields.Char(string='رقم العقد')
    date_from = fields.Date(string='تاريخ الاستلام')
    date_to = fields.Date(string='تاريخ التسليم')

    amount_paid = fields.Monetary(string='المبلغ المدفوع', currency_field='currency_id', compute='_compute_metrics', store=False)
    amount_due = fields.Monetary(string='المبلغ المستحق', currency_field='currency_id', compute='_compute_metrics', store=False)
    expenses_amount = fields.Monetary(string='المصروفات', currency_field='currency_id', compute='_compute_metrics', store=False)
    revenues_amount = fields.Monetary(string='الإيرادات', currency_field='currency_id', compute='_compute_metrics', store=False)
    currency_id = fields.Many2one('res.currency', default=lambda self: self.env.company.currency_id)

    invoices_total = fields.Integer(string='عدد الفواتير الإجمالي', compute='_compute_metrics', store=False)
    invoices_paid = fields.Integer(string='عدد الفواتير المسددة', compute='_compute_metrics', store=False)
    invoices_due = fields.Integer(string='عدد الفواتير المستحقة', compute='_compute_metrics', store=False)

    summary_html = fields.Html(string='ملخص التحليل')
    yearly_html = fields.Html(string='المقارنة السنوية')
    predictions_html = fields.Html(string='توصيات وتوقعات')

    @api.depends(
        'company_id', 'branch_id', 'property_id', 'analytic_account_id',
        'partner_id', 'contract_number', 'date_from', 'date_to'
    )
    def _compute_metrics(self):
        for wiz in self:
            invoices = wiz._fetch_invoices()
            vendor_bills = wiz._fetch_expenses()

            paid_domain = [inv for inv in invoices if inv.payment_state == 'paid']
            due_domain = [inv for inv in invoices if inv.payment_state in ('not_paid', 'partial')]

            wiz.invoices_total = len(invoices)
            wiz.invoices_paid = len(paid_domain)
            wiz.invoices_due = len(due_domain)
            wiz.amount_paid = sum(inv.amount_total_signed for inv in paid_domain)
            wiz.amount_due = sum(inv.amount_total_signed for inv in due_domain)
            wiz.revenues_amount = sum(inv.amount_total_signed for inv in invoices)
            wiz.expenses_amount = sum(b.amount_total_signed for b in vendor_bills)

            # Render auxiliary HTML sections for immediate feedback on form open
            rev_by_year = group_by_year(invoices, lambda r: r.invoice_date, lambda r: r.amount_total_signed)
            exp_by_year = group_by_year(vendor_bills, lambda r: r.invoice_date, lambda r: r.amount_total_signed)
            wiz.yearly_html = wiz._render_yearly_html(rev_by_year, exp_by_year)

            rev_by_month = group_by_month(invoices, lambda r: r.invoice_date, lambda r: r.amount_total_signed)
            month_series = [(y, m, v) for ((y, m), v) in rev_by_month.items()]
            forecasts = simple_linear_forecast(month_series, horizon=3)
            wiz.predictions_html = wiz._render_predictions_html(forecasts)

            wiz.summary_html = wiz._render_summary_html()

    def action_compute(self):
        self.ensure_one()
        invoices = self._fetch_invoices()
        vendor_bills = self._fetch_expenses()
        # Aggregations
        paid_domain = [inv for inv in invoices if inv.payment_state == 'paid']
        due_domain = [inv for inv in invoices if inv.payment_state in ('not_paid', 'partial')]
        self.invoices_total = len(invoices)
        self.invoices_paid = len(paid_domain)
        self.invoices_due = len(due_domain)
        self.amount_paid = sum(inv.amount_total_signed for inv in paid_domain)
        self.amount_due = sum(inv.amount_total_signed for inv in due_domain)
        self.revenues_amount = sum(inv.amount_total_signed for inv in invoices)
        self.expenses_amount = sum(b.amount_total_signed for b in vendor_bills)

        # Yearly comparison
        rev_by_year = group_by_year(invoices, lambda r: r.invoice_date, lambda r: r.amount_total_signed)
        exp_by_year = group_by_year(vendor_bills, lambda r: r.invoice_date, lambda r: r.amount_total_signed)
        self.yearly_html = self._render_yearly_html(rev_by_year, exp_by_year)

        # Predictions (forecast next 3 months revenue)
        rev_by_month = group_by_month(invoices, lambda r: r.invoice_date, lambda r: r.amount_total_signed)
        month_series = [(y, m, v) for ((y, m), v) in rev_by_month.items()]
        forecasts = simple_linear_forecast(month_series, horizon=3)
        self.predictions_html = self._render_predictions_html(forecasts)

        # Summary
        self.summary_html = self._render_summary_html()

        return {
            'type': 'ir.actions.act_window',
            'res_model': 'rental.ai.insights.wizard',
            'view_mode': 'form',
            'res_id': self.id,
            'target': 'current',
        }

    def _base_invoice_domain(self):
        domain = [('move_type', '=', 'out_invoice'), ('state', '=', 'posted')]
        if self.company_id:
            domain.append(('company_id', '=', self.company_id.id))
        if self.partner_id:
            domain.append(('partner_id', '=', self.partner_id.id))
        if self.date_from:
            domain.append(('invoice_date', '>=', self.date_from))
        if self.date_to:
            domain.append(('invoice_date', '<=', self.date_to))
        # Join via sale order to filter branch/property/contract
        # property_name and obj_sale_order are added by renting module
        if self.property_id:
            domain.append(('property_name', '=', self.property_id.id))
        if self.contract_number:
            domain.append(('so_contract_number', '=', self.contract_number))
        # branch: attempt via sale order line (if present on invoice)
        if self.branch_id:
            domain.append(('rent_sale_line_id.property_address_area', '=', self.branch_id.name))
        return domain

    def _fetch_invoices(self):
        domain = self._base_invoice_domain()
        return self.env['account.move'].search(domain)

    def _fetch_expenses(self):
        domain = [('move_type', '=', 'in_invoice'), ('state', '=', 'posted')]
        if self.company_id:
            domain.append(('company_id', '=', self.company_id.id))
        if self.analytic_account_id:
            # match expense lines with analytic account
            bills = self.env['account.move'].search(domain)
            bills = bills.filtered(lambda m: any(l.analytic_account_id == self.analytic_account_id for l in m.line_ids))
            return bills
        if self.property_id:
            bills = self.env['account.move'].search(domain)
            bills = bills.filtered(lambda m: getattr(m, 'property_name', False) == self.property_id)
            return bills
        return self.env['account.move'].search(domain)

    def _render_summary_html(self):
        return (
            f"<div>"
            f"<h4>ملخص مالي</h4>"
            f"<ul>"
            f"<li>عدد الفواتير: {self.invoices_total}</li>"
            f"<li>الفواتير المسددة: {self.invoices_paid}</li>"
            f"<li>الفواتير المستحقة: {self.invoices_due}</li>"
            f"<li>الإيرادات: {self.revenues_amount:.2f} {self.currency_id.symbol}</li>"
            f"<li>المصروفات: {self.expenses_amount:.2f} {self.currency_id.symbol}</li>"
            f"<li>المدفوع: {self.amount_paid:.2f} {self.currency_id.symbol}</li>"
            f"<li>المستحق: {self.amount_due:.2f} {self.currency_id.symbol}</li>"
            f"</ul>"
            f"</div>"
        )

    def _render_yearly_html(self, rev_by_year, exp_by_year):
        rows = []
        years = sorted(set(rev_by_year.keys()) | set(exp_by_year.keys()))
        for y in years:
            rev = rev_by_year.get(y, 0.0)
            exp = exp_by_year.get(y, 0.0)
            net = rev - exp
            rows.append(f"<tr><td>{y}</td><td>{rev:.2f}</td><td>{exp:.2f}</td><td>{net:.2f}</td></tr>")
        table = (
            "<div>"
            "<h4>مقارنة سنوية</h4>"
            "<table class='table table-sm'>"
            "<thead><tr><th>السنة</th><th>الإيرادات</th><th>المصروفات</th><th>الصافي</th></tr></thead>"
            f"<tbody>{''.join(rows)}</tbody>"
            "</table>"
            "</div>"
        )
        return table

    def _render_predictions_html(self, forecasts):
        if not forecasts:
            return "<div><h4>توقعات</h4><p>لا توجد بيانات كافية للتنبؤ.</p></div>"
        rows = []
        for y, m, v in forecasts:
            rows.append(f"<tr><td>{y}-{m:02d}</td><td>{v:.2f}</td></tr>")
        return (
            "<div>"
            "<h4>توقع الإيرادات (3 أشهر)</h4>"
            "<table class='table table-sm'>"
            "<thead><tr><th>الشهر</th><th>القيمة المتوقعة</th></tr></thead>"
            f"<tbody>{''.join(rows)}</tbody>"
            "</table>"
            "<p>تم استخدام انحدار خطي بسيط لاكتشاف الاتجاه.</p>"
            "</div>"
        )
