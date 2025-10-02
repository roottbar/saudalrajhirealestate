# -*- coding: utf-8 -*-
from odoo import models, fields, api


class Picking(models.Model):
    _inherit = "stock.picking"

    petty_cash_id = fields.Many2one('petty.cash', string='Petty Cash')
