# -*- coding: utf-8 -*-
from odoo import models


class AccountMove(models.Model):
    _inherit = "account.move"

    def print_journal_entry(self):
        # print journal entry report
        return self.env.ref('journal_entry_report.action_report_journal_entry').report_action(self)
