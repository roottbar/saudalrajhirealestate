# -*- coding: utf-8 -*-
# (c) 2014 Daniel Campos <danielcampos@avanzosc.es>
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

from odoo import models, fields


class StockMove(models.Model):
    _inherit = 'stock.move'

    workorder_id = fields.Many2one(
        comodel_name='mrp.workorder',
        string='Work Order',
        related='workorder_ids.workorder_id',
        store=False
    )
