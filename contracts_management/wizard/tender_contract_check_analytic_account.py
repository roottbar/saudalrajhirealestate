# -*- coding: utf-8 -*-

from odoo import fields, models


class TenderContractCheckAnalyticAccountWizard(models.TransientModel):
    _name = "tender.contract.check.analytic.account.wizard"
    _description = "Tender Contract (Check Analytic Account and Tags)"

    assign_analytic = fields.Selection([
        ("assign_analytic_account_tags", "Assign Analytic Account and Tags"),
        ("not_assign_analytic_account_tags", "Not Assign")], required=True, string="Assign Analytic",
        default="assign_analytic_account_tags")

    def action_post_account_moves(self):
        moves = self.env["account.move"].search(
            [("id", "in", self._context["active_ids"]), ("tender_contract_id", "!=", False)])

        if self.assign_analytic == "assign_analytic_account_tags":
            for move in moves:
                tender_contract = move.tender_contract_id
                vals = {
                    "analytic_account_id": tender_contract.analytic_account_id,
                }
                if tender_contract.analytic_tag_ids:
                    vals.update({
                        "analytic_tag_ids": [(4, analytic_tag.id) for analytic_tag in tender_contract.analytic_tag_ids]
                    })
                move.invoice_line_ids.write(vals)

        return moves.with_context(check_assign_analytic_account=True).action_post()

    def action_confirm_sale_orders(self):
        orders = self.env["sale.order"].search([("id", "in", self._context["active_ids"])])

        if self.assign_analytic == "assign_analytic_account_tags":
            sale_orders = orders.filtered(lambda o: o.tender_contract_id)
            for order in sale_orders:
                if order.state not in ["draft", "sent"]:
                    continue
                tender_contract = order.tender_contract_id

                # update analytic account
                if order.analytic_account_id != tender_contract.analytic_account_id:
                    order.write({
                        "analytic_account_id": order.tender_contract_id.analytic_account_id,
                    })
                # check tags and update
                if tender_contract.analytic_tag_ids:
                    order.order_line.write({
                        "analytic_tag_ids": [(4, analytic_tag.id) for analytic_tag in tender_contract.analytic_tag_ids]
                    })

        return orders.with_context(check_assign_analytic_account=True).action_confirm()

    def action_confirm_purchase_orders(self):
        orders = self.env["purchase.order"].search([("id", "in", self._context["active_ids"])])

        if self.assign_analytic == "assign_analytic_account_tags":
            purchase_orders = orders.filtered(lambda o: o.tender_contract_id)
            for order in purchase_orders:
                if order.state not in ["draft", "sent"]:
                    continue
                tender_contract = order.tender_contract_id

                # update analytic account and tags
                vals = {
                    "account_analytic_id": tender_contract.analytic_account_id,
                }
                if tender_contract.analytic_tag_ids:
                    vals.update({
                        "analytic_tag_ids": [(4, analytic_tag.id) for analytic_tag in tender_contract.analytic_tag_ids]
                    })
                order.order_line.write(vals)

        return orders.with_context(check_assign_analytic_account=True).button_confirm()

    def action_validate_stock_picking(self):
        picking = self.env["stock.picking"].search([("id", "=", self._context["active_id"])])

        if self.assign_analytic == "assign_analytic_account_tags":
            picking.write({"apply_assign_analytic": True})
        return picking.with_context(check_assign_analytic_account=True).button_validate()
