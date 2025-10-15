# -*- coding: utf-8 -*-

from odoo import models, fields, api
from .ai_utils import group_by_year, group_by_month, simple_linear_forecast


class RentalAIInsightsWizard(models.TransientModel):
    _name = 'rental.ai.insights.wizard'
    _description = 'Rental AI Insights Wizard'

    company_id = fields.Many2one('res.company', string='الشركة', default=lambda self: self.env.company)
    operating_unit_id = fields.Many2one('operating.unit', string='الفرع')
    property_id = fields.Many2one('rent.property', string='العقار')
    product_id = fields.Many2one('product.product', string='المنتج')
    analytic_account_id = fields.Many2one('account.analytic.account', string='الحساب التحليلي')
    partner_id = fields.Many2one('res.partner', string='اسم العميل')
    contract_number = fields.Char(string='رقم العقد')
    date_from = fields.Date(string='تاريخ الاستلام')
    date_to = fields.Date(string='تاريخ التسليم')

    sort_by = fields.Selection([
        ('property', 'العقار'),
        ('contract', 'رقم العقد'),
        ('product', 'المنتج'),
    ], string='ترتيب حسب')

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
    property_predictions_html = fields.Html(string='توقعات العقار')
    contracts_html = fields.Html(string='تقرير العقود')

    @api.depends(
        'company_id', 'operating_unit_id', 'property_id', 'product_id', 'analytic_account_id',
        'partner_id', 'contract_number', 'date_from', 'date_to', 'sort_by'
    )
    def _compute_metrics(self):
        for wiz in self:
            invoices = wiz._fetch_invoices()
            vendor_bills = wiz._fetch_expenses()
            contract_lines = wiz._fetch_contract_lines()

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

            # Property-specific predictions
            if wiz.property_id:
                prop_invoices = invoices.filtered(lambda inv: getattr(inv, 'property_name', False) == wiz.property_id)
                prop_by_month = group_by_month(prop_invoices, lambda r: r.invoice_date, lambda r: r.amount_total_signed)
                prop_series = [(y, m, v) for ((y, m), v) in prop_by_month.items()]
                prop_forecasts = simple_linear_forecast(prop_series, horizon=3)
                wiz.property_predictions_html = wiz._render_property_predictions_html(prop_forecasts)
            else:
                wiz.property_predictions_html = "<div><p>اختر عقارًا لعرض توقعاته.</p></div>"

            wiz.summary_html = wiz._render_summary_html()
            wiz.contracts_html = wiz._render_contracts_html(contract_lines)

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
        if self.product_id:
            domain.append(('invoice_line_ids.product_id', '=', self.product_id.id))
        if self.contract_number:
            domain.append(('so_contract_number', '=', self.contract_number))
        # operating_unit filtering on invoices depends on custom relations; handled in contracts report instead
        return domain

    def _fetch_invoices(self):
        domain = self._base_invoice_domain()
        return self.env['account.move'].search(domain)

    def _fetch_expenses(self):
        domain = [('move_type', '=', 'in_invoice'), ('state', '=', 'posted')]
        if self.company_id:
            domain.append(('company_id', '=', self.company_id.id))
        if self.product_id:
            # Apply product filter to vendor bills if products are used
            domain.append(('invoice_line_ids.product_id', '=', self.product_id.id))
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

    def _fetch_contract_lines(self):
        """Fetch sale.order.line records overlapping the selected date range and filters."""
        domain = []
        if self.company_id:
            domain.append(('order_id.company_id', '=', self.company_id.id))
        if self.partner_id:
            domain.append(('order_partner_id', '=', self.partner_id.id))
        if self.analytic_account_id:
            domain.append(('analytic_account_id', '=', self.analytic_account_id.id))
        if self.property_id:
            domain.append(('property_number', '=', self.property_id.id))
        if self.product_id:
            domain.append(('product_id', '=', self.product_id.id))
        if self.contract_number:
            domain.append(('order_id.name', '=', self.contract_number))
        if self.operating_unit_id:
            domain.append(('order_id.operating_unit_id', '=', self.operating_unit_id.id))

        # Date overlap: fromdate <= date_to AND todate >= date_from
        if self.date_from:
            domain.append(('todate', '>=', self.date_from))
        if self.date_to:
            domain.append(('fromdate', '<=', self.date_to))
        order_map = {
            'property': 'property_number',
            'contract': 'order_id.name',
            'product': 'product_id',
        }
        orderby = order_map.get(self.sort_by) or 'order_id.name'
        return self.env['sale.order.line'].search(domain, order=orderby)

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

    def _render_property_predictions_html(self, forecasts):
        title = f"توقع الإيرادات للعقار: {self.property_id.display_name}" if self.property_id else "توقع الإيرادات للعقار"
        if not forecasts:
            return f"<div><h4>{title}</h4><p>لا توجد بيانات كافية للتنبؤ.</p></div>"
        rows = []
        for y, m, v in forecasts:
            rows.append(f"<tr><td>{y}-{m:02d}</td><td>{v:.2f}</td></tr>")
        return (
            f"<div><h4>{title}</h4>"
            "<table class='table table-sm'>"
            "<thead><tr><th>الشهر</th><th>القيمة المتوقعة</th></tr></thead>"
            f"<tbody>{''.join(rows)}</tbody>"
            "</table>"
            "</div>"
        )

    def _render_contracts_html(self, lines):
        # ترتيب الأعمدة كما في الصورة: الفرع، المجمع، العقار، الحساب التحليلي، الوحدة، اسم العميل، رقم العقد، الحالة،
        # ثم المبالغ، ثم تاريخ الاستلام والتسليم
        header = (
            "<thead><tr>"
            "<th>الفرع</th><th>المجمع</th><th>العقار</th><th>الحساب التحليلي</th><th>الوحدة</th><th>اسم العميل</th>"
            "<th>رقم العقد</th><th>رقم عقد التوصيل</th><th>شاغرة / مؤجرة</th>"
            "<th>المبلغ المستحق</th><th>المبلغ المدفوع</th><th>المصروفات</th><th>الإيرادات</th>"
            "<th>تاريخ الاستلام</th><th>تاريخ التسليم</th>"
            "</tr></thead>"
        )
        rows = []
        # Cache delivery order contract numbers per sale order to avoid repeated searches
        do_contract_cache = {}
        StockPicking = self.env['stock.picking']
        for l in lines:
            pickup = l.pickup_date and fields.Datetime.to_string(l.pickup_date) or ''
            return_d = l.return_date and fields.Datetime.to_string(l.return_date) or ''
            revenues = getattr(l, 'unit_revenues', 0.0) or 0.0
            expenses = getattr(l, 'unit_expenses', 0.0) or 0.0
            due = getattr(l, 'amount_due', 0.0) or 0.0
            paid = getattr(l, 'amount_paid', 0.0) or 0.0
            state = getattr(l, 'unit_state', '') or ''
            contract = l.order_id and l.order_id.name or ''
            # رقم عقد التوصيل من أوامر التوصيل المرتبطة
            do_contract = ''
            if l.order_id:
                so_name = l.order_id.name
                if so_name in do_contract_cache:
                    do_contract = do_contract_cache[so_name]
                else:
                    pickings = StockPicking.search([('origin', '=', so_name)])
                    # استخلاص رقم العقد من الحقل tender_contract_id إذا كان موجودًا
                    tender_refs = [p.tender_contract_id.ref or p.tender_contract_id.name for p in pickings if p.tender_contract_id]
                    do_contract = tender_refs and tender_refs[0] or ''
                    do_contract_cache[so_name] = do_contract
            customer = l.order_partner_id and l.order_partner_id.display_name or ''
            unit = l.product_id and l.product_id.display_name or ''
            analytic = l.analytic_account_id and l.analytic_account_id.display_name or ''
            property_name = l.property_number and l.property_number.display_name or ''
            complex_name = getattr(l, 'property_address_build2', '') or ''
            branch = l.order_id.operating_unit_id and l.order_id.operating_unit_id.name or ''
            rows.append(
                f"<tr><td>{branch}</td><td>{complex_name}</td><td>{property_name}</td><td>{analytic}</td><td>{unit}</td><td>{customer}</td>"
                f"<td>{contract}</td><td>{do_contract}</td><td>{state}</td>"
                f"<td>{due:.2f}</td><td>{paid:.2f}</td><td>{expenses:.2f}</td><td>{revenues:.2f}</td>"
                f"<td>{pickup}</td><td>{return_d}</td>"
                "</tr>"
            )
        table = (
            "<div>"
            "<h4>تقرير العقود للفترة المحددة</h4>"
            "<table class='table table-sm'>"
            f"{header}<tbody>{''.join(rows)}</tbody>"
            "</table>"
            "</div>"
        )
        return table