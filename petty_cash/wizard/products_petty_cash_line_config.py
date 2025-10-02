# -*- coding: utf-8 -*-

from odoo import fields, models, api, _
from odoo.exceptions import ValidationError


class ProductsPettyCashLineConfigWizard(models.TransientModel):
    _name = 'products.petty.cash.line.config'
    _description = 'Products of Petty Cash Line Config'

    products = fields.Many2many('product.product', string='products', domain="[('purchase_ok','=',True)]")

    @api.model
    def default_get(self, fields):
        res = super(ProductsPettyCashLineConfigWizard, self).default_get(fields)

        products = self.env["ir.config_parameter"].sudo().get_param('products', '[]')

        # check products exists or not
        products = self.env['product.product'].search([('id', 'in', eval(products))])

        res.update({'products': [(6, 0, products.ids)]})

        return res

    def execute(self):
        config_parameters = self.env["ir.config_parameter"].sudo()

        # check if remove products from settings that is already used in petty cash
        products = eval(config_parameters.get_param('products', '[]'))

        if products:
            diff_products = list(set(products) - set(self.products.ids))

            if diff_products:
                petty_cash_lines = self.env['petty.cash.line'].search([('product_id', 'in', diff_products)])

                if petty_cash_lines:
                    raise ValidationError(
                        _("You cannot delete this products from settings,there are already used in petty cash"))

        # update products of petty cash Line in settings
        config_parameters.set_param("products", str(self.products.ids))

        # add account for every product in accounts of settings if not exists
        accounts = eval(config_parameters.get_param('accounts', '[]'))

        for product in self.products:
            property_account_expense_id = product.property_account_expense_id

            if property_account_expense_id:
                if property_account_expense_id.id not in accounts:
                    accounts.append(property_account_expense_id.id)
            else:
                property_account_expense_categ_id = product.categ_id.property_account_expense_categ_id
                if property_account_expense_categ_id and property_account_expense_categ_id.id not in accounts:
                    accounts.append(property_account_expense_categ_id.id)

        # update accounts of petty cash Line in settings
        config_parameters.set_param("accounts", str(accounts))

        return True
