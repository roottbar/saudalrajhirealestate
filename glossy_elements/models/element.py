# -*- coding: utf-8 -*-

from odoo import models, fields, api


class Element(models.Model):
    _name = 'element.element'
    _description = 'Glossy path Element'

    name = fields.Char()
    type = fields.Selection([('prepaid','Prepaid'),('accrued','Accrued')])
    recurring = fields.Selection([('month','Monthly'),('year','Yearly')])
    annual_amount = fields.Float()
    monthly_amount = fields.Float(compute="_get_monthly_amount")
    journal_id = fields.Many2one('account.journal')
    debit_account_id = fields.Many2one('account.account')
    credit_account_id = fields.Many2one('account.account')
    element_type = fields.Selection([('eos','End of Service'),('ticket','Air Ticket'),('medical','Medical Insurance')],)
    is_eos_element = fields.Boolean()


    notes = fields.Text()


#     value = fields.Integer()
#     value2 = fields.Float(compute="_value_pc", store=True)
#     description = fields.Text()
#
    @api.depends('annual_amount')
    def _get_monthly_amount(self):
        for record in self:
            record.monthly_amount = float(record.annual_amount) / 12


