# -*- coding: utf-8 -*-

from odoo import models, fields, api

class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'
    
    # إضافة حقل parent_line_id للتوافق مع Odoo 17.0+
    parent_line_id = fields.Many2one(
        'sale.order.line',
        string='Parent Line',
        help='Parent line for subscription or bundle products',
        index=True
    )
    
    # إضافة حقول أخرى قد تكون مطلوبة للتوافق
    child_line_ids = fields.One2many(
        'sale.order.line',
        'parent_line_id',
        string='Child Lines',
        help='Child lines for subscription or bundle products'
    )