#!/usr/bin/python
# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import UserError, Warning
import base64
import qrcode
from io import BytesIO
from datetime import datetime, time


class Company(models.Model):
    _name = "res.company"
    _inherit = "res.company"

    foreign_name = fields.Char(string="Foreign Name", help="Foreign Name")


class ResPartnerBank(models.Model):
    _inherit = 'res.partner.bank'

    swift_code = fields.Char('Swift Code')


class AccountMove(models.Model):
    _inherit = 'account.move'

    l10n_sa_qr_code_str = fields.Char(string='Saudi QR Code String', compute='_compute_l10n_sa_qr_code_str')
    qr_code = fields.Binary(string='QR Code Image', compute='_compute_qr_code_image')

    @api.depends('company_id.name', 'company_id.vat', 'invoice_date', 'amount_tax', 'amount_total')
    def _compute_l10n_sa_qr_code_str(self):
        """حساب سلسلة QR وفق معيار ZATCA باستخدام TLV ثم Base64. يدعم مرحلة 2 عند توفر الحقول (69)."""
        def _tlv(tag, value):
            value = value or ''
            vb = value.encode('utf-8')
            return bytes([tag, len(vb)]) + vb

        for record in self:
            if record.move_type in ('out_invoice', 'out_refund') and record.company_id:
                seller = record.company_id.name or ''
                vat = record.company_id.vat or ''
                # وقت الإصدار بصيغة ISO8601 (UTC)
                ts_value = record.invoice_date or record.create_date or fields.Datetime.now()
                if isinstance(ts_value, datetime):
                    ts_dt = ts_value
                else:
                    try:
                        ts_dt = datetime.combine(ts_value, time())
                    except Exception:
                        ts_dt = fields.Datetime.now()
                timestamp = ts_dt.strftime('%Y-%m-%dT%H:%M:%SZ')
                total = '{:.2f}'.format(record.amount_total or 0.0)
                vat_total = '{:.2f}'.format(record.amount_tax or 0.0)

                # حقول مرحلة 2 (TLV 6-9) إن وجدت في النموذج/الوحدات الأخرى
                def _get_optional(field_names):
                    for fname in field_names:
                        if record._fields.get(fname):
                            val = getattr(record, fname, False)
                            if val:
                                return str(val)
                    return ''

                invoice_hash = _get_optional([
                    'invoice_hash', 'zatca_invoice_hash', 'qr_invoice_hash', 'crypto_invoice_hash'
                ])
                ecdsa_signature = _get_optional([
                    'ecdsa_signature', 'zatca_signature', 'qr_signature', 'crypto_stamp_signature'
                ])
                public_key = _get_optional([
                    'public_key', 'zatca_public_key', 'qr_public_key', 'crypto_stamp_public_key'
                ])
                signature_type = _get_optional([
                    'signature_type', 'zatca_signature_type', 'qr_signature_type', 'crypto_stamp_signature_type'
                ])

                payload = (
                    _tlv(1, seller)
                    + _tlv(2, vat)
                    + _tlv(3, timestamp)
                    + _tlv(4, total)
                    + _tlv(5, vat_total)
                )

                if invoice_hash:
                    payload += _tlv(6, invoice_hash)
                if ecdsa_signature:
                    payload += _tlv(7, ecdsa_signature)
                if public_key:
                    payload += _tlv(8, public_key)
                if signature_type:
                    payload += _tlv(9, signature_type)

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
        """دالة لإنشاء QR code (للتوافق مع einv_sa)"""
        self._compute_l10n_sa_qr_code_str()
        self._compute_qr_code_image()
        return True
