# -*- coding: utf-8 -*-

import json
from datetime import timedelta

from babel.dates import format_datetime, format_date
from odoo import models, fields, _
from odoo.tools import DEFAULT_SERVER_DATE_FORMAT as DF
from odoo.tools.misc import get_lang


class PettyCashUserRule(models.Model):
    _inherit = "petty.cash.user.rule"

    kanban_dashboard = fields.Text(compute='_kanban_dashboard')
    kanban_dashboard_graph = fields.Text(compute='_kanban_dashboard_graph')
    color = fields.Integer("Color Index", default=1)

    def _kanban_dashboard(self):
        for user_rule in self:
            user_rule.kanban_dashboard = json.dumps(user_rule.get_petty_cash_dashboard_datas())

    def _kanban_dashboard_graph(self):
        for user_rule in self:
            user_rule.kanban_dashboard_graph = json.dumps(user_rule.get_bar_graph_datas())

    def get_bar_graph_datas(self):
        data = []
        today = fields.Datetime.now(self)
        data.append({'label': _('Due'), 'value': 0.0, 'type': 'past'})
        day_of_week = int(format_datetime(today, 'e', locale=get_lang(self.env).code))
        first_day_of_week = today + timedelta(days=-day_of_week + 1)
        for i in range(-1, 4):
            if i == 0:
                label = _('This Week')
            elif i == 3:
                label = _('Not Due')
            else:
                start_week = first_day_of_week + timedelta(days=i * 7)
                end_week = start_week + timedelta(days=6)
                if start_week.month == end_week.month:
                    label = str(start_week.day) + '-' + str(end_week.day) + ' ' + format_date(end_week, 'MMM',
                                                                                              locale=get_lang(
                                                                                                  self.env).code)
                else:
                    label = format_date(start_week, 'd MMM', locale=get_lang(self.env).code) + '-' + format_date(
                        end_week, 'd MMM', locale=get_lang(self.env).code)
            data.append({'label': label, 'value': 0.0, 'type': 'past' if i < 0 else 'future'})

        # Build SQL query to find amount aggregated by week
        (select_sql_clause, query_args) = self._get_bar_graph_select_query()
        query = ''
        start_date = (first_day_of_week + timedelta(days=-7))
        for i in range(0, 6):
            if i == 0:
                query += "(" + select_sql_clause + " and start_date < '" + start_date.strftime(DF) + "')"
            elif i == 5:
                query += " UNION ALL (" + select_sql_clause + " and start_date >= '" + start_date.strftime(DF) + "')"
            else:
                next_date = start_date + timedelta(days=7)
                query += " UNION ALL (" + select_sql_clause + " and start_date >= '" + start_date.strftime(
                    DF) + "' and start_date < '" + next_date.strftime(DF) + "')"
                start_date = next_date

        self.env.cr.execute(query, query_args)
        query_results = self.env.cr.dictfetchall()

        for index in range(0, len(query_results)):
            if query_results[index].get('aggr_date') != None:
                data[index]['value'] = query_results[index].get('total')

        return [{'values': data, 'title': '', 'key': _('Petty Cash: Untaxed Total')}]

    def get_petty_cash_dashboard_datas(self):
        # get petty cash in progress
        (query, query_args) = self._get_in_progress_petty_cash_query()
        self.env.cr.execute(query, query_args)
        results_to_in_progress = self.env.cr.dictfetchall()
        (number_in_progress, sum_in_progress) = self._count_results_and_sum_amounts(results_to_in_progress)

        # get review petty cash
        (query, query_args) = self._get_review_petty_cash_query()
        self.env.cr.execute(query, query_args)
        results_to_review = self.env.cr.dictfetchall()
        (number_review, sum_review) = self._count_results_and_sum_amounts(results_to_review)

        # get close petty cash
        (query, query_args) = self._get_close_petty_cash_query()
        self.env.cr.execute(query, query_args)
        results_to_close = self.env.cr.dictfetchall()
        (number_close, sum_close) = self._count_results_and_sum_amounts(results_to_close)

        # get current balance
        (query, query_args) = self._get_current_balance_user_query()
        self.env.cr.execute(query, query_args)
        ml_data = self.env.cr.dictfetchall()

        current_balance = ml_data and ml_data[0].get('current_balance') or 0
        expected_balance = current_balance - (sum_review + sum_in_progress)

        return {
            'sum_in_progress': round(sum_in_progress, 2),
            'number_in_progress': number_in_progress,
            'sum_review': round(sum_review, 2),
            'number_review': number_review,
            'sum_close': round(sum_close, 2),
            'number_close': number_close,
            'current_balance': round(current_balance, 2),
            'expected_balance': round(expected_balance, 2)
        }

    def _get_in_progress_petty_cash_query(self):
        return ("""SELECT state, amount_total FROM petty_cash
                          WHERE user_rule = %(user_rule)s AND state = 'in progress';""", {'user_rule': self.id})

    def _get_review_petty_cash_query(self):
        return ("""SELECT state, amount_total FROM petty_cash
                          WHERE user_rule = %(user_rule)s AND state = 'review';""", {'user_rule': self.id})

    def _get_close_petty_cash_query(self):
        return ("""SELECT state, amount_total FROM petty_cash
                          WHERE user_rule = %(user_rule)s AND state = 'closed';""", {'user_rule': self.id})

    def _get_current_balance_user_query(self):
        return ("""SELECT sum(debit - credit) AS current_balance FROM account_move_line
                                  WHERE journal_id = %(journal_id)s AND account_id = %(account_id)s;""",
                {'journal_id': self.journal_id.id, 'account_id': self.account_id.id})

    def _count_results_and_sum_amounts(self, results_dict):
        count = 0
        sum = 0.0

        for result in results_dict:
            count += 1
            sum += result.get('amount_total')

        return (count, sum)

    def _get_bar_graph_select_query(self):
        return ("""SELECT sum(amount_total) as total, min(start_date) as aggr_date FROM petty_cash
                    WHERE user_rule = %(user_rule)s""", {'user_rule': self.id})

    def open_action(self):
        # return action based on state and user rule
        action = self.sudo().env.ref('petty_cash.action_petty_cash', False)
        result = action.read()[0]
        result['domain'] = [('user_rule', '=', self.id)]

        return result

    def create_cash_statement(self):
        ctx = self._context.copy()
        ctx.update({'default_responsible_id': self.env.user.id})
        return {
            'name': _('Create Petty Cash'),
            'type': 'ir.actions.act_window',
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'petty.cash',
            'context': ctx,
        }
