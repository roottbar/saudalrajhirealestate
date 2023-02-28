from odoo import fields, models


class ResCompany(models.Model):
    _inherit = 'res.company'
    product_id = fields.Many2one('product.product', string='Product',)
    partner_id = fields.Many2one('res.partner', string='Partner')
    legal_notify_user_ids = fields.Many2many(comodel_name='res.users',relation="legal_notify_rel", string='Notify Users')


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    product_id = fields.Many2one('product.product', string='Product', related='company_id.product_id', readonly=False)
    partner_id = fields.Many2one('res.partner', string='Partner',related="company_id.partner_id", readonly=False)
    notification = fields.Integer(string='')

    legal_upcoming_days = fields.Integer(config_parameter='notify_upcoming_and_overdue.legal_upcoming_days')
    legal_over_days = fields.Integer(config_parameter='notify_upcoming_and_overdue.legal_over_days')
    legal_send_user_notify = fields.Boolean(config_parameter='notify_upcoming_and_overdue.legal_send_user_notify')
    legal_notify_user_ids = fields.Many2many(string="Notify Users", related='company_id.legal_notify_user_ids', readonly=False)
