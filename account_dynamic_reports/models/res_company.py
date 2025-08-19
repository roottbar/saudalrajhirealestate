# -*- coding: utf-8 -*-

from odoo import api, fields, models
from odoo.exceptions import ValidationError


class ResCompany(models.Model):
    _inherit = 'res.company'

    strict_range = fields.Boolean(
        string='Use Strict Range', default=True,
        help='Use this if you want to show TB with retained earnings section'
    )
    bucket_1 = fields.Integer(string='Bucket 1', required=True, default=30)
    bucket_2 = fields.Integer(string='Bucket 2', required=True, default=60)
    bucket_3 = fields.Integer(string='Bucket 3', required=True, default=90)
    bucket_4 = fields.Integer(string='Bucket 4', required=True, default=120)
    bucket_5 = fields.Integer(string='Bucket 5', required=True, default=180)
    date_range = fields.Selection([
        ('today', 'Today'),
        ('this_week', 'This Week'),
        ('this_month', 'This Month'),
        ('this_quarter', 'This Quarter'),
        ('this_financial_year', 'This financial Year'),
        ('yesterday', 'Yesterday'),
        ('last_week', 'Last Week'),
        ('last_month', 'Last Month'),
        ('last_quarter', 'Last Quarter'),
        ('last_financial_year', 'Last Financial Year')
    ], string='Default Date Range', default='this_financial_year', required=True)
    financial_year = fields.Selection([
        ('april_march', '1 April to 31 March'),
        ('july_june', '1 July to 30 June'),
        ('january_december', '1 Jan to 31 Dec')
    ], string='Financial Year', default='january_december', required=True)


class ResCurrency(models.Model):
    _inherit = 'res.currency'

    excel_format = fields.Char(
        string='Excel format',
        default='_ * #,##0.00_) ;_ * - #,##0.00_) ;_ * "-"??_) ;_ @_ ',
        required=True
    )


class InsAccountFinancialReport(models.Model):
    _name = "ins.account.financial.report"
    _description = "Account Report"

    name = fields.Char('Report Name', required=True, translate=True)
    parent_id = fields.Many2one('ins.account.financial.report', 'Parent')
    children_ids = fields.One2many('ins.account.financial.report', 'parent_id', 'Account Report')
    sequence = fields.Integer('Sequence')
    level = fields.Integer(compute='_compute_level', string='Level', store=True)
    type = fields.Selection([
        ('sum', 'View'),
        ('accounts', 'Accounts'),
        ('account_type', 'Account Type'),
        ('account_report', 'Report Value')
    ], 'Type', default='sum')
    account_ids = fields.Many2many(
        'account.account', 'ins_account_account_financial_report',
        'report_line_id', 'account_id', 'Accounts'
    )
    account_report_id = fields.Many2one('ins.account.financial.report', 'Report Value')
    account_type_ids = fields.Many2many(
        'account.account.type', 'ins_account_account_financial_report_type',
        'report_id', 'account_type_id', 'Account Types'
    )
    sign = fields.Selection([
        ('-1', 'Reverse balance sign'),
        ('1', 'Preserve balance sign')
    ], 'Sign on Reports', required=True, default='1')
    range_selection = fields.Selection([
        ('from_the_beginning', 'From the Beginning'),
        ('current_date_range', 'Based on Current Date Range'),
        ('initial_date_range', 'Based on Initial Date Range')
    ], string='Custom Date Range')
    display_detail = fields.Selection([
        ('no_detail', 'No detail'),
        ('detail_flat', 'Display children flat'),
        ('detail_with_hierarchy', 'Display children with hierarchy')
    ], 'Display details', default='detail_flat')
    style_overwrite = fields.Selection([
        ('0', 'Automatic formatting'),
        ('1', 'Main Title 1 (bold, underlined)'),
        ('2', 'Title 2 (bold)'),
        ('3', 'Title 3 (bold, smaller)'),
        ('4', 'Normal Text'),
        ('5', 'Italic Text (smaller)'),
        ('6', 'Smallest Text'),
    ], 'Financial Report Style', default='0')

    # --- computed fields for visibility in form views ---
    show_range_selection = fields.Boolean(compute='_compute_visibility')
    show_display_detail = fields.Boolean(compute='_compute_visibility')
    show_account_report_id = fields.Boolean(compute='_compute_visibility')
    show_account_ids = fields.Boolean(compute='_compute_visibility')
    show_account_type_ids = fields.Boolean(compute='_compute_visibility')

    @api.depends('type')
    def _compute_visibility(self):
        for rec in self:
            rec.show_range_selection = rec.type in ['accounts', 'account_type']
            rec.show_display_detail = rec.type in ['accounts', 'account_type']
            rec.show_account_report_id = rec.type == 'account_report'
            rec.show_account_ids = rec.type == 'accounts'
            rec.show_account_type_ids = rec.type == 'account_type'

    @api.depends('parent_id')
    def _compute_level(self):
        for rec in self:
            rec.level = 0
            if rec.parent_id:
                rec.level = rec.parent_id.level + 1

    @api.constrains('range_selection', 'type')
    def _check_range_selection(self):
        for rec in self:
            if rec.type in ['accounts', 'account_type'] and not rec.range_selection:
                raise ValidationError("Range Selection is required for the selected type.")

    def _get_children_by_order(self, strict_range):
        res = self
        children = self.search([('parent_id', 'in', self.ids)], order='sequence ASC')
        for child in children:
            res += child._get_children_by_order(strict_range)
        if not strict_range:
            res -= self.env.ref('account_dynamic_reports.ins_account_financial_report_unallocated_earnings0')
            res -= self.env.ref('account_dynamic_reports.ins_account_financial_report_equitysum0')
        return res


class AccountAccount(models.Model):
    _inherit = 'account.account'

    def get_cashflow_domain(self):
        cash_flow_id = self.env.ref('account_dynamic_reports.ins_account_financial_report_cash_flow0')
        if cash_flow_id:
            return [('parent_id.id', '=', cash_flow_id.id)]

    cash_flow_category = fields.Many2one(
        'ins.account.financial.report',
        string="Cash Flow type",
        domain=get_cashflow_domain
    )

    @api.onchange('cash_flow_category')
    def onchange_cash_flow_category(self):
        if self._origin and self._origin.id:
            self.cash_flow_category.write({'account_ids': [(4, self._origin.id)]})
            self.env.ref('account_dynamic_reports.ins_account_financial_report_cash_flow0').write({'account_ids': [(4, self._origin.id)]})
        if self._origin.cash_flow_category:
            self._origin.cash_flow_category.write({'account_ids': [(3, self._origin.id)]})
            self.env.ref('account_dynamic_reports.ins_account_financial_report_cash_flow0').write({'account_ids': [(3, self._origin.id)]})


class CommonXlsxOut(models.TransientModel):
    _name = 'common.xlsx.out'

    filedata = fields.Binary('Download file', readonly=True)
    filename = fields.Char('Filename', size=64, readonly=True)
