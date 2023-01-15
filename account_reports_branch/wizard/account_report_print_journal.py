# -*- coding: utf-8 -*-

from odoo import api, fields, models


class AccountPrintJournal(models.TransientModel):
    _inherit = "account.print.journal"

    branch_ids = fields.Many2many("res.branch", string="Branches", domain="[('company_id','=',company_id)]")

    @api.onchange("company_id")
    def _onchange_company_id(self):
        super(AccountPrintJournal, self)._onchange_company_id()
        self.branch_ids = False

    def _print_report(self, data):
        result = super(AccountPrintJournal, self)._print_report(data)
        result["data"]["form"]["branch_ids"] = self.branch_ids.ids
        result["data"]['form']['used_context']["branch_ids"] = self.branch_ids.ids
        return result
