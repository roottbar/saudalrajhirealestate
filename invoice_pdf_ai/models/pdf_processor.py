import logging
from odoo import models, fields, api
import PyPDF2
import re
try:
    from pdfminer.high_level import extract_text
except ImportError:
    extract_text = None

_logger = logging.getLogger(__name__)

class PDFProcessor(models.TransientModel):
    _name = 'pdf.ai.processor'
    _description = 'PDF AI Processor'

    pdf_file = fields.Binary(string='Upload PDF File', required=True)
    filename = fields.Char(string='Filename')

    def extract_rent_payments_schedule(self):
        """Extract Rent Payments Schedule table from PDF"""
        pdf_content = self._get_pdf_content()
        if not pdf_content:
            return 0

        # Use AI/ML or regex to find the table (simplified example)
        pattern = r'Rent Payments Schedule(.*?)Total|$'
        matches = re.search(pattern, pdf_content, re.DOTALL | re.IGNORECASE)
        
        if matches:
            table_content = matches.group(1)
            # Count paid invoices (simplified - adjust based on your PDF structure)
            paid_count = len(re.findall(r'paid|مسدد', table_content, re.IGNORECASE))
            return paid_count
        return 0

    def _get_pdf_content(self):
        """Extract text from PDF using different methods"""
        if not self.pdf_file:
            return ""
        
        try:
            # Method 1: Use pdfminer if available
            if extract_text:
                import tempfile
                with tempfile.NamedTemporaryFile(suffix='.pdf') as tmp:
                    tmp.write(self.pdf_file)
                    return extract_text(tmp.name)
            
            # Method 2: Fallback to PyPDF2
            import io
            import PyPDF2
            pdf_file = io.BytesIO(self.pdf_file)
            reader = PyPDF2.PdfFileReader(pdf_file)
            text = ""
            for page in range(reader.numPages):
                text += reader.getPage(page).extractText()
            return text
        except Exception as e:
            _logger.error("Error extracting PDF text: %s", str(e))
            return ""