# -*- coding: utf-8 -*-
from odoo import fields, models, api


class ResUsers(models.Model):
    _inherit = 'res.users'

    allowed_warehouses = fields.Many2many('stock.warehouse', string='Allowed Warehouses',
                                          help='Allowed Warehouses for this user')
    all_warehouses = fields.Boolean(string="All Warehouses")

    @api.model
    def create(self, vals):
        self.clear_caches()
        return super(ResUsers, self).create(vals)

    def write(self, vals):
        # for clearing out existing values and update with new values
        self.clear_caches()
        return super(ResUsers, self).write(vals)
