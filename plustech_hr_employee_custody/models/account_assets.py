from odoo import fields, models, api


class AccountAsset(models.Model):
    _inherit = 'account.asset'

    custody_ok = fields.Boolean(string='Can be custody')
    linked_product_id = fields.Many2one('product.product', domain="[('can_be_custody', '=', True),('asset_id', '=', False)]")
    status = fields.Selection([('free', 'Free'), ('allocate', 'Allocated')], string='Status', default='free')
    owner_id = fields.Many2one('hr.employee', string='Owner')
    allocation_date = fields.Date(string='Allocation Date')

    @api.model
    def create(self, values):
        res = super(AccountAsset, self).create(values)
        if values.get('linked_product_id'):
            product = self.env['product.product'].browse(int(values.get('linked_product_id')))
            product.write({'asset_id': res.id})
        return res

    def write(self, values):
        res = super(AccountAsset, self).write(values)
        if values.get('linked_product_id') and not self.env.context.get('product'):
            product = self.env['product.product'].browse(int(values.get('linked_product_id')))
            product.write({'asset_id': self.id})
        return res
