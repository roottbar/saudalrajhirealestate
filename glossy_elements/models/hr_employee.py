# -*- coding: utf-8 -*-
from datetime import datetime
from time import strftime

from odoo import models, fields, api


class HrEmployee(models.Model):
    _inherit = 'hr.employee'

    element_line_ids = fields.One2many(comodel_name='employee.element.line',inverse_name='employee_id')

    @api.model
    def _generate_monthly_elements_entry(self):
        employees = self.env['hr.employee'].search([])
        for employee in employees:
            employee.generate_monthly_elements_entry()

    def generate_monthly_elements_entry(self):

        for emp in self:
            if emp.contract_id:
                for element in self.element_line_ids:
                    jrl_entry = self.env['account.move']
                    if element.recurring=='month' :
                        jrl_entry.create({
                            # 'type': 'entry',
                            'date': datetime.now(),
                            'ref':"Monthly ELEMENTSEntry in ",
                            'journal_id':element.journal_id.id,
                            'auto_post': True,
                            'line_ids': [
                                (0, 0, {
                                    'name': 'line_debit',
                                    'debit': element.monthly_amount,
                                    'partner_id': element.employee_id.address_home_id.id,
                                    'account_id': element.debit_account_id.id,
                                }),
                                (0, 0, {
                                    'credit': element.monthly_amount,
                                    'partner_id': emp.address_home_id.id,
                                    'account_id': element.credit_account_id.id,
                                }),
                            ],
                        })






class HrEmployeeElement(models.Model):
    _name = 'employee.element.line'
    element_id = fields.Many2one('element.element')
    type = fields.Selection(related='element_id.type')
    recurring = fields.Selection(related='element_id.recurring',store=True)
    annual_amount = fields.Float(related='element_id.annual_amount')
    monthly_amount = fields.Float(related='element_id.monthly_amount',store=True,readonly=False)
    journal_id = fields.Many2one('account.journal',related='element_id.journal_id')
    debit_account_id = fields.Many2one('account.account',related='element_id.debit_account_id')
    credit_account_id = fields.Many2one('account.account',related='element_id.credit_account_id')
    employee_id = fields.Many2one('hr.employee')
    is_eos_element = fields.Boolean(string='Eos Element', related='element_id.is_eos_element')

    state = fields.Selection([('draft','Draft'),('generate','Generated')])


    #     value = fields.Integer()
    #     value2 = fields.Float(compute="_value_pc", store=True)
    #     description = fields.Text()
    #
    @api.depends('annual_amount','employee_id')
    def _get_monthly_amount(self):
        for record in self:

            record.monthly_amount = float(record.annual_amount) / 12



