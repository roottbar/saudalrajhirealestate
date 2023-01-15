# -*- coding: utf-8 -*-

from odoo import api, models, fields, _
from odoo.exceptions import ValidationError


class ProductCategory(models.Model):
    _inherit = 'product.category'

    is_it = fields.Boolean(string="IT", copy=False)
    pr_product = fields.Boolean(string="PR Product", copy=False)

    @api.constrains('is_it')
    def _check_is_it(self):
        for category in self.filtered(lambda c: c.is_it):
            category_it = self.search([("id", "!=", category.id), ("is_it", "=", True)])
            if category_it:
                raise ValidationError(
                    _("Category %s is IT, You can not create more than one IT category  " % category_it.name))

    @api.constrains('pr_product')
    def _check_pr_product(self):
        for category in self.filtered(lambda c: c.pr_product):
            category_pr = self.search([("id", "!=", category.id), ("pr_product", "=", True)])
            if category_pr:
                raise ValidationError(
                    _("Category %s is  PR Product , You can not create more than one PR Product category  " % category_pr.name))
