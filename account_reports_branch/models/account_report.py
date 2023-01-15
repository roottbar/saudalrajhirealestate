# -*- coding: utf-8 -*-

from odoo import models, fields, api, _


class AccountReport(models.AbstractModel):
    _inherit = "account.report"

    filter_branches = True

    @api.model
    def _get_filter_branches(self):
        return self.env["res.branch"].with_context(active_test=False).search(
            [("company_id", "in", self.env.user.company_ids.ids or [self.env.company.id])], order="company_id")

    @api.model
    def _init_filter_branches(self, options, previous_options=None):
        if self.filter_branches is None:
            return

        previous_branches = []
        if previous_options and previous_options.get('branches'):
            for option_branch in previous_options['branches']:
                if option_branch['id'] != "divider" and option_branch["selected"]:
                    previous_branches.append(option_branch["id"])

        options["branches"] = []
        previous_company = False

        for branch in self._get_filter_branches():
            if branch.company_id != previous_company:
                options["branches"].append({"id": "divider", "name": branch.company_id.name})
                previous_company = branch.company_id

            options["branches"].append({
                "id": branch.id,
                "name": branch.name,
                "selected": (branch.id in previous_branches)
            })

    @api.model
    def _get_options_branches(self, options):
        return [branch for branch in options.get('branches', []) if branch["id"] != "divider" and branch['selected']]

    @api.model
    def _get_options_branches_domain(self, options):
        selected_branches = self._get_options_branches(options)
        return selected_branches and [("branch_id", "in", [branch["id"] for branch in selected_branches])] or []

    @api.model
    def _get_options_domain(self, options):
        domain = super(AccountReport, self)._get_options_domain(options)
        domain += self._get_options_branches_domain(options)

        return domain
