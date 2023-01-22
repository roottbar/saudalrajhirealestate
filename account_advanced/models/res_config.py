# -*- coding: utf-8 -*-

from odoo import models, fields


class ResConfigSettings(models.TransientModel):
    _inherit = "res.config.settings"

    module_account_payment_advanced = fields.Boolean(string='Payments Advanced')
    module_journal_entry_report = fields.Boolean(string='Journal Entry Report')
