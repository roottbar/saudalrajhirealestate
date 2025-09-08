# -*- coding: utf-8 -*-

from odoo import models, fields, api


class AccountMoveLine(models.Model):
    _inherit = 'account.move.line'

    # إضافة حقل subscription_id المفقود للتوافق
    subscription_id = fields.Many2one(
        'sale.subscription',
        string='Subscription',
        help='Related subscription for compatibility with existing views'
    )