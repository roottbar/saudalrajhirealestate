# -*- coding: utf-8 -*-

from odoo import fields, models


class TenderContractInvoiceReportWizard(models.TransientModel):
    _name = "tender.contract.invoice.report.wizard"
    _description = "Tender Contract Invoice Report"

    invoice_id = fields.Many2one("account.move", string="Invoice", required=True)

    def print_report(self):
        return self.env.ref("contracts_management.action_report_invoice_tender_contract").report_action(self.invoice_id)
