# -*- coding: utf-8 -*-

from odoo import models, fields


class ProjectTask(models.Model):
    _inherit = "project.task"

    tender_contract_id = fields.Many2one("tender.contract", string="Contract", domain=[("state", "=", "in progress")],
                                         copy=False)

class account_analytic_line(models.Model):
    _inherit = "account.analytic.line"

    tender_contract_id = fields.Many2one("tender.contract", string="Contract", domain=[("state", "=", "in progress")],
                                         copy=False)


