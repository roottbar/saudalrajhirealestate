# -*- coding: utf-8 -*-

from odoo import api, models


class ReportPettyCashLines(models.AbstractModel):
    _name = 'report.petty_cash.report_petty_cash_lines'

    @api.model
    def get_petty_cash_lines(self, data=None):
        filters = ''
        cr = self.env.cr

        if data['form']['date_from']:
            filters += " AND l.date >= '%s'" % data['form']['date_from']

        if data['form']['date_to']:
            filters += " AND l.date <= '%s'" % data['form']['date_to']

        if data['form']['responsible_ids']:
            responsible_ids = data['form']['responsible_ids']

            if len(responsible_ids) == 1:
                filters += ' AND p.responsible_id = ' + str(responsible_ids[0])
            else:
                filters += ' AND p.responsible_id IN ' + str(tuple(responsible_ids))

        if data['form']['product_ids']:
            product_ids = data['form']['product_ids']
            if len(product_ids) == 1:
                filters += ' AND l.product_id = ' + str(product_ids[0])
            else:
                filters += ' AND l.product_id IN ' + str(tuple(product_ids))

        if data['form']['account_ids']:
            account_ids = data['form']['account_ids']
            if len(account_ids) == 1:
                filters += ' AND l.account_id = ' + str(account_ids[0])
            else:
                filters += ' AND l.account_id IN ' + str(tuple(account_ids))

        if data['form']['partner_ids']:
            partner_ids = data['form']['partner_ids']
            if len(partner_ids) == 1:
                filters += ' AND l.partner_id = ' + str(partner_ids[0])
            else:
                filters += ' AND l.partner_id IN ' + str(tuple(partner_ids))

        if data['form']['analytic_account_ids']:
            analytic_account_ids = data['form']['analytic_account_ids']
            if len(analytic_account_ids) == 1:
                filters += ' AND l.analytic_account_id = ' + str(analytic_account_ids[0])
            else:
                filters += ' AND l.analytic_account_id IN ' + str(tuple(analytic_account_ids))

        if data['form']['include_tax']:
            filters += ' AND l.amount_tax != 0'

        sql = """SELECT l.description, l.date, l.amount_untaxed, l.amount_tax, p.name AS petty_cash_name, 
                        rp.name AS responsible_name, aa.name AS account_name FROM petty_cash_line AS l, 
                        petty_cash AS p, res_users AS ru, res_partner as rp, account_account AS aa 
                        where p.id = l.petty_cash_id AND ru.id = p.responsible_id AND rp.id = ru.partner_id 
                        AND aa.id = l.account_id"""

        if data['form']['group_by']:
            res = []
            if data['form']['group_by'] == 'product':
                product_obj = self.env['product.product']
                cr.execute("SELECT product_id FROM petty_cash_line where product_id IS NOT NULL GROUP BY product_id")

                for row in cr.dictfetchall():
                    product_id = row['product_id']
                    filter_group = filters + ' AND l.product_id = ' + str(product_id)
                    cr.execute(sql + filter_group)
                    petty_cash_lines = cr.dictfetchall()

                    # sum total amount untaxed and amount tax
                    sum_amount = self._sum_total_amount(petty_cash_lines)

                    if data['form']['display'] == 'all' or petty_cash_lines:
                        res.append({
                            'group_name': product_obj.browse(product_id).name,
                            'petty_cash_lines': petty_cash_lines,
                            'group_amount_untaxed': sum_amount['total_amount_untaxed'],
                            'group_amount_tax': sum_amount['total_amount_tax'],
                            'group_total_amount': sum_amount['total_amount']
                        })
            elif data['form']['group_by'] == 'responsible box':
                res_users_obj = self.env['res.users']
                cr.execute("SELECT responsible_id FROM petty_cash GROUP BY responsible_id")

                for row in cr.dictfetchall():
                    responsible_id = row['responsible_id']
                    filter_group = filters + ' AND p.responsible_id = ' + str(responsible_id)
                    cr.execute(sql + filter_group)
                    petty_cash_lines = cr.dictfetchall()

                    # sum total amount untaxed and amount tax
                    sum_amount = self._sum_total_amount(petty_cash_lines)

                    if data['form']['display'] == 'all' or petty_cash_lines:
                        res.append({
                            'group_name': res_users_obj.browse(responsible_id).name,
                            'petty_cash_lines': petty_cash_lines,
                            'group_amount_untaxed': sum_amount['total_amount_untaxed'],
                            'group_amount_tax': sum_amount['total_amount_tax'],
                            'group_total_amount': sum_amount['total_amount']
                        })

            elif data['form']['group_by'] == 'account':
                account_obj = self.env['account.account']
                cr.execute("SELECT account_id FROM petty_cash_line GROUP BY account_id")

                for row in cr.dictfetchall():
                    account_id = row['account_id']
                    filter_group = filters + ' AND l.account_id = ' + str(account_id)
                    cr.execute(sql + filter_group)
                    petty_cash_lines = cr.dictfetchall()

                    # sum total amount untaxed and amount tax
                    sum_amount = self._sum_total_amount(petty_cash_lines)

                    if data['form']['display'] == 'all' or petty_cash_lines:
                        res.append({
                            'group_name': account_obj.browse(account_id).name,
                            'petty_cash_lines': petty_cash_lines,
                            'group_amount_untaxed': sum_amount['total_amount_untaxed'],
                            'group_amount_tax': sum_amount['total_amount_tax'],
                            'group_total_amount': sum_amount['total_amount']
                        })

            elif data['form']['group_by'] == 'analytic_account':
                analytic_account_obj = self.env['account.analytic.account']
                cr.execute("""SELECT analytic_account_id FROM petty_cash_line where analytic_account_id IS NOT NULL 
                              GROUP BY analytic_account_id""")

                for row in cr.dictfetchall():
                    analytic_account_id = row['analytic_account_id']
                    filter_group = filters + ' AND l.analytic_account_id = ' + str(analytic_account_id)
                    cr.execute(sql + filter_group)
                    petty_cash_lines = cr.dictfetchall()

                    # sum total amount untaxed and amount tax
                    sum_amount = self._sum_total_amount(petty_cash_lines)

                    if data['form']['display'] == 'all' or petty_cash_lines:
                        res.append({
                            'group_name': analytic_account_obj.browse(analytic_account_id).name,
                            'petty_cash_lines': petty_cash_lines,
                            'group_amount_untaxed': sum_amount['total_amount_untaxed'],
                            'group_amount_tax': sum_amount['total_amount_tax'],
                            'group_total_amount': sum_amount['total_amount']
                        })
        else:
            sql += filters
            cr.execute(sql)
            res = cr.dictfetchall()

        return res

    def _sum_total_amount(self, lines):
        total_amount_tax = 0
        total_amount_untaxed = 0
        for line in lines:
            total_amount_untaxed += line['amount_untaxed']
            total_amount_tax += line['amount_tax']

        return {
            "total_amount_untaxed": total_amount_untaxed,
            "total_amount_tax": total_amount_tax,
            "total_amount": total_amount_untaxed + total_amount_tax
        }

    @api.model
    def _get_report_values(self, docids, data=None):
        petty_cash_lines = self.get_petty_cash_lines(data)
        print_responsible = False
        print_products = False
        print_accounts = False
        print_partners = False
        print_analytic_accounts = False

        if data['form'].get('responsible_ids', False):
            print_responsible = ','.join(
                [responsible.name for responsible in
                 self.env['res.users'].search([('id', 'in', data['form']['responsible_ids'])])])

        if data['form'].get('product_ids', False):
            print_products = ','.join(
                [product.name for product in
                 self.env['product.product'].search([('id', 'in', data['form']['product_ids'])])])

        if data['form'].get('account_ids', False):
            print_accounts = ','.join(
                [account.name for account in
                 self.env['account.account'].search([('id', 'in', data['form']['account_ids'])])])

        if data['form'].get('partner_ids', False):
            print_partners = ','.join(
                [partner.name for partner in
                 self.env['res.partner'].search([('id', 'in', data['form']['partner_ids'])])])

        if data['form'].get('analytic_account_ids', False):
            print_analytic_accounts = ','.join(
                [analytic_account.name for analytic_account in
                 self.env['account.analytic.account'].search([('id', 'in', data['form']['analytic_account_ids'])])])

        return {
            'data': data['form'],
            'petty_cash_lines': petty_cash_lines,
            'print_responsible': print_responsible,
            'print_products': print_products,
            'print_accounts': print_accounts,
            'print_partners': print_partners,
            'print_analytic_accounts': print_analytic_accounts,
        }
