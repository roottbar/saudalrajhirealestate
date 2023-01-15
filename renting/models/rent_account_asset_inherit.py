# -*- coding: utf-8 -*-

from odoo import models, fields, api


class AccountAsset(models.Model):
    _inherit = 'account.asset'

    @api.depends('account_analytic_id')
    def get_product(self):
        for r in self:
            product = self.env['product.product'].search([('analytic_account', '=', r.account_analytic_id.id)], limit=1)
            if product:
                r.product_id = product.id
            else:
                r.product_id = False

    product_id = fields.Many2one('product.product', compute='get_product', string='وحدة', store=True, index=True)
    property_id = fields.Many2one('rent.property', related='product_id.property_id', string='عمارة', store=True,
                                  index=True)
    property_address_area = fields.Many2one('operating.unit', string='الفرع ',
                                            related='property_id.property_address_area', store=True, index=True)
    property_address_build = fields.Many2one('rent.property.build', string='المجمع',
                                             related='property_id.property_address_build', store=True, index=True)
    property_address_city = fields.Many2one('rent.property.city', string='المدينة',
                                            related='property_id.property_address_city', store=True)
    country = fields.Many2one('res.country', string='الدولة', related='property_id.country', store=True, index=True)

    @api.onchange('model_id')
    def _onchange_model_id(self):
        model = self.model_id
        if model:
            self.method = model.method
            self.method_number = model.method_number
            self.method_period = model.method_period
            self.method_progress_factor = model.method_progress_factor
            self.prorata = model.prorata
            self.prorata_date = fields.Date.today()
            self.account_analytic_id = model.account_analytic_id.id or self.account_analytic_id.id
            self.analytic_tag_ids = [(6, 0, model.analytic_tag_ids.ids)]
            self.account_depreciation_id = model.account_depreciation_id
            self.account_depreciation_expense_id = model.account_depreciation_expense_id
            self.journal_id = model.journal_id
            self.account_asset_id = model.account_asset_id
