# -*- coding: utf-8 -*-

from num2words import num2words
from odoo.exceptions import ValidationError
from odoo import api, models, fields, _


class PurchaseOrder(models.Model):
    _inherit = 'purchase.order'

    from_pr = fields.Boolean(string="From PR", readonly=True, copy=False)

