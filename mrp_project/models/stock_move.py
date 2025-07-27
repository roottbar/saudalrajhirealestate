# -*- coding: utf-8 -*-
# (c) 2014 Daniel Campos <danielcampos@avanzosc.es>
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

from odoo import models, fields


class StockMove(models.Model):
    _inherit = 'stock.move'

    workorder_id = fields.Many2one(
        comodel_name='mrp.workorder',
        string='Work Order',
        compute='_compute_workorder_id',
        store=False
    )

    def _compute_workorder_id(self):
        for move in self:
            workorder = False
            if move.raw_material_production_id:
                # For raw materials, find the workorder from the production
                workorders = move.raw_material_production_id.workorder_ids
                if workorders:
                    workorder = workorders[0]  # Take the first workorder
            move.workorder_id = workorder
