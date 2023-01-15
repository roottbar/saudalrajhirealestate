# -*- coding: utf-8 -*-

import itertools

from odoo import api, models


class ReportRequestsFeeding(models.AbstractModel):
    _name = 'report.petty_cash.report_requests_feeding'

    def _get_currency(self):
        return self.env.user.company_id.currency_id.symbol

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
    def _get_report_values(self, docids, data=None):
        print_responsible = False
        print_accounts = False
        print_journals = False
        print_payments_journals = False

        if data['form']['responsible_ids']:
            print_responsible = ','.join(
                [responsible.name for responsible in
                 self.env['res.users'].search([('id', 'in', data['form']['responsible_ids'])])]
            )
        if data['form']['account_ids']:
            print_accounts = ','.join(
                [account.name for account in
                 self.env['account.account'].search([('id', 'in', data['form']['account_ids'])])]
            )
        if data['form']['journal_ids']:
            print_journals = ','.join(
                [journal.name for journal in
                 self.env['account.journal'].search([('id', 'in', data['form']['journal_ids'])])]
            )
        if data['form']['payment_journal_ids']:
            print_payments_journals = ','.join(
                [payment_journal.name for payment_journal in
                 self.env['account.journal'].search([('id', 'in', data['form']['payment_journal_ids'])])]
            )
        return {
            'data': data['form'],
            'feeding_lines': self.get_feeding_lines(data['form']),
            'currency': self._get_currency(),
            'print_responsible': print_responsible,
            'print_accounts': print_accounts,
            'print_journals': print_journals,
            'print_payments_journals': print_payments_journals,
        }
