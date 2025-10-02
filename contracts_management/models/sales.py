# -*- coding: utf-8 -*-

from odoo import models, fields, api


class SaleOrder(models.Model):
    _inherit = "sale.order"

    tender_contract_id = fields.Many2one("tender.contract", string="Contract", domain=[("state", "=", "in progress")],
                                         copy=False)

    @api.onchange("tender_contract_id")
    def _onchange_tender_contract(self):
        self.analytic_account_id = self.tender_contract_id.analytic_account_id

    def action_confirm(self):
        # check there tender contracts or not
        orders = self.filtered(lambda o: o.tender_contract_id and o.state in ["draft", "sent"])
        if "check_assign_analytic_account" not in self._context.keys() and orders:
            action = self.sudo().env.ref("contracts_management.action_tender_contract_confirm_sale_order", False)
            result = action.read()[0]

            if orders.filtered(lambda o: o.analytic_account_id != o.tender_contract_id.analytic_account_id):
                return result

            for line in orders.filtered(lambda o: o.tender_contract_id.analytic_tag_ids).mapped("order_line"):
                analytic_tag_ids = line.order_id.tender_contract_id.analytic_tag_ids - line.analytic_tag_ids
                if analytic_tag_ids:
                    return result

        return super(SaleOrder, self).action_confirm()

    def _prepare_invoice(self):
        invoice_vals = super(SaleOrder, self)._prepare_invoice()

        if self.tender_contract_id:
            invoice_vals.update({
                "tender_contract_id": self.tender_contract_id.id
            })
        return invoice_vals
