# -*- coding: utf-8 -*-

from odoo import fields, models


class StockQuant(models.Model):
    _inherit = "stock.quant"

    branch_id = fields.Many2one(related="location_id.branch_id", string="Branch", readonly=True, store=True)
