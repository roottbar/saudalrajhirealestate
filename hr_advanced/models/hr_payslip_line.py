# -*- coding: utf-8 -*-
from odoo import api, fields, models


class HrPayslipLine(models.Model):
    _inherit = 'hr.payslip.line'

    partner_id = fields.Many2one(related=False, compute="_compute_partner_id")

    @api.depends('salary_rule_id', 'employee_id')
    def _compute_partner_id(self):
        for line in self:
            partner = line.salary_rule_id.partner_id.id or line.employee_id.user_id.partner_id.id or False
            line.partner_id = partner
