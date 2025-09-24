# -*- coding: utf-8 -*-
from io import BytesIO
import base64
import xlwt
from odoo import fields, models, api
from odoo.exceptions import UserError


class PartnerLedgerGenerateReport(models.TransientModel):
    """
        Wizard for viewing the partner's ledger within a specified date range.
        Allows the user to generate the partner ledger report.
    """
    _name = 'partner.ledger.report'
    _description = "Partner Ledger Report"

    start_date = fields.Date(string="From Date", required=True)
    end_date = fields.Date(string="To Date", required=True)
    partner_id = fields.Many2one('res.partner', string="Partner")

    @api.model
    def default_get(self, fields):
        """
              Get Current Record Active id.
        """
        result = super(PartnerLedgerGenerateReport, self).default_get(fields)
        result['partner_id'] = self._context.get('active_id')
        return result

    def generate_template_report(self):
        """
              Generates a PDF report of the partner's ledger for the selected date range.
        """
        self.ensure_one()
        if self.start_date > self.end_date:
            raise UserError(self.env._("The start date must be earlier than the end date."))
        data = {
            'model': 'partner.ledger.report',
            'form_data': {
                'partner_id': self.partner_id.id,
                'start_date': self.start_date,
                'end_date': self.end_date,
            }
        }
        return (self.env.ref('tk_partner_ledger.action_report_partner_ledger').report_action
                (self, data=data))

    def generate_excel_report(self):
        """
        Generates the Partner Ledger Report in Excel format based on the provided
        date range.
        """
        start_date = self.start_date
        end_date = self.end_date

        active_id = self.env.context.get('active_id')
        partners = self.env['res.partner'].browse(active_id)
        company_currency_symbol = self.env.user.company_id.currency_id.symbol

        invoices = self.env['account.move'].search([
            ('partner_id', '=', active_id),
            ('invoice_date', '>=', start_date),
            ('invoice_date', '<=', end_date),
            ('state', '=', 'posted'),
            ('move_type', 'in', ['out_invoice', 'out_refund']),
        ])
        payments = self.env['account.payment'].search([
            ('partner_id', '=', active_id),
            ('date', '>=', start_date),
            ('date', '<=', end_date),
            ('state', '=', 'posted'),
        ])
        workbook = xlwt.Workbook(encoding="UTF-8")
        sheet1 = workbook.add_sheet('Partner Ledger', cell_overwrite_ok=True)

        main_head = xlwt.easyxf('align: horiz center; borders: left thin, right thin, bottom thin;')
        font = xlwt.Font()
        font.bold = True
        font.height = 310
        main_head.font = font

        header_style = xlwt.easyxf('font: bold True; pattern: pattern solid,'
                                   ' fore_colour gray25;align: horiz center;'
                                   ' borders: left thin, right thin, bottom thin, top thin;')
        header_style_amount = xlwt.easyxf('font: bold True;'
                                          'pattern: pattern solid,fore_colour gray25;'
                                          'align: horiz right;borders: left thin,'
                                          'right thin, bottom thin, top thin;')
        data_style = xlwt.easyxf('align: horiz center; borders: left thin,'
                                 ' right thin, bottom thin, top thin;')
        data_style_amount = xlwt.easyxf('align: horiz right;'
                                        'borders: left thin, right thin, bottom thin, top thin;')

        for i in range(11):
            sheet1.col(i).width = 5000

        sheet1.write_merge(0, 1, 1, 4, 'PARTNER LEDGER', main_head)

        sheet1.write(3, 0, 'Name', header_style)
        sheet1.write(4, 0, 'Email', header_style)
        sheet1.write(5, 0, 'Date', header_style)
        sheet1.write(6, 0, 'Currency In', header_style)

        sheet1.write_merge(3, 3, 1, 2, partners.name, data_style)
        sheet1.write_merge(4, 4, 1, 2, partners.email, data_style)
        sheet1.write_merge(5, 5, 1, 2, f"{self.start_date} To {self.end_date}", data_style)
        sheet1.write_merge(6, 6, 1, 2, company_currency_symbol, data_style)

        sheet1.write_merge(8, 8, 0, 2, 'Invoices', header_style)
        sheet1.write(9, 0, 'Name', header_style)
        sheet1.write(9, 1, 'Date', header_style)
        sheet1.write(9, 2, 'Amount', header_style_amount)

        sheet1.write_merge(8, 8, 3, 5, 'Payments', header_style)
        sheet1.write(9, 3, 'Name', header_style)
        sheet1.write(9, 4, 'Date', header_style)
        sheet1.write(9, 5, 'Amount', header_style_amount)

        row = 10

        total_invoice = 0.0
        total_payment = 0.0

        for invoice in invoices:
            if invoices.partner_id:
                sheet1.write(row, 0, invoice.name, data_style)
                sheet1.write(row, 1, invoice.invoice_date.strftime('%d-%m-%Y'), data_style)
                sheet1.write(row, 2, f"{invoice.amount_total:.2f}", data_style_amount)
                total_invoice += invoice.amount_total
                row += 1

        payment_row = 10
        for payment in payments:
            if payment.partner_id:
                sheet1.write(payment_row, 3, payment.name, data_style)
                sheet1.write(payment_row, 4, payment.date.strftime('%d-%m-%Y'), data_style)
                sheet1.write(payment_row, 5, f"{payment.amount:.2f}", data_style_amount)
                total_payment += payment.amount
                payment_row += 1

        sheet1.write_merge(row, row, 0, 1, 'Total Invoice Amount',
                           header_style_amount)
        sheet1.write(row, 2, f"{total_invoice:.2f}", data_style_amount)

        sheet1.write_merge(payment_row, payment_row, 3, 4, 'Total Payment Amount',
                           header_style_amount)
        sheet1.write(payment_row, 5, f"{total_payment:.2f}", data_style_amount)

        sheet1.write_merge(payment_row + 1, payment_row + 1, 3, 4, 'Amount Due',
                           header_style_amount)
        sheet1.write(payment_row + 1, 5, f"{total_invoice - total_payment:.2f}", data_style_amount)

        stream = BytesIO()
        workbook.save(stream)

        filename = f"Partner_Ledger_{partners.name}.xls"
        output = base64.encodebytes(stream.getvalue())
        attachment = self.env['ir.attachment'].sudo()
        attachment_id = attachment.create({
            'name': filename,
            'type': "binary",
            'public': False,
            'datas': output,
        })

        return {
            'type': 'ir.actions.act_url',
            'url': f'/web/content/{attachment_id.id}?download=true',
            'target': 'self',
        }
