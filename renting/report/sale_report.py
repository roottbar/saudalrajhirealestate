# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import fields, models


class SaleReport(models.Model):
    _inherit = "sale.report"

    property_id = fields.Many2one('rent.property', string='عقارات', readonly=True)
    property_state_id = fields.Char(string='حالة العقار')
    property_address_build = fields.Many2one('rent.property.build', string='المجمع')
    property_address_city = fields.Many2one('rent.property.city',string='المدينة')
    country = fields.Many2one('res.country', string='الدولة')

    def _query(self, with_clause='', fields={}, groupby='', from_clause=''):
        fields['property_id'] = ", t.property_id as property_id"
        fields['property_state_id'] = ", t.state_id as property_state_id"
        fields['property_address_build'] = ", t.property_address_build as property_address_build"
        fields['property_address_city'] = ", t.property_address_city as property_address_city"
        fields['country'] = ", t.country as country"
        groupby += ', t.property_id, property_state_id, property_address_build, property_address_city, country'
        return super(SaleReport, self)._query(with_clause, fields, groupby, from_clause)
