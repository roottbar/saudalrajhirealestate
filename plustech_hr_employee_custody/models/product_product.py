from odoo import models, fields, api


class ProductProduct(models.Model):
    _inherit = 'product.product'

    can_be_custody = fields.Boolean(string='Is Custody')
    asset_id = fields.Many2one('account.asset', string='Related Asset',
                               domain=[('linked_product_id', '=', False),
                                       ('asset_type', '=', 'purchase'), ('state', '!=', 'model')])
    status = fields.Selection([('free', 'Free'), ('allocate', 'Allocated')], string='Status', default='free')

    @api.model
    def create(self, values):
        res = super(ProductProduct, self).create(values)
        if values.get('asset_id'):
            asset = self.env['account.asset'].browse(int(values.get('asset_id')))
            asset.write({'linked_product_id': res.id,
                         'custody_ok': True})
        return res

    def write(self, values):
        res = super(ProductProduct, self).write(values)
        if values.get('asset_id'):
            asset = self.env['account.asset'].browse(int(values.get('asset_id')))
            asset.with_context(product=True).write({'linked_product_id': self.id,
                                                    'custody_ok': True})
        return res
