#!/usr/bin/python
# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import UserError, Warning
import base64
import qrcode
from io import BytesIO


class AccountMove(models.Model):
    _name = "account.move"
    _inherit = "account.move"
    einv_amount_sale_total = fields.Monetary(string="Amount sale total", compute="_compute_total", store='True',
                                             help="")
    einv_amount_discount_total = fields.Monetary(string="Amount discount total", compute="_compute_total", store='True',
                                                 help="")
    einv_amount_tax_total = fields.Monetary(string="Amount tax total", compute="_compute_total", store='True', help="")

    # amount_invoiced = fields.Float(string="Amount tax total", help="")
    # qrcode = fields.Char(string="QR", help="")
    l10n_sa_qr_code_str = fields.Char(string='Saudi QR Code String', compute='_compute_l10n_sa_qr_code_str')
    qr_code = fields.Binary(string='QR Code Image', compute='_compute_qr_code_image')

    @api.depends('invoice_line_ids', 'amount_total')
    def _compute_total(self):
        for r in self:
            r.einv_amount_sale_total = r.amount_untaxed + sum(line.einv_amount_discount for line in r.invoice_line_ids)
            r.einv_amount_discount_total = sum(line.einv_amount_discount for line in r.invoice_line_ids)
            r.einv_amount_tax_total = sum(line.einv_amount_tax for line in r.invoice_line_ids)

    def _compute_amount(self):
        res = super(AccountMove, self)._compute_amount()

        # do the things here
        return res

    @api.depends('company_id.name', 'company_id.vat', 'invoice_date', 'amount_tax', 'amount_total')
    def _compute_l10n_sa_qr_code_str(self):
        """حساب سلسلة QR وفق معيار ZATCA باستخدام TLV ثم Base64."""
        def _tlv(tag, value):
            value = value or ''
            vb = value.encode('utf-8')
            return bytes([tag, len(vb)]) + vb

        for record in self:
            if record.move_type in ('out_invoice', 'out_refund') and record.company_id:
                seller = record.company_id.name or ''
                vat = record.company_id.vat or ''
                timestamp = str(fields.Datetime.now())
                total = '{:.2f}'.format(record.amount_total or 0.0)
                vat_total = '{:.2f}'.format(record.amount_tax or 0.0)

                payload = _tlv(1, seller) + _tlv(2, vat) + _tlv(3, timestamp) + _tlv(4, total) + _tlv(5, vat_total)
                record.l10n_sa_qr_code_str = base64.b64encode(payload).decode('utf-8')
            else:
                record.l10n_sa_qr_code_str = False

    @api.depends('l10n_sa_qr_code_str')
    def _compute_qr_code_image(self):
        """إنشاء صورة QR code"""
        for record in self:
            if record.l10n_sa_qr_code_str:
                qr = qrcode.QRCode(version=1, box_size=10, border=5)
                qr.add_data(record.l10n_sa_qr_code_str)
                qr.make(fit=True)
                
                img = qr.make_image(fill_color="black", back_color="white")
                buffer = BytesIO()
                img.save(buffer, format='PNG')
                buffer.seek(0)
                
                record.qr_code = base64.b64encode(buffer.getvalue())
            else:
                record.qr_code = False

    def generate_qr_code(self):
        """دالة لإنشاء QR code (للتوافق مع التقارير)"""
        self._compute_l10n_sa_qr_code_str()
        self._compute_qr_code_image()
        return True




class AccountMoveLine(models.Model):
    _name = "account.move.line"
    _inherit = "account.move.line"
    einv_amount_discount = fields.Monetary(string="Amount discount", compute="_compute_amount_discount", store='True',
                                           help="")
    einv_amount_tax = fields.Monetary(string="Amount tax", compute="_compute_amount_tax", store='True', help="")

    @api.depends('discount', 'quantity', 'price_unit')
    def _compute_amount_discount(self):
        for r in self:
            r.einv_amount_discount = r.quantity * r.price_unit * (r.discount / 100)

    @api.depends('tax_ids', 'discount', 'quantity', 'price_unit')
    def _compute_amount_tax(self):
        for r in self:
            r.einv_amount_tax = sum(r.price_subtotal * (tax.amount / 100) for tax in r.tax_ids)
