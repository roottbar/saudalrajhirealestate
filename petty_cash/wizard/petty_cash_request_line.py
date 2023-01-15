# -*- coding: utf-8 -*-

from odoo import fields, models, api, _
from odoo.exceptions import ValidationError


class PettyCashRequestLineWizard(models.TransientModel):
    _name = 'petty.cash.request.line'
    _description = 'Petty Cash Request Line'

    def _get_domain_product(self):
        if self.env.user.has_group('petty_cash.group_petty_cash_manager'):
            products = eval(self.env["ir.config_parameter"].sudo().get_param('products', '[]'))
        else:
            user_rules = self.env['petty.cash.user.rule'].search([('user', '=', self.env.user.id)])
            products = set()

            for user_rule in user_rules:
                products.update(user_rule.products.ids)

        domain = [('id', 'in', list(products))]
        return domain

    def _get_domain_account(self):
        if self.env.user.has_group('petty_cash.group_petty_cash_manager'):
            accounts = eval(self.env["ir.config_parameter"].sudo().get_param('accounts', '[]'))
        else:
            user_rules = self.env['petty.cash.user.rule'].search([('user', '=', self.env.user.id)])
            accounts = set()

            for user_rule in user_rules:
                accounts.update(user_rule.accounts.ids)

        domain = [('id', 'in', list(accounts))]
        return domain

    def _get_domain_petty_cash(self):
        domain = []
        if 'petty_cash_ids' in self._context.keys():
            petty_cash_ids = self._context['petty_cash_ids']

            domain = [('id', 'in', petty_cash_ids)]
        return domain

    petty_cash_id = fields.Many2one('petty.cash', string='Petty Cash', required=True, domain=_get_domain_petty_cash)
    template_type = fields.Selection([
        ('with product', 'With Product'),
        ('without product', 'without product'),
    ], string='Template Type', related='petty_cash_id.template_type')
    account_id = fields.Many2one('account.account', string="Account", required=True, domain=_get_domain_account)
    product_id = fields.Many2one('product.product', string='product', domain=_get_domain_product)

    @api.onchange('product_id')
    def onchange_product(self):
        self.account_id = self.product_id.property_account_expense_id or self.product_id.categ_id.property_account_expense_categ_id

    def create_petty_cash_line(self):
        petty_cash_request_id = self.env['petty.cash.request'].browse(self._context['active_id'])

        if self.petty_cash_id.state == 'closed':
            raise ValidationError(
                _("Petty cash %s is closed , Please select or create new petty cash") % self.petty_cash_id.name)

        vals = {
            'reference': petty_cash_request_id.name,
            'description': petty_cash_request_id.description,
            'date': petty_cash_request_id.date,
            'account_id': self.account_id.id,
            'amount_untaxed': petty_cash_request_id.actual_amount,
            'petty_cash_id': self.petty_cash_id.id,
            'petty_cash_request_id': petty_cash_request_id.id
        }

        if self.template_type == 'with product':
            vals.update({
                'product_id': self.product_id.id,
                'price_unit': petty_cash_request_id.actual_amount,
                'uom_id': self.product_id.uom_po_id.id or self.product_id.uom_id.id,
                'partner_id': petty_cash_request_id.partner_id and petty_cash_request_id.partner_id.id or False
            })

        self.env['petty.cash.line'].create(vals)
        return True
