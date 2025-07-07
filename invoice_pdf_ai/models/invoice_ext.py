from odoo import models, fields, api

class AccountMove(models.Model):
    _inherit = 'account.move'

    paid_invoices_count = fields.Integer(
        string='Paid Invoices Count',
        help='Number of paid invoices extracted from Rent Payments Schedule PDF'
    )

    def action_process_pdf_schedule(self):
        """Action to process PDF and update paid invoices count"""
        self.ensure_one()
        return {
            'name': 'Process Rent Payments Schedule',
            'type': 'ir.actions.act_window',
            'res_model': 'pdf.ai.processor',
            'view_mode': 'form',
            'target': 'new',
            'context': {'default_invoice_id': self.id},
        }