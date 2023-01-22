# -*- coding: utf-8 -*-

from odoo import models, api, _


class AccountReport(models.AbstractModel):
    _inherit = "account.report"

    filter_level1 = None
    filter_level2 = None
    filter_level3 = None

    def get_unfolded_levels(self,options):
        unfolded_levels = []
        if options.get('level1'):
            unfolded_levels.append(1)
        if options.get('level2'):
            unfolded_levels.append(2)
        if options.get('level3'):
            unfolded_levels.append(3)
        return unfolded_levels

    def _create_hierarchy(self, lines, options):
        lines = super(AccountReport, self)._create_hierarchy(lines, options)
        unfolded_levels = self.get_unfolded_levels(options)
        if not options.get('unfold_all'):
            for line in lines:
                line['unfolded'] = True if line['level'] in unfolded_levels else False
        return lines


class AccountChartOfAccountReport(models.AbstractModel):
    _inherit = "account.coa.report"

    filter_level1 = False
    filter_level2 = False
    filter_level3 = False
