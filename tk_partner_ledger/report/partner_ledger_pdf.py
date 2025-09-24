# -*- coding: utf-8 -*-
from odoo import models, api


class PartnerLedgerAbstract(models.AbstractModel):
    """
        Abstract model for generating partner ledger reports.
    """
    _name = 'report.tk_partner_ledger.report_partner_ledger_pdf'
    _description = 'Partner Ledger Pdf Report'

    @api.model
    def _get_report_values(self, docids, data=None):
        active_id = self.env.context.get('active_id')
        start_date = data.get('form_data').get('start_date')
        end_date = data.get('form_data').get('end_date')
        partner = self.env['res.partner'].browse(active_id)
        company_currency_symbol = self.env.user.company_id.currency_id.symbol

        payments = self.env['account.payment'].search([
            ('partner_id', '=', active_id),
            ('date', '>=', start_date),
            ('date', '<=', end_date),
            ('state', '=', 'posted'),
        ])
        invoices = self.env['account.move'].search([
            ('partner_id', '=', active_id),
            ('invoice_date', '>=', start_date),
            ('invoice_date', '<=', end_date),
            ('state', '=', 'posted'),
            ('move_type', 'in', ['out_invoice', 'out_refund']),
        ])
        combined_data = []
        for invoice, payment in zip(invoices, payments):
            combined_data.append({
                'invoice_name': invoice.name,
                'invoice_date': invoice.invoice_date,
                'invoice_amount': invoice.amount_total,
                'payment_name': payment.name,
                'payment_date': payment.date,
                'payment_amount': payment.amount,
            })
        if len(invoices) > len(payments):
            for invoice in invoices[len(payments):]:
                combined_data.append({
                    'invoice_name': invoice.name,
                    'invoice_date': invoice.invoice_date,
                    'invoice_amount': invoice.amount_total,
                    'payment_name': '',
                    'payment_date': '',
                    'payment_amount': 0.0,
                })
        if len(payments) > len(invoices):
            for payment in payments[len(invoices):]:
                combined_data.append({
                    'invoice_name': '',
                    'invoice_date': '',
                    'invoice_amount': 0.0,
                    'payment_name': payment.name,
                    'payment_date': payment.date,
                    'payment_amount': payment.amount,
                })
        return {
            'doc_ids': docids,
            'combined_data': combined_data,
            'doc_model': 'partner.ledger.report',
            'docs': self.env['partner.ledger.report'].browse(docids),
            'partner': partner,
            'payments': payments,
            'invoices': invoices,
            'currency': company_currency_symbol,
            'from_date': start_date,
            'to_date': end_date,
        }
