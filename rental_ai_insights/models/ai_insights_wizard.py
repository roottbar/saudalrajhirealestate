# -*- coding: utf-8 -*-

from odoo import models, fields, api
from .ai_utils import group_by_year, group_by_month, simple_linear_forecast


class RentalAIInsightsWizard(models.TransientModel):
    _name = 'rental.ai.insights.wizard'
    _description = 'Rental AI Insights Wizard'

    company_id = fields.Many2one('res.company', string='الشركة', default=lambda self: self.env.company)
    # حقول الربط والفلترة بحسب طلب المستخدم
    operating_unit_id = fields.Many2one('operating.unit', string='الفرع')
    property_address_area = fields.Many2one('operating.unit', string='الفرع')
    property_id = fields.Many2one('rent.property', string='العقار')
    property_number = fields.Many2one('rent.property', string='العقار')
    property_address_build2 = fields.Many2one('rent.property.build', string='المجمع')
    product_id = fields.Many2one('product.template', string='الوحدة')
    analytic_account_id = fields.Many2one('account.analytic.account', string='الحساب التحليلي')
    partner_id = fields.Many2one('res.partner', string='اسم العميل')
    order_partner_id = fields.Many2one('res.partner', string='إسم العميل')
    order_id = fields.Many2one('sale.order', string='رقم العقد')
    contract_number = fields.Char(string='رقم العقد')
    date_from = fields.Date(string='تاريخ الاستلام')
    date_to = fields.Date(string='تاريخ التسليم')

    sort_by = fields.Selection([
        ('property', 'العقار'),
        ('contract', 'رقم العقد'),
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
        'company_id', 'operating_unit_id', 'property_address_area', 'property_id', 'property_number',
        'property_address_build2', 'product_id', 'analytic_account_id',
        'partner_id', 'order_partner_id', 'order_id', 'contract_number',
        'date_from', 'date_to', 'sort_by'
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
        # العميل
        partner = self.order_partner_id or self.partner_id
        if partner:
            domain.append(('partner_id', '=', partner.id))
        if self.date_from:
            domain.append(('invoice_date', '>=', self.date_from))
        if self.date_to:
            domain.append(('invoice_date', '<=', self.date_to))
        # Join via sale order to filter branch/property/contract
        # property_name and obj_sale_order are added by renting module
        prop = self.property_number or self.property_id
        if prop:
            domain.append(('property_name', '=', prop.id))
        # الربط بالعقد مباشرة إن تم اختياره
        if self.order_id:
            domain.append(('obj_sale_order', '=', self.order_id.id))
        elif self.contract_number:
            # دعم الفلترة برقم العقد المخزن على أمر البيع
            domain.append(('so_contract_number', '=', self.contract_number))
        # الفرع
        ou = self.property_address_area or self.operating_unit_id
        if ou:
            domain.append(('operating_unit_id', '=', ou.id))
        return domain

    def _fetch_invoices(self):
        domain = self._base_invoice_domain()
        return self.env['account.move'].search(domain)

    def _fetch_expenses(self):
        domain = [('move_type', '=', 'in_invoice'), ('state', '=', 'posted')]
        if self.company_id:
            domain.append(('company_id', '=', self.company_id.id))
        ou = self.property_address_area or self.operating_unit_id
        if ou:
            domain.append(('operating_unit_id', '=', ou.id))
        if self.analytic_account_id:
            domain.append(('line_ids.analytic_account_id', '=', self.analytic_account_id.id))
        prop = self.property_number or self.property_id
        if prop:
            domain.append(('property_name', '=', prop.id))
        # المصروفات على مستوى الوحدة إن تم اختيارها
        if self.product_id:
            domain.append(('unit_number', '=', self.product_id.id))
        return self.env['account.move'].search(domain)

    def _fetch_contract_lines(self):
        """Fetch sale.order.line records overlapping the selected date range and filters."""
        domain = []
        if self.company_id:
            domain.append(('order_id.company_id', '=', self.company_id.id))
        partner = self.order_partner_id or self.partner_id
        if partner:
            domain.append(('order_partner_id', '=', partner.id))
        if self.analytic_account_id:
            domain.append(('analytic_account_id', '=', self.analytic_account_id.id))
        prop = self.property_number or self.property_id
        if prop:
            domain.append(('property_number', '=', prop.id))
        # المجمع
        if self.property_address_build2:
            domain.append(('property_address_build2', '=', self.property_address_build2.id))
        # الوحدة (product.template -> sale.order.line.product_id.product_tmpl_id)
        if self.product_id:
            domain.append(('product_id.product_tmpl_id', '=', self.product_id.id))
        # العقد
        if self.order_id:
            domain.append(('order_id', '=', self.order_id.id))
        elif self.contract_number:
            domain.append(('order_id.name', '=', self.contract_number))
        # الفرع
        ou = self.property_address_area or self.operating_unit_id
        if ou:
            domain.append(('order_id.operating_unit_id', '=', ou.id))

        # Date overlap: fromdate <= date_to AND todate >= date_from
        if self.date_from:
            domain.append(('todate', '>=', self.date_from))
        if self.date_to:
            domain.append(('fromdate', '<=', self.date_to))
        order_map = {
            'property': 'property_number',
            # Odoo doesn't support ordering by subfield (order_id.name).
            # Use the Many2one field itself; it sorts by record name.
            'contract': 'order_id',
        }
        # Default order by contract (sale order reference)
        orderby = order_map.get(self.sort_by) or 'order_id'
        return self.env['sale.order.line'].search(domain, order=orderby)

    @api.onchange('operating_unit_id')
    def _onchange_operating_unit_id(self):
        """عند تغيير الفرع، يتم تقييد العقارات والحسابات التحليلية لتابعة لنفس الفرع.
        كما يتم إعادة تعيين الحقول غير المتوافقة.
        """
        domain = {}
        if self.operating_unit_id:
            # العقارات التابعة لهذا الفرع
            domain['property_id'] = [('property_address_area', '=', self.operating_unit_id.id)]
            domain['property_number'] = [('property_address_area', '=', self.operating_unit_id.id)]
            # المجمعات عبر العقارات المختارة لاحقاً
            domain['property_address_build2'] = []
            # الحسابات التحليلية التابعة لهذا الفرع
            # يعتمد على الحقل operating_unit_id في account.analytic.account
            domain['analytic_account_id'] = [('operating_unit_id', '=', self.operating_unit_id.id)]
            # الوحدات التابعة لعقارات هذا الفرع
            domain['product_id'] = [('property_id.property_address_area', '=', self.operating_unit_id.id)]
            # إعادة تعيين إذا خرجت القيم عن النطاق
            if self.property_id and self.property_id.property_address_area != self.operating_unit_id:
                self.property_id = False
            if self.property_number and self.property_number.property_address_area != self.operating_unit_id:
                self.property_number = False
            if self.analytic_account_id and getattr(self.analytic_account_id, 'operating_unit_id', False) != self.operating_unit_id:
                self.analytic_account_id = False
            # مزامنة حقل الفرع البديل
            self.property_address_area = self.operating_unit_id
        return {'domain': domain} if domain else {}

    @api.onchange('property_address_area')
    def _onchange_property_address_area(self):
        """مزامنة اختيار الفرع البديل مع الفرع الأساسي وتقييد باقي الحقول."""
        if self.property_address_area:
            self.operating_unit_id = self.property_address_area
            return self._onchange_operating_unit_id()
        return {}

    @api.onchange('property_id')
    def _onchange_property_id(self):
        """عند اختيار العقار، يتم ضبط الفرع تلقائياً، وتقييد الحساب التحليلي ليطابق عقار المختار.
        كما يتم تعيين الحساب التحليلي للقيمة الافتراضية لعقار المختار إن وُجد.
        """
        domain = {}
        if self.property_id:
            # ضبط الفرع من العقار
            if self.property_id.property_address_area:
                self.operating_unit_id = self.property_id.property_address_area
                self.property_address_area = self.property_id.property_address_area
                domain['property_id'] = [('property_address_area', '=', self.operating_unit_id.id)]
                domain['analytic_account_id'] = [('operating_unit_id', '=', self.operating_unit_id.id)]
            # تقييد الحساب التحليلي ليكون حساب العقار نفسه
            if self.property_id.analytic_account:
                domain['analytic_account_id'] = [('id', '=', self.property_id.analytic_account.id)]
                # ضبط الحساب التحليلي تلقائياً إن لم يكن محدداً أو غير متوافق
                if not self.analytic_account_id or self.analytic_account_id != self.property_id.analytic_account:
                    self.analytic_account_id = self.property_id.analytic_account
            # مزامنة العقار البديل والمجمع
            self.property_number = self.property_id
            self.property_address_build2 = self.property_id.property_address_build
            # تقييد الوحدات لعقار المختار
            domain['product_id'] = [('property_id', '=', self.property_id.id)]
        return {'domain': domain} if domain else {}

    @api.onchange('property_number')
    def _onchange_property_number(self):
        """مزامنة اختيار العقار البديل مع العقار الأساسي وباقي الحقول."""
        if self.property_number:
            self.property_id = self.property_number
            return self._onchange_property_id()
        return {}

    @api.onchange('property_address_build2')
    def _onchange_property_address_build2(self):
        """تقييد العقارات والوحدات حسب المجمع المختار، ومزامنة الفرع إن أمكن."""
        domain = {}
        if self.property_address_build2:
            # تقييد العقارات بهذا المجمع
            domain['property_id'] = [('property_address_build', '=', self.property_address_build2.id)]
            domain['property_number'] = [('property_address_build', '=', self.property_address_build2.id)]
            # تقييد الوحدات لعقارات هذا المجمع
            domain['product_id'] = [('property_id.property_address_build', '=', self.property_address_build2.id)]
            # محاولة مزامنة الفرع عبر أول عقار مطابق
            prop = self.env['rent.property'].search([('property_address_build', '=', self.property_address_build2.id)], limit=1)
            if prop and prop.property_address_area:
                self.operating_unit_id = prop.property_address_area
                self.property_address_area = prop.property_address_area
        return {'domain': domain} if domain else {}

    @api.onchange('analytic_account_id')
    def _onchange_analytic_account_id(self):
        """عند اختيار الحساب التحليلي، يتم ضبط الفرع تلقائياً،
        ومحاولة تعيين العقار الذي يملك هذا الحساب التحليلي.
        """
        domain = {}
        if self.analytic_account_id:
            # ضبط الفرع إن كان معرفاً على الحساب التحليلي
            ou = getattr(self.analytic_account_id, 'operating_unit_id', False)
            if ou:
                self.operating_unit_id = ou
                self.property_address_area = ou
                domain['property_id'] = [('property_address_area', '=', ou.id)]
                domain['property_number'] = [('property_address_area', '=', ou.id)]
                domain['analytic_account_id'] = [('operating_unit_id', '=', ou.id)]
            # ربط العقار بالحساب التحليلي إن وُجد
            prop = self.env['rent.property'].search([('analytic_account', '=', self.analytic_account_id.id)], limit=1)
            if prop:
                self.property_id = prop
                self.property_number = prop
                # تقييد الحساب التحليلي ليكون نفس حساب العقار المحدد
                domain['analytic_account_id'] = [('id', '=', prop.analytic_account.id)]
                # مزامنة المجمع
                self.property_address_build2 = prop.property_address_build
                domain['product_id'] = [('property_id', '=', prop.id)]
        return {'domain': domain} if domain else {}

    @api.onchange('product_id')
    def _onchange_product_id(self):
        """عند اختيار الوحدة، يتم ضبط العقار والمجمع والفرع والحساب التحليلي تلقائياً."""
        domain = {}
        if self.product_id:
            prop = self.product_id.property_id
            if prop:
                self.property_id = prop
                self.property_number = prop
                self.property_address_build2 = prop.property_address_build
                self.operating_unit_id = prop.property_address_area
                self.property_address_area = prop.property_address_area
                domain['analytic_account_id'] = [('id', '=', getattr(self.product_id, 'analytic_account', False) and self.product_id.analytic_account.id or False)]
                if getattr(self.product_id, 'analytic_account', False):
                    self.analytic_account_id = self.product_id.analytic_account
            # تقييد العقارات والوحدات بنفس الترابط
            domain['property_id'] = [('id', '=', prop.id)] if prop else []
            domain['property_number'] = [('id', '=', prop.id)] if prop else []
        return {'domain': domain} if domain else {}

    @api.onchange('order_partner_id')
    def _onchange_order_partner_id(self):
        """مزامنة اسم العميل مع الحقل الأساسي وتقييد العقود."""
        domain = {}
        if self.order_partner_id:
            self.partner_id = self.order_partner_id
            domain['order_id'] = [('partner_id', '=', self.order_partner_id.id)]
        return {'domain': domain} if domain else {}

    @api.onchange('partner_id')
    def _onchange_partner_id(self):
        if self.partner_id:
            self.order_partner_id = self.partner_id
            return self._onchange_order_partner_id()
        return {}

    @api.onchange('order_id')
    def _onchange_order_id(self):
        """عند اختيار العقد، مزامنة العميل والفرع تلقائياً."""
        if self.order_id:
            self.order_partner_id = self.order_id.partner_id
            self.partner_id = self.order_id.partner_id
            if getattr(self.order_id, 'operating_unit_id', False):
                self.operating_unit_id = self.order_id.operating_unit_id
                self.property_address_area = self.order_id.operating_unit_id
        return {}

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
        # Some databases may not have 'tender_contract_id' on stock.picking.
        # Detect field existence to avoid AttributeError and provide a graceful fallback.
        has_tender_field = 'tender_contract_id' in StockPicking._fields
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
                    # إذا كان الحقل tender_contract_id موجودًا استخدمه، وإلا وفّر بديلًا آمنًا
                    if has_tender_field:
                        tender_ref = ''
                        for p in pickings:
                            t = p.tender_contract_id
                            if t:
                                # بعض النماذج تحتوي على ref و name، التزم بالأولوية لـ ref إن وجد
                                ref_val = ('ref' in t._fields) and t.ref or False
                                name_val = ('name' in t._fields) and t.name or False
                                tender_ref = ref_val or name_val or ''
                                if tender_ref:
                                    break
                        do_contract = tender_ref
                    else:
                        # بديل: اعرض مرجع أمر التوصيل (origin أو name) إن وُجد
                        if pickings:
                            p0 = pickings[0]
                            do_contract = p0.origin or p0.name or ''
                        else:
                            do_contract = ''
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