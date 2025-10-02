# -*- coding: utf-8 -*-
from odoo import models, fields, _
from odoo.exceptions import ValidationError


class ResPartnerAccountCategory(models.Model):
    _inherit = "res.partner.account.category"

    apply_to_tender_contract = fields.Boolean("Apply to Tender Contract", copy=False)

    def unlink(self):
        tender_contract_customer_account_category_id = self.env["ir.config_parameter"].sudo().get_param(
            "contracts_management.tender_contract_customer_account_category_id", False)
        config_tender_contract_customer_account_category_id = tender_contract_customer_account_category_id and eval(
            tender_contract_customer_account_category_id) or False

        if config_tender_contract_customer_account_category_id:
            for partner_account_category in self:
                # check used in configuration tender projects & contracts or not
                if partner_account_category.id == config_tender_contract_customer_account_category_id:
                    raise ValidationError(_(
                        "You cannot delete a partner category %s which is already used in settings" % partner_account_category.name))

        return super(ResPartnerAccountCategory, self).unlink()
