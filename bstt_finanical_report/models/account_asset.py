# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

import calendar
from dateutil.relativedelta import relativedelta
from math import copysign

from odoo import api, fields, models, _
from odoo.exceptions import UserError
from odoo.tools import float_compare, float_is_zero, float_round


class AccountAsset(models.Model):
    _inherit = 'account.asset'

    # إزالة @api.depends على account_analytic_id لأنه غير موجود
    @api.depends()
    def get_product(self):
        for r in self:
            # التحقق من وجود الحقل قبل استخدامه
            if hasattr(r, 'account_analytic_id') and r.account_analytic_id:
                product = self.env['product.product'].search([('analytic_account', '=', r.account_analytic_id.id)], limit=1)
                r.product_id = product.id if product else False
            else:
                r.product_id = False

    product_id = fields.Many2one('product.product', compute='get_product', string='وحدة', store=True, index=True)
    property_id = fields.Many2one('rent.property', related='product_id.property_id', string='عمارة', store=True, index=True)
    property_address_area = fields.Many2one('operating.unit', string='الفرع ', related='property_id.property_address_area', store=True, index=True)
    property_address_build = fields.Many2one('rent.property.build', string='المجمع',
                                             related='property_id.property_address_build', store=True, index=True)
    property_address_city = fields.Many2one('rent.property.city', string='المدينة',
                                            related='property_id.property_address_city', store=True)
    country = fields.Many2one('res.country', string='الدولة', related='property_id.country', store=True, index=True)
