from odoo import fields, models


class ResCompany(models.Model):
    _inherit = 'res.company'
    product_id = fields.Many2one('product.product', string='Product',)
    partner_id = fields.Many2one('res.partner', string='Partner')

class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    product_id = fields.Many2one('product.product', string='Product', related='company_id.product_id', readonly=False)
    partner_id = fields.Many2one('res.partner', string='Partner',related="company_id.partner_id", readonly=False)
    notification = fields.Integer(string='')