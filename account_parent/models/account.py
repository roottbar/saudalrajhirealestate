# -*- coding: utf-8 -*-
##############################################################################
#
#    ODOO, Open Source Management Solution
#    Copyright (C) 2016 - 2020 Steigend IT Solutions (Omal Bastin)
#    Copyright (C) 2020 - Today O4ODOO (Omal Bastin)
#
##############################################################################
from odoo import api, fields, models
from odoo.osv import expression

import io
import json
import datetime
try:
    import xlwt
except ImportError:
    xlwt = None
from odoo.http import request, serialize_exception
from odoo import http, _

# class AccountAccountTemplate(models.Model):
#     _inherit = "account.account.template"

#     parent_id = fields.Many2one('account.account', 'Parent Account', ondelete="set null")

#     @api.model
#     def _search(self, args, offset=0, limit=None, order=None, count=False, access_rights_uid=None):
#         context = self._context or {}
#         new_args = []
#         if args:
#             for arg in args:
#                 if isinstance(arg, (list, tuple)) and arg[0] == 'name' and isinstance(arg[2], str):
#                     new_args.append('|')
#                     new_args.append(arg)
#                     new_args.append(['code', arg[1], arg[2]])
#                 else:
#                     new_args.append(arg)
#         if not context.get('show_parent_account', False):
#             new_args = expression.AND([[('user_type_id.type', '!=', 'view')], new_args])
#         return super(AccountAccountTemplate, self)._search(new_args, offset=offset,
#                                                            limit=limit, order=order, count=count,
#                                                            access_rights_uid=access_rights_uid)


class AccountAccountType(models.Model):
    _inherit = "account.account.type"

    type = fields.Selection(selection_add=[('view', 'View')], ondelete={'view': 'cascade'})


class AccountAccount(models.Model):
    _inherit = "account.account"

    parent_id = fields.Many2one('account.account', 'Parent Account', ondelete="set null")
    child_ids = fields.One2many('account.account', 'parent_id', 'Child Accounts')
    parent_path = fields.Char(index=True)

    @api.depends('move_line_ids.debit', 'move_line_ids.credit')
    def compute_values(self):
        for account in self:
            debit = sum(account.move_line_ids.mapped('debit'))
            credit = sum(account.move_line_ids.mapped('credit'))
            account.debit = debit
            account.credit = credit
            account.balance = debit - credit
            account.initial_balance = 0.0  # يمكنك إضافة الحساب الابتدائي هنا إذا لزم

    move_line_ids = fields.One2many('account.move.line', 'account_id', 'Journal Entry Lines')
    balance = fields.Float(compute="compute_values", digits=(16, 4), string='Balance')
    credit = fields.Float(compute="compute_values", digits=(16, 4), string='Credit')
    debit = fields.Float(compute="compute_values", digits=(16, 4), string='Debit')
    initial_balance = fields.Float(compute="compute_values", digits=(16, 4), string='Initial Balance')

    _parent_name = "parent_id"
    _parent_store = True
    _parent_order = 'code, name'
    _order = 'code, id'

    @api.model
    def _search(self, args, offset=0, limit=None, order=None, count=False, access_rights_uid=None):
        context = self._context or {}
        new_args = []
        if args:
            for arg in args:
                if isinstance(arg, (list, tuple)) and arg[0] == 'name' and isinstance(arg[2], str):
                    new_args.append('|')
                    new_args.append(arg)
                    new_args.append(['code', arg[1], arg[2]])
                else:
                    new_args.append(arg)
        if not context.get('show_parent_account', False):
            new_args = expression.AND([[('user_type_id.type', '!=', 'view')], new_args])
        return super(AccountAccount, self)._search(new_args, offset=offset, limit=limit, order=order,
                                                   count=count, access_rights_uid=access_rights_uid)


class AccountJournal(models.Model):
    _inherit = "account.journal"

    @api.model
    def _prepare_liquidity_account(self, name, company, currency_id, type):
        res = super(AccountJournal, self)._prepare_liquidity_account(name, company, currency_id, type)
        if type == 'bank':
            account_code_prefix = company.bank_account_code_prefix or ''
        else:
            account_code_prefix = company.cash_account_code_prefix or company.bank_account_code_prefix or ''

        parent_id = self.env['account.account'].with_context({'show_parent_account': True}).search([
            ('code', '=', account_code_prefix),
            ('company_id', '=', company.id),
            ('user_type_id.type', '=', 'view')], limit=1)

        if parent_id:
            res.update({'parent_id': parent_id.id})
        return res


# Controller لتصدير XLS
class CoAReportController(http.Controller):

    @http.route('/account_parent/export/xls', type='http', auth='user')
    def coa_xls_report(self, data, **kw):
        coa_data = json.loads(data)
        report_id = coa_data.get('wiz_id', [])
        report_obj = request.env['account.open.chart'].browse(report_id)

        lines = report_obj.get_xls_lines()  # افترض وجود دالة get_xls_lines في موديلك
        row_data = [['Code', 'Name', 'Type', 'Debit', 'Credit', 'Balance']]
        for line in lines:
            row_data.append([line['code'], line['name'], line['type'], line['debit'], line['credit'], line['balance']])

        return request.make_response(
            self.coa_format_data(['Chart of Accounts'], row_data),
            headers=[
                ('Content-Type', 'application/vnd.ms-excel'),
                ('Content-Disposition', 'attachment; filename=coa_report.xls;')
            ]
        )

    def coa_format_data(self, fields, rows):
        if not xlwt:
            raise ValueError(_('xlwt library is required to export XLS.'))
        workbook = xlwt.Workbook(style_compression=2)
        worksheet = workbook.add_sheet('Sheet 1')
        style = xlwt.easyxf('align: wrap yes')
        font = xlwt.Font()
        font.bold = True
        style.font = font
        for i, fieldname in enumerate(fields):
            worksheet.write(0, i, fieldname, style)
        for r, row in enumerate(rows):
            for c, val in enumerate(row):
                worksheet.write(r + 1, c, val)
        fp = io.BytesIO()
        workbook.save(fp)
        fp.seek(0)
        return fp.read()
