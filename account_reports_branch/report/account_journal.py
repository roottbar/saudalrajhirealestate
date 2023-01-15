# -*- coding: utf-8 -*-

from odoo import models


class ReportJournal(models.AbstractModel):
    _inherit = "report.account.report_journal"

    def lines(self, target_move, journal_ids, sort_selection, data):
        lines = super(ReportJournal, self).lines(target_move, journal_ids, sort_selection, data)

        if data['form']['branch_ids'] and lines:
            lines = self.env['account.move.line'].search(
                [("id", "in", lines.ids), ("branch_id", "in", data['form']['branch_ids'])])

        return lines
