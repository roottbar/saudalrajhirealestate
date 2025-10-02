# -*- coding: utf-8 -*-

from odoo import models, api


class AccountMoveLine(models.Model):
    _inherit = 'account.move.line'

    @api.model
    def _query_get(self, domain=None):
        tables, where_clause, where_clause_params = super(AccountMoveLine, self)._query_get(domain)
        context = dict(self._context or {})
        
        if context.get("branch_ids", False):
            branch_ids = context.get("branch_ids")
            where_clause += " AND " + (
                    len(branch_ids) == 1 and """("account_move_line"."branch_id" = %s)""" or """("account_move_line"."branch_id" in %s)""")

            where_clause_params += len(branch_ids) == 1 and branch_ids or [tuple(branch_ids)]

        return tables, where_clause, where_clause_params
