import logging
from odoo import models, fields, api, _
from odoo.exceptions import UserError
import io
import PyPDF2
import re

_logger = logging.getLogger(__name__)

class PDFProcessor(models.TransientModel):
    _name = 'pdf.ai.processor'
    _description = 'PDF AI Processor'

    pdf_file = fields.Binary(string='Upload PDF File', required=True)
    filename = fields.Char(string='Filename')
    invoice_id = fields.Many2one('account.move', string='Related Invoice')
    paid_count = fields.Integer(string='Paid Invoices Count', readonly=True)

    def action_process_pdf(self):
        """Main processing method"""
        self.ensure_one()
        if not self.pdf_file:
            raise UserError(_("Please upload a PDF file first."))

        paid_count = self._extract_rent_payments_schedule()
        if paid_count == 0:
            raise UserError(_("No paid invoices found in the schedule or could not parse the PDF."))
        
        # Update both the wizard and the invoice
        self.write({'paid_count': paid_count})
        if self.invoice_id:
            self.invoice_id.write({'paid_invoices_count': paid_count})
        
        return {
            'type': 'ir.actions.act_window',
            'res_model': self._name,
            'res_id': self.id,
            'view_mode': 'form',
            'target': 'new',
            'context': {'show_paid_count': True},
        }

    def _extract_rent_payments_schedule(self):
        """Extract Rent Payments Schedule table from PDF"""
        pdf_content = self._get_pdf_content()
        if not pdf_content:
            return 0

        # Improved regex pattern to find the table
        pattern = r'(Rent\s*Payments\s*Schedule|جدول\s*دفعات\s*الإيجار)(.*?)(Total|المجموع|$)'
        matches = re.search(pattern, pdf_content, re.DOTALL | re.IGNORECASE)
        
        if matches:
            table_content = matches.group(2)
            # Count paid invoices - adjust based on your PDF's actual wording
            paid_count = len(re.findall(r'(paid|مسدد|تم الدفع)', table_content, re.IGNORECASE))
            return paid_count
        return 0

    def _get_pdf_content(self):
        """Extract text from PDF"""
        try:
            pdf_file = io.BytesIO(self.pdf_file)
            reader = PyPDF2.PdfReader(pdf_file)
            text = ""
            for page in reader.pages:
                text += page.extract_text() or ""
            return text
        except Exception as e:
            _logger.error("PDF extraction error: %s", str(e))
            raise UserError(_("Could not read the PDF file. Please make sure it's a valid PDF."))
