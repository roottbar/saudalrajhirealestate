# -*- coding: utf-8 -*-
from odoo import models, fields, api


class AccountMove(models.Model):
    _inherit = "account.move"

    tender_contract_id = fields.Many2one("tender.contract", string="Contract", domain=[("state", "=", "in progress")],
                                         copy=False)

    @api.onchange("partner_id")
    def _onchange_partner(self):
        domain = [("state", "=", "in progress")]
        if self.partner_id:
            domain += [("partner_id", "=", self.partner_id.id)]

        return {"domain": {"tender_contract_id": domain}}

    def action_post(self):
        # check there tender contracts or not
        moves = self.filtered(lambda m: m.tender_contract_id)

        if "check_assign_analytic_account" not in self._context.keys() and moves:
            action = self.sudo().env.ref("contracts_management.action_tender_contract_validate_account_move", False)
            result = action.read()[0]

            if moves.mapped("invoice_line_ids").filtered(
                    lambda l: l.analytic_account_id != l.tender_contract_id.analytic_account_id):
                return result

            for line in moves.filtered(lambda m: m.tender_contract_id.analytic_tag_ids).mapped("invoice_line_ids"):
                analytic_tag_ids = line.tender_contract_id.analytic_tag_ids - line.analytic_tag_ids
                if analytic_tag_ids:
                    return result

        return super(AccountMove, self).action_post()


class AccountMoveLine(models.Model):
    _inherit = "account.move.line"

    tender_contract_id = fields.Many2one(related="move_id.tender_contract_id", string="Contract", store=True,
                                         readonly=True)
    tender_project_id = fields.Many2one(related="tender_contract_id.tender_project_id", string="Project", store=True,
                                        readonly=True)
    service_type_id = fields.Many2one("tender.service.type", string="Service Type", copy=False)
    service_category_id = fields.Many2one(related="service_type_id.service_category_id", string="Service Category",
                                          store=True, readonly=True)
    parent_service_category_id = fields.Many2one(related="service_category_id.parent_id",
                                                 string="Parent Service Category", store=True, readonly=True)
    branch_id = fields.Many2one("tender.branch", string="Branch", copy=False)
