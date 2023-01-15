import itertools

from odoo import models, api


class DynamicReportPettyCashLines(models.TransientModel):
    _name = 'report.dynamic.petty.cash.lines'
    _description = 'Dynamic report helper model'

    def _get_currency(self):
        return self.env.user.company_id.currency_id.symbol

    @api.model
    def filter_config_responsible(self):
        user_rules = self.env['petty.cash.user.rule'].search([])
        responsible_ids = set()
        for user_rule in user_rules:
            responsible_ids.add(user_rule.user.id)

        return list(responsible_ids)

    @api.model
    def filter_config_products(self):
        return eval(self.env["ir.config_parameter"].sudo().get_param('products', '[]'))

    @api.model
    def filter_config_accounts(self):
        return eval(self.env["ir.config_parameter"].sudo().get_param('accounts', '[]'))

    @api.model
    def filter_config_partners(self):
        return eval(self.env["ir.config_parameter"].sudo().get_param('petty_cash.partner_ids', '[]'))

    @api.model
    def filter_config_analytic_account(self):
        return eval(self.env["ir.config_parameter"].sudo().get_param('analytic_account_ids', '[]'))

    @api.model
    def get_petty_cash_lines(self, data=None):
        filters = ''
        cr = self.env.cr

        if data['date_from']:
            filters += " AND l.date >= '%s'" % data['date_from']

        if data['date_to']:
            filters += " AND l.date <= '%s'" % data['date_to']

        if data['responsible_ids']:
            responsible_ids = data['responsible_ids']

            if len(responsible_ids) == 1:
                filters += ' AND p.responsible_id = ' + str(responsible_ids[0])
            else:
                filters += ' AND p.responsible_id IN ' + str(tuple(responsible_ids))

        if data['product_ids']:
            product_ids = data['product_ids']
            if len(product_ids) == 1:
                filters += ' AND l.product_id = ' + str(product_ids[0])
            else:
                filters += ' AND l.product_id IN ' + str(tuple(product_ids))

        if data['account_ids']:
            account_ids = data['account_ids']
            if len(account_ids) == 1:
                filters += ' AND l.account_id = ' + str(account_ids[0])
            else:
                filters += ' AND l.account_id IN ' + str(tuple(account_ids))

        if data['partner_ids']:
            partner_ids = data['partner_ids']
            if len(partner_ids) == 1:
                filters += ' AND l.partner_id = ' + str(partner_ids[0])
            else:
                filters += ' AND l.partner_id IN ' + str(tuple(partner_ids))

        if data['analytic_account_ids']:
            analytic_account_ids = data['analytic_account_ids']
            if len(analytic_account_ids) == 1:
                filters += ' AND l.analytic_account_id = ' + str(analytic_account_ids[0])
            else:
                filters += ' AND l.analytic_account_id IN ' + str(tuple(analytic_account_ids))

        if data['include_tax']:
            filters += ' AND l.amount_tax != 0'

        sql = """SELECT l.id as line_id, l.description, l.date, l.amount_untaxed, l.amount_tax, p.name AS petty_cash_name, 
                            rp.name AS responsible_name, aa.name AS account_name FROM petty_cash_line AS l, 
                            petty_cash AS p, res_users AS ru, res_partner as rp, account_account AS aa 
                            where p.id = l.petty_cash_id AND ru.id = p.responsible_id AND rp.id = ru.partner_id 
                            AND aa.id = l.account_id"""

        if data['group_by']:
            res = []
            if data['group_by'] == 'product':
                product_obj = self.env['product.product']
                cr.execute("SELECT product_id FROM petty_cash_line where product_id IS NOT NULL GROUP BY product_id")

                for row in cr.dictfetchall():
                    product_id = row['product_id']
                    filter_group = filters + ' AND l.product_id = ' + str(product_id)
                    cr.execute(sql + filter_group)
                    petty_cash_lines = cr.dictfetchall()

                    # sum total amount untaxed and amount tax
                    sum_amount = self._sum_total_amount(petty_cash_lines)

                    if data['display'] == 'all' or petty_cash_lines:
                        res.append({
                            'group_id': product_obj.browse(product_id).id,
                            'group_name': product_obj.browse(product_id).name,
                            'petty_cash_lines': petty_cash_lines,
                            'group_amount_untaxed': sum_amount['total_amount_untaxed'],
                            'group_amount_tax': sum_amount['total_amount_tax'],
                            'group_total_amount': sum_amount['total_amount']
                        })
            elif data['group_by'] == 'responsible box':
                res_users_obj = self.env['res.users']
                cr.execute("SELECT responsible_id FROM petty_cash GROUP BY responsible_id")

                for row in cr.dictfetchall():
                    responsible_id = row['responsible_id']
                    filter_group = filters + ' AND p.responsible_id = ' + str(responsible_id)
                    cr.execute(sql + filter_group)
                    petty_cash_lines = cr.dictfetchall()

                    # sum total amount untaxed and amount tax
                    sum_amount = self._sum_total_amount(petty_cash_lines)

                    if data['display'] == 'all' or petty_cash_lines:
                        res.append({
                            'group_id': res_users_obj.browse(responsible_id).id,
                            'group_name': res_users_obj.browse(responsible_id).name,
                            'petty_cash_lines': petty_cash_lines,
                            'group_amount_untaxed': sum_amount['total_amount_untaxed'],
                            'group_amount_tax': sum_amount['total_amount_tax'],
                            'group_total_amount': sum_amount['total_amount']
                        })

            elif data['group_by'] == 'account':
                account_obj = self.env['account.account']
                cr.execute("SELECT account_id FROM petty_cash_line GROUP BY account_id")

                for row in cr.dictfetchall():
                    account_id = row['account_id']
                    filter_group = filters + ' AND l.account_id = ' + str(account_id)
                    cr.execute(sql + filter_group)
                    petty_cash_lines = cr.dictfetchall()

                    # sum total amount untaxed and amount tax
                    sum_amount = self._sum_total_amount(petty_cash_lines)

                    if data['display'] == 'all' or petty_cash_lines:
                        res.append({
                            'group_id': account_obj.browse(account_id).id,
                            'group_name': account_obj.browse(account_id).name,
                            'petty_cash_lines': petty_cash_lines,
                            'group_amount_untaxed': sum_amount['total_amount_untaxed'],
                            'group_amount_tax': sum_amount['total_amount_tax'],
                            'group_total_amount': sum_amount['total_amount']
                        })

            elif data['group_by'] == 'analytic_account':
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

                    if data['display'] == 'all' or petty_cash_lines:
                        res.append({
                            'group_id': analytic_account_obj.browse(analytic_account_id).id,
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
    def _get_report_values(self, data=None):
        petty_cash_lines = self.get_petty_cash_lines(data)
        return {
            'data': data,
            'petty_cash_lines': petty_cash_lines,
        }

    @api.model
    def get_lines(self, data, data_id):
        return {}

    @api.model
    def get_html(self, data):
        result = {}
        rcontext = {}
        if data['group_by']:
            template = self.sudo().env.ref('petty_cash.dynamic_report_petty_cash_lines_grouped')
        else:
            template = self.sudo().env.ref('petty_cash.dynamic_report_petty_cash_lines')
        rcontext['currency'] = self._get_currency()
        rcontext['data'] = data
        rcontext['petty_cash_lines'] = self.get_petty_cash_lines(data=data)
        result['html'] = template._render(rcontext)
        return result

    @api.model
    def print_report(self, data):
        result = {
            'ids': [],
            'form': data,
        }
        return result


class DynamicReportRequestFeeding(models.TransientModel):
    _name = 'report.dynamic.request.feeding'
    _description = 'Dynamic report helper model'

    def _get_currency(self):
        return self.env.user.company_id.currency_id.symbol

    @api.model
    def filter_config_responsible(self):
        user_rules = self.env['petty.cash.user.rule'].search([])
        responsible_ids = set()
        for user_rule in user_rules:
            responsible_ids.add(user_rule.user.id)

        return list(responsible_ids)

    def get_feeding_lines(self, data):
        journal_filter = ''
        if isinstance(data['journal_ids'], list) and data['journal_ids']:
            journal_filter = 'AND rf.journal_id in (%s)' % ', '.join(str(i) for i in data['journal_ids'])
        elif data['journal_ids']:
            journal_filter = 'AND rf.journal_id = %s' % data['journal_ids']

        payment_journal_filter = ''
        if isinstance(data['payment_journal_ids'], list) and data['payment_journal_ids']:
            payment_journal_filter = 'AND rf.payment_journal_id in (%s)' % ', '.join(
                str(i) for i in data['payment_journal_ids'])
        elif data['payment_journal_ids']:
            payment_journal_filter = 'AND rf.payment_journal_id = %s' % data['payment_journal_ids']

        account_filter = ''
        if isinstance(data['account_ids'], list) and data['account_ids']:
            account_filter = 'AND rf.account_id in (%s)' % ', '.join(str(i) for i in data['account_ids'])
        elif data['account_ids']:
            account_filter = 'AND rf.account_id = %s' % data['account_ids']

        state_filter = ''
        if data['state']:
            state_filter = "AND state = '%s'" % data['state']

        responsible_filter = ''
        if isinstance(data['responsible_ids'], list) and data['responsible_ids']:
            responsible_filter = 'AND ur.user in (%s)' % ', '.join(str(i) for i in data['responsible_ids'])
        elif data['responsible_ids']:
            responsible_filter = 'AND ur.user = %s' % data['responsible_ids']

        order_by = ''
        if data['group_by']:
            if data['group_by'] == 'journal':
                order_by = 'ORDER BY rf.journal_id'
                group_by = 'journal_id'
            elif data['group_by'] == 'payment_journal':
                order_by = 'ORDER BY rf.payment_journal_id'
                group_by = 'payment_journal_id'
            elif data['group_by'] == 'responsible_box':
                order_by = 'ORDER BY ur.user'
                group_by = 'user'
        cr = self.env.cr
        sql = """
            SELECT rf.name, rf.id, rf.date, rf.journal_id, rf.payment_journal_id,
                rf.amount, rf.actual_amount, rf.state,
                rf.final_current_balance, ur.user
            FROM petty_cash_request_feeding rf
            LEFT JOIN petty_cash_user_rule ur
                ON rf.journal_id = ur.journal_id
            WHERE
                rf.create_date >= '{0}' AND rf.create_date <= '{1}' {2} {3} {4} {5} {6}
            {7}
        """
        cr.execute(sql.format(
            data['date_from'],
            data['date_to'],
            journal_filter,
            payment_journal_filter,
            account_filter,
            responsible_filter,
            state_filter,
            order_by,
        ))
        data_lines = cr.dictfetchall()
        if data['group_by']:
            grouped_data_lines = []
            key_function = lambda x: x[group_by]
            for group_id, lines in itertools.groupby(data_lines, key_function):
                if group_by in ['journal_id', 'payment_journal_id']:
                    group_name = self.env['account.journal'].browse(group_id).name
                elif group_by == 'user':
                    group_name = self.env['res.users'].browse(group_id).name
                list_lines = list(lines)
                totals = {
                    'amount': 0,
                    'actual_amount': 0,
                    'current_balance': 0,
                }
                for line in list_lines:
                    line['journal_name'] = self.env['account.journal'].browse(line['journal_id']).name
                    line['payment_journal_name'] = self.env['account.journal'].browse(line['payment_journal_id']).name
                    line['current_balance'] = self.env['petty.cash.request.feeding'].browse(line['id']).current_balance
                    if line['amount']:
                        totals['amount'] += line['amount']
                    if line['actual_amount']:
                        totals['actual_amount'] += line['actual_amount']
                    if line['state'] in ['approved', 'rejected']:
                        totals['current_balance'] += line['final_current_balance']
                    else:
                        totals['current_balance'] += line['current_balance']
                grouped_data_lines.append(
                    {'group': {
                        'group_name': group_name,
                        'group_id': group_id
                    },
                        'group_total': totals,
                        'group_lines': list_lines
                    }
                )
            return grouped_data_lines
        else:
            for line in data_lines:
                line['journal_name'] = self.env['account.journal'].browse(line['journal_id']).name
                line['payment_journal_name'] = self.env['account.journal'].browse(line['payment_journal_id']).name
                if line['state'] in ['approved', 'rejected']:
                    line['current_balance'] = line['final_current_balance']
                else:
                    line['current_balance'] = self.env['petty.cash.request.feeding'].browse(line['id']).current_balance
            return data_lines

    @api.model
    def get_html(self, data):
        result = {}
        rcontext = {}
        if data['group_by']:
            template = self.sudo().env.ref('petty_cash.dynamic_report_request_feeding_grouped')
        else:
            template = self.sudo().env.ref('petty_cash.dynamic_report_request_feeding')
        rcontext['currency'] = self._get_currency()
        rcontext['data'] = data
        rcontext['feeding_lines'] = self.get_feeding_lines(data)
        result['html'] = template._render(rcontext)
        return result

    @api.model
    def print_report(self, data):
        result = {
            'ids': [],
            'form': data,
        }
        return result
