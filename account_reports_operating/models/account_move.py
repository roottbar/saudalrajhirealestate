# -*- coding: utf-8 -*-

from odoo import models, api


class AccountMoveLine(models.Model):
    _inherit = 'account.move.line'

    @api.model
    def _query_get(self, domain=None):
        tables, where_clause, where_clause_params = super(AccountMoveLine, self)._query_get(domain)
        context = dict(self._context or {})
        
        if context.get("operating_ids", False):
            operating_ids = context.get("operating_ids")
            where_clause += " AND " + (
                    len(operating_ids) == 1 and """("account_move_line"."operating_unit_id" = %s)""" or """("account_move_line"."operating_unit_id" in %s)""")

            where_clause_params += len(operating_ids) == 1 and operating_ids or [tuple(operating_ids)]

        return tables, where_clause, where_clause_params
