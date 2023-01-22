# -*- coding: utf-8 -*-

from odoo import models, fields


class ResCompany(models.Model):
    _inherit = "res.company"

    print_analytic_account_journal_entry = fields.Selection(selection=[
        ("full_name", "Full Name"),
        ("name", "Name"),
        ("code", "Code"),
    ], string="Print Analytic Account", copy=False)
    print_reference_journal_entry = fields.Boolean("Print Reference", copy=False)
