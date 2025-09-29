# -*- coding: utf-8 -*-
# Odoo 18.0 Compatible - Updated by roottbar

from odoo import models, fields, api


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    customer_account_category_id = fields.Many2one('res.partner.account.category', 'Customer Accounting Category',
                                                   required=True, domain=[('apply_to_customer', '=', True)])
    vendor_account_category_id = fields.Many2one('res.partner.account.category', 'Vendor Accounting Category',
                                                 required=True, domain=[('apply_to_vendor', '=', True)])

    def set_values(self):
        super(ResConfigSettings, self).set_values()
        config_parameters = self.env["ir.config_parameter"].sudo()

        config_parameters.set_param("accounting_category_partner.customer_account_category_id",
                                    self.customer_account_category_id.id)
        config_parameters.set_param("accounting_category_partner.vendor_account_category_id",
                                    self.vendor_account_category_id.id)

    @api.model
    def get_values(self):
        res = super(ResConfigSettings, self).get_values()
        config_parameters = self.env["ir.config_parameter"].sudo()

        customer_account_category_id = config_parameters.get_param(
            'accounting_category_partner.customer_account_category_id', False)
        vendor_account_category_id = config_parameters.get_param(
            'accounting_category_partner.vendor_account_category_id', False)

        res.update(
            customer_account_category_id=customer_account_category_id and eval(customer_account_category_id) or False,
            vendor_account_category_id=vendor_account_category_id and eval(vendor_account_category_id) or False,
        )
        return res
