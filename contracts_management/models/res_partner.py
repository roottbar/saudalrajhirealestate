# -*- coding: utf-8 -*-
from odoo import models, api, fields


class ResPartner(models.Model):
    _inherit = "res.partner"

    number = fields.Char(string="Number", readonly=True, index=True, copy=False, tracking=True)

    @api.model
    def default_get(self, fields):
        res = super(ResPartner, self).default_get(fields)

        if self._context.get("customer_tender_contract"):
            tender_contract_customer_account_category_id = self.env["ir.config_parameter"].sudo().get_param(
                "contracts_management.tender_contract_customer_account_category_id", False)
            res.update({"partner_account_category_id": tender_contract_customer_account_category_id and eval(
                tender_contract_customer_account_category_id) or False})

        return res

    @api.model
    def create(self, vals):
        auto_sequence_customer = self.env["ir.config_parameter"].sudo().get_param(
            "contracts_management.auto_sequence_customer", False)
        if auto_sequence_customer:
            vals["number"] = self.env["ir.sequence"].next_by_code("tender.customer")

        return super(ResPartner, self).create(vals)
