# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import fields, models


class SaleReport(models.Model):
    _inherit = "sale.report"

    property_id = fields.Many2one('rent.property', string='عقارات', readonly=True)
    property_state_id = fields.Char(string='حالة العقار')
    property_address_build = fields.Many2one('rent.property.build', string='المجمع')
    property_address_city = fields.Many2one('rent.property.city', string='المدينة')
    country = fields.Many2one('res.country', string='الدولة')

    def _select_additional_fields(self):
        fields_add = super()._select_additional_fields()
        fields_add['property_id'] = "t.property_id"
        fields_add['property_state_id'] = "t.state_id"
        fields_add['property_address_build'] = "t.property_address_build"
        fields_add['property_address_city'] = "t.property_address_city"
        fields_add['country'] = "t.country"
        return fields_add

    def _group_by_sale(self):
        groupby = super()._group_by_sale()
        groupby += ", t.property_id, t.state_id, t.property_address_build, t.property_address_city, t.country"
        return groupby
