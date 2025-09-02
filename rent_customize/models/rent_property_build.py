# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError


class RentPropertyBuild(models.Model):
    _inherit = "rent.property.build"

    def sync_ref_analytic_account(self):
        properties = self.env['rent.property'].search([('property_address_build', '=', self.id)])
        for property in properties:
            property.ref_analytic_account = property.get_ref_analytic_account()
            property.analytic_account.write({'code': property.ref_analytic_account})
