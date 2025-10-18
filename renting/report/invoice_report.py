# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import fields, models


class AccountInvoiceReport(models.Model):
    _inherit = 'account.invoice.report'

    property_id = fields.Many2one('rent.property', string='عقارات', readonly=True)
    state_id = fields.Char(string='حالة العقار')
    property_address_build = fields.Many2one('rent.property.build', string='المجمع')
    property_address_city = fields.Many2one('rent.property.city', string='المدينة')
    country = fields.Many2one('res.country', string='الدولة')

    def _select(self):
        return super(AccountInvoiceReport,
                     self)._select() + ", template.property_id as property_id, template.state_id as state_id, template.property_address_build as property_address_build, template.property_address_city as property_address_city, template.country as country "
