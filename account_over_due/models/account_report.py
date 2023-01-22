# -*- coding: utf-8 -*-

from odoo import api, models


class AccountReport(models.AbstractModel):
    _inherit = 'account.report'

    @api.model
    def _format_aml_name(self, line_name, move_ref, move_name):
        super(AccountReport, self)._format_aml_name(line_name, move_ref, move_name)
        names = []
        if move_name and move_name != '/':
            names.append(move_name)
        res = '-'.join(names)
        return res




    def get_pdf(self, options):
        return super(AccountReport, self.sudo()).get_pdf(options, minimal_layout=False)
