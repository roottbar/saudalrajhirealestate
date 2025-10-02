#!/usr/bin/python
# -*- coding: utf-8 -*-

from odoo import models, fields, api, _


class AccountMove(models.Model):
    _inherit = 'account.move'

    def remove_analytic_account(self, move_id):
        self.remove_analytic_account_from_date(move_id)

    def remove_analytic_account_from_date(self, move_id):
        print(move_id)
        move_lines = self.env['account.move.line'].search([('move_id', 'in', move_id.ids)]).filtered(
            lambda l: l.analytic_account_id)
        # xx = moves.line_ids.filtered(lambda l: l.analytic_account_id)
        print('Move IDDS', move_lines.ids)

        if len(move_lines) > 1:
            query = """UPDATE account_move_line 
            SET analytic_account_id = null 
            WHERE id IN {move_ids}""".format(
                move_ids=tuple(move_lines.ids))
            self.env.cr.execute(query)

            # remove analytic lines form account move line
            query = """DELETE FROM account_analytic_line 
                WHERE move_id IN {move_ids}""".format(
                move_ids=tuple(move_lines.ids))
            print(query)
            self.env.cr.execute(query)
        elif move_lines:
            query = """UPDATE account_move_line 
                        SET analytic_account_id = null 
                        WHERE id = {move_ids}""".format(
                move_ids=move_lines.id)
            print(query)
            self.env.cr.execute(query)

            # remove analytic lines form account move line
            query = """DELETE FROM account_analytic_line 
                            WHERE move_id = {move_ids}""".format(
                move_ids=move_lines.id)
            self.env.cr.execute(query)
