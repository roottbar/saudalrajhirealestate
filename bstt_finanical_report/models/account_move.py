# -*- coding: utf-8 -*-
import base64

from odoo import api, fields, models, _
from odoo.exceptions import UserError


class AccountMoveLine(models.Model):
    _inherit = 'account.move.line'

    customer_vat = fields.Char(related="partner_id.vat", string="رقم الضريبي للعميل")

    product_id1 = fields.Many2one('product.product', string='وحدة', ondelete='restrict', compute='get_property_data', store=True)

    property_id = fields.Many2one('rent.property', compute='get_property_data', string='عمارة', store=True, index=True)
    property_address_area = fields.Many2one('operating.unit', string='الفرع ', compute='get_property_data', store=True, index=True)
    property_address_build = fields.Many2one('rent.property.build', string='المجمع',
                                             compute='get_property_data', store=True, index=True)
    property_address_city = fields.Many2one('rent.property.city', string='المدينة',
                                            compute='get_property_data', store=True)
    country = fields.Many2one('res.country', string='الدولة', compute='get_property_data', store=True, index=True)

    @api.depends('analytic_distribution')
    def get_property_data(self):
        for r in self:
            r.property_id = False
            r.property_address_area = False
            r.property_address_build = False
            r.property_address_city = False
            r.country = False

            # Get analytic account from analytic_distribution (Odoo 15+ format)
            analytic_account_id = False
            if r.analytic_distribution:
                # analytic_distribution is a JSON field: {account_id: percentage}
                for account_id, percentage in r.analytic_distribution.items():
                    analytic_account_id = int(account_id)
                    break  # Use the first analytic account found

            if analytic_account_id:
                product = self.env['product.product'].search([('analytic_account', '=', analytic_account_id)],limit=1)
                if product.property_id.rent_config_property_type_id:
                    r.product_id1 = product.id
                    r.property_id = product.property_id.id
                    r.property_address_area = product.property_id.property_address_area
                    r.property_address_build = product.property_id.property_address_build
                    r.property_address_city = product.property_id.property_address_city
                    r.country = product.country

