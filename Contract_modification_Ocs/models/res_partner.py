# -*- coding: utf-8 -*-

from odoo import models, fields, api
from odoo.exceptions import ValidationError
import re


class ResPartner(models.Model):
    _inherit = 'res.partner'

    identity_number = fields.Char(
        string='رقم الهوية/الإقامة',
        size=10,
        required=True,
        help='رقم الهوية أو الإقامة (10 خانات)'
    )

    @api.constrains('identity_number')
    def _check_identity_number(self):
        """التحقق من صحة رقم الهوية/الإقامة"""
        for record in self:
            if record.identity_number:
                # التحقق من أن الرقم يحتوي على 10 خانات فقط
                if not re.match(r'^\d{10}$', record.identity_number):
                    raise ValidationError(
                        'رقم الهوية/الإقامة يجب أن يحتوي على 10 أرقام بالضبط'
                    )
                
                # التحقق من عدم التكرار
                existing = self.search([
                    ('identity_number', '=', record.identity_number),
                    ('id', '!=', record.id)
                ])
                if existing:
                    raise ValidationError(
                        f'رقم الهوية/الإقامة {record.identity_number} مستخدم من قبل {existing[0].name}'
                    )