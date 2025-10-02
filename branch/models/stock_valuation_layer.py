# -*- coding: utf-8 -*-

from odoo import fields, models


class StockValuationLayer(models.Model):
    _inherit = "stock.valuation.layer"

    branch_id = fields.Many2one(related="stock_move_id.branch_id", string="Branch", readonly=True, store=True)
