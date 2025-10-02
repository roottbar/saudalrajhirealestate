# -*- coding: utf-8 -*-
import re
from datetime import date
from odoo.tests.common import TransactionCase, tagged


@tagged('test_partner_ledger')
class TestPartnerLedger(TransactionCase):
    """
        Test case for the 'PartnerLedger' model.
        This test suite checks the functionality of the customer ledger process.
    """

    @classmethod
    def setUpClass(cls):
        """
                Set up the test class by creating a partner with an initial approval state of
                'draft'.
        """
        super().setUpClass()
        cls.partner = cls.env['res.partner'].create({
            'name': 'Test Partner',
            'email': 'test.partner@example.com',
        })
        cls.invoice = cls.env['account.move'].create({
            'partner_id': cls.partner.id,
            'move_type': 'out_invoice',
            'invoice_date': date(2025, 1, 1),
            'amount_total': 100.0,
        })
        cls.payment = cls.env['account.payment'].create({
            'partner_id': cls.partner.id,
            'date': date(2025, 1, 15),
            'amount': 50.0,
        })
        cls.wizard = cls.env['partner.ledger.report'].create({
            'partner_id': cls.partner.id,
            'start_date': date(2025, 1, 1),
            'end_date': date(2025, 1, 31),
        })

    def test_generate_pdf_report(self):
        """
        Test if the PDF report generation works as expected.
        """
        pdf_action = self.wizard.generate_template_report()
        self.assertEqual(pdf_action.get('type'), 'ir.actions.report')

    def test_generate_excel_report(self):
        """
        Test if the Excel report generation works as expected.
        """
        excel_action = self.wizard.generate_excel_report()

        self.assertTrue(excel_action.get('type') == 'ir.actions.act_url')
        self.assertIn('/web/content/', excel_action.get('url'))

        pattern = r'/web/content/(\d+)\?download=true'
        match = re.search(pattern, excel_action.get('url'))

        if match:
            extracted_attachment_id = match.group(1)
            self.assertIsNotNone(extracted_attachment_id)
        else:
            self.fail("Attachment ID not found in the URL")

    def test_action_open_wizard_ledger(self):
        """
        Test if the partner's ledger wizard can be opened correctly.
        """
        action = self.partner.action_open_wizard_ledger()
        self.assertEqual(action.get('type'), 'ir.actions.act_window')
        self.assertIn('context', action)
        self.assertEqual(action.get('res_model'), 'partner.ledger.report')
        self.assertEqual(action.get('view_mode'), 'form')
