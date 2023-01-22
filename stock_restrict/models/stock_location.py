from odoo import fields, models, api


class StockLocation(models.Model):
    _inherit = 'stock.location'

    warehouse_id = fields.Many2one('stock.warehouse', string="Warehouse", compute='_compute_warehouse', store=True)

    @api.depends('location_id')
    def _compute_warehouse(self):
        for location in self:
            location.warehouse_id = location.location_id.get_warehouse().id



    @api.returns('stock.warehouse', lambda value: value.id)
    def get_warehouse(self):
        """ Returns warehouse id of warehouse that contains location """
        domain = [('view_location_id', 'parent_of', self.ids)]
        return self.env['stock.warehouse'].search(domain, limit=1)
