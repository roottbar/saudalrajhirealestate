# -*- coding: utf-8 -*-

from odoo import models, fields, api


class ResConfigSettings(models.TransientModel):
    _inherit = "res.config.settings"

    print_analytic_account_journal_entry = fields.Selection(selection=[
        ("full_name", "Full Name"),
        ("name", "Name"),
        ("code", "Code"),
    ], string="Print Analytic Account", copy=False)
    print_reference_journal_entry = fields.Boolean("Print Reference", copy=False)

    def set_values(self):
        super(ResConfigSettings, self).set_values()
        company = self.env.user.company_id
        company.write({
            "print_analytic_account_journal_entry": self.print_analytic_account_journal_entry,
            "print_reference_journal_entry": self.print_reference_journal_entry
        })

    @api.model
    def get_values(self):
        res = super(ResConfigSettings, self).get_values()

        company = self.env.user.company_id
        res.update(
            print_analytic_account_journal_entry=company.print_analytic_account_journal_entry,
            print_reference_journal_entry=company.print_reference_journal_entry
        )
        return res
