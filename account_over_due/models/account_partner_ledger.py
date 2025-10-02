# -*- coding: utf-8 -*-

from odoo import models, _


class ReportPartnerLedger(models.AbstractModel):
    _inherit = "account.partner.ledger"

    def _get_report_name(self):
        """
        Override
        Return the name of the report
        """
        return _('Statement of Account')
