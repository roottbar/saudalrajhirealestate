# -*- coding: utf-8 -*-

from odoo import api, fields, models


class AccountPrintJournal(models.TransientModel):
    _inherit = "account.print.journal"

    operating_ids = fields.Many2many("operating.unit", string="operatings", domain="[('company_id','=',company_id)]")

    @api.onchange("company_id")
    def _onchange_company_id(self):
        super(AccountPrintJournal, self)._onchange_company_id()
        self.operating_ids = False

    def _print_report(self, data):
        result = super(AccountPrintJournal, self)._print_report(data)
        result["data"]["form"]["operating_ids"] = self.operating_ids.ids
        result["data"]['form']['used_context']["operating_ids"] = self.operating_ids.ids
        return result
