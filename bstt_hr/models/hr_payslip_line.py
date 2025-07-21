# -*- coding: utf-8 -*-
from odoo import api, fields, models


class HrPayslipLine(models.Model):
    _inherit = 'hr.payslip.line'

    partner_id = fields.Many2one('res.partner', related=False, compute="_compute_partner_id", store=True)

    @api.depends('salary_rule_id', 'employee_id')
    def _compute_partner_id(self):
        for line in self:
            employee = line.employee_id
            partner = False

            # محاولة الحصول على عنوان الموظف
            address = getattr(employee, 'private_address_id', False)

            if not address:
                address = self.env['res.partner'].create({
                    'name': employee.name,
                    'street': getattr(employee, 'address', False) or '',
                })
                if hasattr(employee, 'private_address_id'):
                    employee.private_address_id = address.id

            partner = line.salary_rule_id.partner_id or address
            line.partner_id = partner.id if partner else False
