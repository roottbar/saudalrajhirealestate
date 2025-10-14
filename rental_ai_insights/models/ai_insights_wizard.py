# -*- coding: utf-8 -*-

from odoo import models, fields, api
from odoo.exceptions import UserError
from collections import defaultdict
from datetime import datetime, date


class RentalAIInsightsWizard(models.TransientModel):
    _name = 'rental.ai.insights.wizard'
    _description = 'معالج تحليلات الإيجارات بالذكاء الاصطناعي'

    # Filters
    company_ids = fields.Many2many('res.company', string='الشركات', required=True, default=lambda self: self.env.company)
    operating_unit_id = fields.Many2one('operating.unit', string='الفرع',
                                        domain="[('company_id', 'in', company_ids)]")
    property_build_id = fields.Many2one('rent.property.build', string='المجمع')
    property_id = fields.Many2one('rent.property', string='العقار',
                                  domain="[('property_address_build', '=', property_build_id), ('property_address_area', '=', operating_unit_id)]")
    product_id = fields.Many2one('product.product', string='الوحدة', domain="[('property_id', '=', property_id)]")

    date_from = fields.Date(string='من تاريخ')
    date_to = fields.Date(string='إلى تاريخ')

    analysis_granularity = fields.Selection([
        ('year', 'سنوي'),
        ('month', 'شهري'),
    ], string='مستوى التحليل', default='year')

    compare_years = fields.Boolean(string='المقارنة التحليلية بين السنوات', default=True)
    include_invoice_analysis = fields.Boolean(string='تحليل الفواتير (مسددة/مستحقة)', default=True)
    include_predictions = fields.Boolean(string='توصيات تنبؤية (توقع الإيرادات)', default=True)

    report_type = fields.Selection([
        ('html', 'HTML'),
    ], string='نوع التقرير', default='html', required=True)

    @api.onchange('company_ids')
    def _onchange_company_ids(self):
        self.operating_unit_id = False
        self.property_build_id = False
        self.property_id = False
        self.product_id = False
        if self.company_ids:
            return {'domain': {'operating_unit_id': [('company_id', 'in', self.company_ids.ids)]}}
        return {'domain': {'operating_unit_id': []}}

    @api.onchange('operating_unit_id')
    def _onchange_operating_unit_id(self):
        self.property_build_id = False
        self.property_id = False
        self.product_id = False
        if self.operating_unit_id:
            properties = self.env['rent.property'].search([('property_address_area', '=', self.operating_unit_id.id)])
            build_ids = properties.mapped('property_address_build').ids
            return {'domain': {'property_build_id': [('id', 'in', build_ids)]}}
        return {'domain': {'property_build_id': []}}

    @api.onchange('property_build_id')
    def _onchange_property_build_id(self):
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
        self.product_id = False
        if self.property_id:
            return {'domain': {'product_id': [('property_id', '=', self.property_id.id)]}}
        return {'domain': {'product_id': []}}

    # Domains and data collection
    def _build_sale_line_domain(self):
        domain = []
        if self.company_ids:
            domain.append(('order_id.company_id', 'in', self.company_ids.ids))
        if self.operating_unit_id:
            domain.append(('property_address_area', '=', self.operating_unit_id.id))
        if self.property_build_id:
            domain.append(('property_address_build2', '=', self.property_build_id.id))
        if self.property_id:
            domain.append(('property_number', '=', self.property_id.id))
        if self.product_id:
            domain.append(('product_id', '=', self.product_id.id))

        # Overlapping date logic to include active contracts intersecting the period
        if self.date_from and self.date_to:
            domain.extend([
                ('fromdate', '<=', self.date_to),
                ('todate', '>=', self.date_from)
            ])
        elif self.date_from:
            domain.append(('todate', '>=', self.date_from))
        elif self.date_to:
            domain.append(('fromdate', '<=', self.date_to))
        return domain

    def _collect_core_records(self):
        lines = self.env['sale.order.line'].search(self._build_sale_line_domain())
        data = []
        for line in lines:
            filtered_invoices = line.order_id.order_contract_invoice
            if self.date_from and self.date_to:
                date_from_dt = datetime.combine(self.date_from, datetime.min.time()) if isinstance(self.date_from, date) else self.date_from
                date_to_dt = datetime.combine(self.date_to, datetime.max.time()) if isinstance(self.date_to, date) else self.date_to
                filtered_invoices = filtered_invoices.filtered(
                    lambda inv: inv.fromdate <= date_to_dt and inv.todate >= date_from_dt
                )
            elif self.date_from:
                date_from_dt = datetime.combine(self.date_from, datetime.min.time()) if isinstance(self.date_from, date) else self.date_from
                filtered_invoices = filtered_invoices.filtered(lambda inv: inv.todate >= date_from_dt)
            elif self.date_to:
                date_to_dt = datetime.combine(self.date_to, datetime.max.time()) if isinstance(self.date_to, date) else self.date_to
                filtered_invoices = filtered_invoices.filtered(lambda inv: inv.fromdate <= date_to_dt)

            invoice_total_amount = sum(filtered_invoices.mapped('amount')) if filtered_invoices else 0.0

            data.append({
                'company_name': line.order_id.company_id.name,
                'company_id': line.order_id.company_id.id,
                'operating_unit': line.property_address_area.name if line.property_address_area else '',
                'operating_unit_id': line.property_address_area.id if line.property_address_area else False,
                'property_build': line.property_address_build2.name if line.property_address_build2 else '',
                'property_build_id': line.property_address_build2.id if line.property_address_build2 else False,
                'property_name': line.property_number.property_name if line.property_number else '',
                'property_id': line.property_number.id if line.property_number else False,
                'analytic_account': line.analytic_account_id.name if line.analytic_account_id else '',
                'analytic_account_id': line.analytic_account_id.id if line.analytic_account_id else False,
                'unit_name': line.product_id.name,
                'unit_id': line.product_id.id,
                'customer_name': line.order_partner_id.name if line.order_partner_id else '',
                'contract_number': line.order_id.name,
                'ejar_contract_number': line.order_id.contract_number or '',
                'unit_state': line.unit_state or '',
                'contract_amount': line.order_id.amount_total or 0.0,
                'invoice_count': line.order_id.invoice_number or 0,
                'invoice_total_amount': invoice_total_amount,
                'amount_paid': line.amount_paid,
                'amount_due': line.amount_due,
                'from_date': line.fromdate,
                'to_date': line.todate,
                'sale_order_id': line.order_id.id,
            })
        return data

    def _collect_invoice_stats(self, sale_order_ids):
        domain = [
            ('move_type', 'in', ('out_invoice', 'out_refund')),
            ('state', '=', 'posted'),
        ]
        if self.date_from:
            domain.append(('invoice_date', '>=', self.date_from))
        if self.date_to:
            domain.append(('invoice_date', '<=', self.date_to))
        if self.company_ids:
            domain.append(('company_id', 'in', self.company_ids.ids))
        if sale_order_ids:
            domain.append(('renting_id', 'in', sale_order_ids))

        moves = self.env['account.move'].search(domain)
        paid = len(moves.filtered(lambda m: m.payment_state == 'paid'))
        due = len(moves.filtered(lambda m: m.payment_state in ('not_paid', 'partial', 'in_payment')))
        total_amount = sum(moves.mapped('amount_total'))
        residual = sum(moves.mapped('amount_residual'))
        return {
            'invoice_paid_count': paid,
            'invoice_due_count': due,
            'invoice_total_amount': total_amount,
            'invoice_total_residual': residual,
        }

    def _year_key(self, d):
        if not d:
            return None
        return d.year if isinstance(d, (datetime, date)) else fields.Date.from_string(d).year

    def _compute_yearly_comparison(self, core_data):
        by_year = defaultdict(lambda: {'revenue': 0.0, 'paid': 0.0, 'due': 0.0, 'contracts': 0})
        for row in core_data:
            year = self._year_key(row.get('from_date')) or self._year_key(row.get('to_date'))
            if not year:
                continue
            by_year[year]['revenue'] += row.get('invoice_total_amount', 0.0)
            by_year[year]['paid'] += row.get('amount_paid', 0.0)
            by_year[year]['due'] += row.get('amount_due', 0.0)
            by_year[year]['contracts'] += 1
        # Sorted list of years
        return [{'year': y, **vals} for y, vals in sorted(by_year.items())]

    def _predict_next_year_revenue(self, yearly):
        # Simple average growth model: average year-over-year growth applied to last year
        if not yearly or len(yearly) < 2:
            # Not enough data; return last year as baseline
            return yearly[-1]['revenue'] if yearly else 0.0
        yearly_sorted = sorted(yearly, key=lambda r: r['year'])
        growths = []
        for i in range(1, len(yearly_sorted)):
            prev = yearly_sorted[i-1]['revenue'] or 0.0001
            cur = yearly_sorted[i]['revenue']
            growths.append((cur - prev) / prev)
        avg_growth = sum(growths) / len(growths) if growths else 0.0
        forecast = yearly_sorted[-1]['revenue'] * (1.0 + avg_growth)
        return forecast

    def _rank_performance(self, core_data):
        by_property = defaultdict(lambda: {'name': '', 'revenue': 0.0, 'paid': 0.0, 'due': 0.0})
        by_branch = defaultdict(lambda: {'name': '', 'revenue': 0.0, 'paid': 0.0, 'due': 0.0})
        for row in core_data:
            pid = row.get('property_id') or 0
            bid = row.get('operating_unit_id') or 0
            by_property[pid]['name'] = row.get('property_name') or '—'
            by_property[pid]['revenue'] += row.get('invoice_total_amount', 0.0)
            by_property[pid]['paid'] += row.get('amount_paid', 0.0)
            by_property[pid]['due'] += row.get('amount_due', 0.0)
            by_branch[bid]['name'] = row.get('operating_unit') or '—'
            by_branch[bid]['revenue'] += row.get('invoice_total_amount', 0.0)
            by_branch[bid]['paid'] += row.get('amount_paid', 0.0)
            by_branch[bid]['due'] += row.get('amount_due', 0.0)

        top_props = sorted([
            {'name': v['name'], 'revenue': v['revenue'], 'paid_ratio': (v['paid'] / v['revenue']) if v['revenue'] else 0.0}
            for v in by_property.values()
        ], key=lambda r: r['revenue'], reverse=True)[:10]

        bottom_props = sorted([
            {'name': v['name'], 'revenue': v['revenue'], 'paid_ratio': (v['paid'] / v['revenue']) if v['revenue'] else 0.0}
            for v in by_property.values()
        ], key=lambda r: r['revenue'])[:10]

        top_branches = sorted([
            {'name': v['name'], 'revenue': v['revenue'], 'paid_ratio': (v['paid'] / v['revenue']) if v['revenue'] else 0.0}
            for v in by_branch.values()
        ], key=lambda r: r['revenue'], reverse=True)[:10]

        bottom_branches = sorted([
            {'name': v['name'], 'revenue': v['revenue'], 'paid_ratio': (v['paid'] / v['revenue']) if v['revenue'] else 0.0}
            for v in by_branch.values()
        ], key=lambda r: r['revenue'])[:10]

        return {
            'top_properties': top_props,
            'bottom_properties': bottom_props,
            'top_branches': top_branches,
            'bottom_branches': bottom_branches,
        }

    def action_generate_report(self):
        core_data = self._collect_core_records()
        sale_order_ids = list({row['sale_order_id'] for row in core_data if row.get('sale_order_id')})

        # Yearly comparison
        yearly = self._compute_yearly_comparison(core_data) if self.compare_years else []
        forecast_next_year = self._predict_next_year_revenue(yearly) if self.include_predictions else 0.0

        # Invoice stats
        invoice_stats = self._collect_invoice_stats(sale_order_ids) if self.include_invoice_analysis else {}

        # Rankings
        rankings = self._rank_performance(core_data)

        # Aggregate KPIs
        total_paid = sum(r.get('amount_paid', 0.0) for r in core_data)
        total_due = sum(r.get('amount_due', 0.0) for r in core_data)
        total_revenue = sum(r.get('invoice_total_amount', 0.0) for r in core_data)

        context = {
            'filters': {
                'companies': ', '.join(self.company_ids.mapped('name')) if self.company_ids else '',
                'operating_unit': self.operating_unit_id.name if self.operating_unit_id else '',
                'property_build': self.property_build_id.name if self.property_build_id else '',
                'property': self.property_id.property_name if self.property_id else '',
                'product': self.product_id.name if self.product_id else '',
                'date_from': self.date_from,
                'date_to': self.date_to,
            },
            'kpis': {
                'total_revenue': total_revenue,
                'total_paid': total_paid,
                'total_due': total_due,
            },
            'invoice_stats': invoice_stats,
            'yearly': yearly,
            'forecast_next_year': forecast_next_year,
            'rankings': rankings,
            'core_data': core_data,
        }

        # Use registered ir.actions.report to render HTML and pass data
        return self.env.ref('rental_ai_insights.rental_ai_insights_ai_report_action').report_action(self, data=context)