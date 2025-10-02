# -*- coding: utf-8 -*-

from odoo import models, fields, api


class PurchaseOrder(models.Model):
    _inherit = "purchase.order"

    tender_contract_id = fields.Many2one("tender.contract", string="Contract", domain=[("state", "=", "in progress")],
                                         copy=False)

    def button_confirm(self):
        # check there tender contracts or not
        orders = self.filtered(lambda o: o.tender_contract_id and o.state in ["draft", "sent"])

        if "check_assign_analytic_account" not in self._context.keys() and orders:
            action = self.sudo().env.ref("contracts_management.action_tender_contract_confirm_purchase_order", False)
            result = action.read()[0]

            if orders.mapped("order_line").filtered(
                    lambda o: o.account_analytic_id != o.order_id.tender_contract_id.analytic_account_id):
                return result

            for line in orders.mapped("order_line").filtered(lambda o: o.order_id.tender_contract_id.analytic_tag_ids):
                analytic_tag_ids = line.order_id.tender_contract_id.analytic_tag_ids - line.analytic_tag_ids
                if analytic_tag_ids:
                    return result

        return super(PurchaseOrder, self).button_confirm()

    def action_view_invoice(self, invoices=False):
        result = super(PurchaseOrder, self).action_view_invoice(invoices)

        if self.tender_contract_id:
            result["context"]["default_tender_contract_id"] = self.tender_contract_id.id

        return result

    @api.model
    def _prepare_picking(self):
        picking_vals = super(PurchaseOrder, self)._prepare_picking()

        if self.tender_contract_id:
            picking_vals.update({"tender_contract_id": self.tender_contract_id.id})

        return picking_vals
