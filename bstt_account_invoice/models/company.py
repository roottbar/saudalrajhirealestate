#!/usr/bin/python
# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import UserError, Warning
import base64
import qrcode
from io import BytesIO


class Company(models.Model):
    _name = "res.company"
    _inherit = "res.company"

    foreign_name = fields.Char(string="Foreign Name", help="Foreign Name")


class ResPartnerBank(models.Model):
    _inherit = 'res.partner.bank'

    swift_code = fields.Char('Swift Code')


class AccountMove(models.Model):
    _inherit = 'account.move'

    l10n_sa_qr_code_str = fields.Char(string='Saudi QR Code String', compute='_compute_l10n_sa_qr_code_str', store=True)
    qr_code = fields.Binary(string='QR Code Image', compute='_compute_qr_code_image')

    @api.depends('company_id.name', 'company_id.vat', 'invoice_date', 'amount_tax', 'amount_total')
    def _compute_l10n_sa_qr_code_str(self):
        """حساب نص QR code للفواتير السعودية"""
        for record in self:
            if record.move_type in ('out_invoice', 'out_refund') and record.company_id and record.invoice_date:
                # تنسيق QR code حسب المعايير السعودية
                qr_data = f"Seller: {record.company_id.name or ''};" 
                qr_data += f"Vat_Number: {record.company_id.vat or ''};" 
                qr_data += f"Date: {record.invoice_date};" 
                qr_data += f"Total_Vat: {record.amount_tax or 0};" 
                qr_data += f"Total_Amount: {record.amount_total or 0}"
                record.l10n_sa_qr_code_str = qr_data
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
        """دالة لإنشاء QR code (للتوافق مع einv_sa)"""
        self._compute_l10n_sa_qr_code_str()
        self._compute_qr_code_image()
        return True
