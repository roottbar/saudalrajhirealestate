# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import AccessError, ValidationError


class HrLetter(models.Model):
    _name = 'hr.letter'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = "HR Letter"

    def _get_default_employee_id(self):
        emp_ids = self.env['hr.employee'].search([
            ('user_id', '=', self.env.uid)])
        return emp_ids and emp_ids[0] or False

    name = fields.Char(readonly=1, default='New')
    applied_to = fields.Char(required=True)
    employee_id = fields.Many2one('hr.employee', string='Employee', default=_get_default_employee_id, required=True)
    department_id = fields.Many2one('hr.department', string='Department', related='employee_id.department_id',
                                    readonly=True)
    contract_id = fields.Many2one('hr.contract', string='Contract', related='employee_id.contract_id', readonly=True)
    wage = fields.Monetary(related='employee_id.contract_id.wage', string='Wage', readonly=True)
    company_id = fields.Many2one('res.company', string='Company', readonly=True,
                                 default=lambda self: self.env.company, )
    currency_id = fields.Many2one(string='Currency', related='company_id.currency_id', readonly=True)

    @api.constrains('contract_id')
    def _check_lines(self):
        for rec in self:
            if not rec.contract_id:
                raise ValidationError(_("Sorry You Can't Request Hr Letter, Because you don't have running contract."))

    @api.model
    def create(self, vals):
        vals['name'] = self.env['ir.sequence'].next_by_code('hr.letter')
        return super(HrLetter, self).create(vals)


class HrEmployee(models.Model):
    _inherit = "hr.employee"

    def _compute_employee_letters(self):
        for rec in self:
            rec.hr_letters_count = self.env['hr.letter'].search_count([('employee_id', '=', rec.id)])

    hr_letters_count = fields.Integer(string="Hr Letters Count", compute='_compute_employee_letters')
