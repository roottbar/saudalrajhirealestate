# -*- coding: utf-8 -*-

from odoo import models, fields


class HrEmployee(models.Model):
    _inherit = "hr.employee"

    is_worker = fields.Boolean("Is Worker?", copy=False)

    tender_contracts_count = fields.Integer(compute="_compute_tender_contracts_count", string="Tender Contracts Count")

    def _compute_tender_contracts_count(self):
        tender_contract_obj = self.env["tender.contract"]
        for employee in self:
            employee.tender_contracts_count = tender_contract_obj.search_count([("worker_ids", "in", employee.id)])

    def get_tender_contracts(self):
        action = self.sudo().env.ref("contracts_management.action_tender_contracts", False)
        result = action.read()[0]
        result["domain"] = [("worker_ids", "in", self.id)]
        return result
