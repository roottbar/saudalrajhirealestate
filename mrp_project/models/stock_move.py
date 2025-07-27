# -*- coding: utf-8 -*-

from odoo import api, fields, models

class StockMove(models.Model):
    _inherit = 'stock.move'

    project_id = fields.Many2one(
        'project.project',
        string='Project',
        compute='_compute_project_id',
        store=True,
        help="Project related to the manufacturing order"
    )

    @api.depends('raw_material_production_id', 'production_id')
    def _compute_project_id(self):
        for move in self:
            project_id = False
            if move.raw_material_production_id and move.raw_material_production_id.project_id:
                project_id = move.raw_material_production_id.project_id.id
            elif move.production_id and move.production_id.project_id:
                project_id = move.production_id.project_id.id
            move.project_id = project_id

    @api.model
    def create(self, vals):
        move = super(StockMove, self).create(vals)
        move._update_analytic_account()
        return move

    def write(self, vals):
        result = super(StockMove, self).write(vals)
        if any(field in vals for field in ['raw_material_production_id', 'production_id', 'project_id']):
            self._update_analytic_account()
        return result

    def _update_analytic_account(self):
        for move in self:
            if move.project_id and move.project_id.analytic_account_id:
                move.analytic_account_id = move.project_id.analytic_account_id.id
