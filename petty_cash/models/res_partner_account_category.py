# -*- coding: utf-8 -*-
from odoo import models, fields, _
from odoo.exceptions import ValidationError


class ResPartnerAccountCategory(models.Model):
    _inherit = "res.partner.account.category"

    apply_to_petty_cash = fields.Boolean("Apply to Petty Cash", copy=False)

    def unlink(self):
        petty_cash_vendor_account_category_id = self.env["ir.config_parameter"].sudo().get_param(
            'petty_cash.petty_cash_vendor_account_category_id', False)
        config_petty_cash_vendor_account_category_id = petty_cash_vendor_account_category_id and eval(
            petty_cash_vendor_account_category_id) or False

        if config_petty_cash_vendor_account_category_id:
            for partner_account_category in self:
                # check used in configuration petty cash or not
                if partner_account_category.id == config_petty_cash_vendor_account_category_id:
                    raise ValidationError(_(
                        'You cannot delete a partner category %s which is already used in settings' % partner_account_category.name))

        return super(ResPartnerAccountCategory, self).unlink()
