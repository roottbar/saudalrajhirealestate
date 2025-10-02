# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    accounts = fields.Many2many('account.account', string='Accounts')
    analytic_account_ids = fields.Many2many('account.analytic.account', string='Analytic accounts')
    products = fields.Many2many('product.product', string='products')
    partner_ids = fields.Many2many('res.partner', string='Partners')

    picking_type_id = fields.Many2one('stock.picking.type', 'Operation Type', required=True,
                                      domain="[('code','=','incoming')]",
                                      help="This will determine operation type of incoming shipment")
    template_type = fields.Selection([
        ('with product', 'With Product'),
        ('without product', 'without product'),
    ], string='Template Type', required=True)
    is_stock_move = fields.Boolean("Stock Move")
    dynamic_journal = fields.Boolean("Dynamic Journal")
    transfer_account_id = fields.Many2one('account.account', domain=lambda self: [('reconcile', '=', True), (
        'user_type_id.id', '=', self.sudo().env.ref('account.data_account_type_current_assets').id),
                                                                                  ('deprecated', '=', False)],
                                          string="Inter-Banks Transfer Account")
    petty_cash_vendor_account_category_id = fields.Many2one('res.partner.account.category',
                                                            'Vendor Accounting Category',
                                                            domain=[('apply_to_petty_cash', '=', True)])

    def set_values(self):
        super(ResConfigSettings, self).set_values()

        if self.template_type == 'without product' and self.is_stock_move:
            raise ValidationError(_("Create Stock Move only with product"))

        company = self.env.user.company_id
        company.write({'transfer_account_id': self.transfer_account_id.id})

        config_parameters = self.env["ir.config_parameter"].sudo()

        config_parameters.set_param("picking_type_id", self.picking_type_id.id)
        config_parameters.set_param("petty_cash.petty_cash_vendor_account_category_id",
                                    self.petty_cash_vendor_account_category_id.id)
        config_parameters.set_param("template_type", self.template_type)
        config_parameters.set_param("is_stock_move", self.is_stock_move)
        config_parameters.set_param("petty_cash.dynamic_journal", self.dynamic_journal)

    @api.model
    def get_values(self):
        res = super(ResConfigSettings, self).get_values()

        config_parameters = self.env["ir.config_parameter"].sudo()
        company = self.env.user.company_id

        picking_type_id = config_parameters.get_param('picking_type_id', False)
        petty_cash_vendor_account_category_id = config_parameters.get_param(
            'petty_cash.petty_cash_vendor_account_category_id', False)

        res.update(
            picking_type_id=picking_type_id and eval(picking_type_id) or False,
            petty_cash_vendor_account_category_id=petty_cash_vendor_account_category_id and eval(
                petty_cash_vendor_account_category_id) or False,
            template_type=config_parameters.get_param('template_type'),
            is_stock_move=config_parameters.get_param('is_stock_move'),
            dynamic_journal=config_parameters.get_param('petty_cash.dynamic_journal'),
            transfer_account_id=company.transfer_account_id.id
        )
        return res
