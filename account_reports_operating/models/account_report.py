# -*- coding: utf-8 -*-

from odoo import models, fields, api, _


class AccountReport(models.AbstractModel):
    _inherit = "account.report"

    filter_operating = True


    @api.model
    def _get_filter_operatings(self):
        return self.env["operating.unit"].with_context(active_test=False).search(
            [("company_id", "in", self.env.user.company_ids.ids or [self.env.company.id])], order="company_id")

    @api.model
    def _init_filter_operatings(self, options, previous_options=None):
        if self.filter_operating is None:
            return

        previous_operatings = []
        if previous_options and previous_options.get('operatings'):
            for option_operating in previous_options['operatings']:
                if option_operating['id'] != "divider" and option_operating["selected"]:
                    previous_operatings.append(option_operating["id"])

        options["operatings"] = []
        previous_company = False

        for operating in self._get_filter_operatings():
            if operating.company_id != previous_company:
                options["operatings"].append({"id": "divider", "name": operating.company_id.name})
                previous_company = operating.company_id

            options["operatings"].append({
                "id": operating.id,
                "name": operating.name,
                "selected": (operating.id in previous_operatings)
            })

    @api.model
    def _get_options_operatings(self, options):
        return [operating for operating in options.get('operatings', []) if operating["id"] != "divider" and operating['selected']]

    @api.model
    def _get_options_operatings_domain(self, options):
        selected_operatings = self._get_options_operatings(options)
        return selected_operatings and [("operating_unit_id", "in", [operating["id"] for operating in selected_operatings])] or []

    @api.model
    def _get_options_domain(self, options):
        domain = super(AccountReport, self)._get_options_domain(options)
        domain += self._get_options_operatings_domain(options)
        return domain


    @api.model
    def _init_filter_operating(self, options, previous_options=None):
        if self.filter_operating is None:
            return

        previous_operatings = []
        if previous_options and previous_options.get('operatings'):
            for option_operating in previous_options['operatings']:
                if option_operating['id'] != "divider" and option_operating["selected"]:
                    previous_operatings.append(option_operating["id"])

        options["operatings"] = []
        previous_company = False

        for operating in self._get_filter_operatings():
            if operating.company_id != previous_company:
                options["operatings"].append({"id": "divider", "name": operating.company_id.name})
                previous_company = operating.company_id

            options["operatings"].append({
                "id": operating.id,
                "name": operating.name,
                "selected": (operating.id in previous_operatings)
            })

    @api.model
    def _get_options_operatings(self, options):
        return [operating for operating in options.get('operatings', []) if operating["id"] != "divider" and operating['selected']]

    @api.model
    def _get_options_operating_domain(self, options):
        selected_operatings = self._get_options_operatings(options)
        return selected_operatings and [("operating_unit_id", "in", [operating["id"] for operating in selected_operatings])] or []

