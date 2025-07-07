from odoo import models, fields, api

class AccountMove(models.Model):
    _inherit = 'account.move'

    invoice_months_count = fields.Integer(
        string='Invoice Months Count',
        help='Number of invoice months extracted from the document',
        default=0
    )
    renting_attachment_ids = fields.Many2many(
        'ir.attachment',
        string='Renting Attachments'
    )

    def action_process_invoice_months(self):
        """Action to process PDF and update months count"""
        self.ensure_one()
        return {
            'name': 'Process Invoice Months',
            'type': 'ir.actions.act_window',
            'res_model': 'pdf.ai.processor',
            'view_mode': 'form',
            'target': 'new',
            'views': [(False, 'form')],
            'context': {
                'default_invoice_id': self.id,
            },
        }
