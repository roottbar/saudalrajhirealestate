# -*- coding: utf-8 -*-

from odoo import models, fields, api
from dateutil.relativedelta import relativedelta


class HrContract(models.Model):
    _inherit = "hr.contract"

    ref = fields.Char('Reference', readonly=True, copy=False)

    contract_duration = fields.Char(compute='_compute_duration')
    # car_allowance = fields.Float(string="Car Allowance", copy=False, tracking=True, )
    overtime_allowance = fields.Float(string="Overtime", copy=False, tracking=True, )
    transportation_allowance = fields.Float(string="Transportation", copy=False, tracking=True)
    food_allowance = fields.Float(string="Food", copy=False, tracking=True)
    housing_allowance = fields.Float(string="Housing", copy=False, tracking=True)
    mobile_allowance = fields.Float(string="Mobile", copy=False, tracking=True)
    fuel_allowance = fields.Float(string="Fuel", copy=False, tracking=True)
    ticket_allowance = fields.Float(string="Ticket", copy=False, tracking=True)
    commission_allowance = fields.Float(string='Commission', copy=False, tracking=True)
    other_allowance = fields.Float(string='Other', copy=False, tracking=True)

    work_permit_fees_deduction = fields.Float(string="Work Permit Fees", copy=False, tracking=True)
    leave_deduction = fields.Float(string="Leave", copy=False, tracking=True)
    esob_deduction = fields.Float(string="End Of Service (ESOB)", copy=False, tracking=True)
    tax_deduction = fields.Float(string="Taxes", copy=False, tracking=True)
    tax_deduction_amount = fields.Float(string="Taxes Amount", copy=False, tracking=True)

    iqama_fees_deduction = fields.Float(string="IQAMA Fees", copy=False, tracking=True)

    gosi_deduction = fields.Float(string="GOSI", copy=False, tracking=True, compute="_compute_gosi_amount", store=True)
    gosi_type = fields.Selection([
        ('national', 'National'),
        ('foreign', 'Foreign')], required=True, string='GOSI Type', index=True,tracking=True)
    gosi_percent = fields.Float(string="GOSI percent", copy=False, tracking=True, compute='_compute_gosi_percent')

    medical_insurance_deduction = fields.Float(string="Medical Insurance", copy=False, tracking=True)
    medical_insurance_family_deduction = fields.Float(string="Medical Insurance Family", copy=False, tracking=True)
    medical_insurance_type_id = fields.Many2one("hr.medical.insurance.type", string="Medical Insurance Type",
                                                copy=False, tracking=True)
    wage_day = fields.Float(string="Wage(Day)", copy=False, tracking=True , compute='_compute_daily_wage')
    gross_wage = fields.Float(string="Gross", copy=False, tracking=True , compute='_compute_all_total')

    allowance_total= fields.Float(compute='_compute_all_total',store=True)

    travel_from_country = fields.Many2one('res.country', string='من', copy=False, tracking=True)
    travel_to_country = fields.Many2one('res.country', string='الي', copy=False, tracking=True)
    travel_value = fields.Float(string='قيمة مخصص السفر', copy=False, tracking=True)
    travel_type = fields.Selection([
        ('single', 'فردي'),
        ('family', 'عائلي')], string='نوع التذكرة', tracking=True)

    ref_analytic_account = fields.Char(string='رقم اشارة الحساب التحليلي', readonly=True)

    @api.onchange('travel_type','travel_to_country','travel_from_country')
    def _onchange_country(self):
        for rec in self:
            rec.travel_value = 0
            if rec.travel_from_country and rec.travel_to_country:
                travel_value = self.env['hr.travel'].search([('from_country', '=', rec.travel_from_country.id), ('to_country', '=', rec.travel_to_country.id)], limit=1).value
                if rec.travel_type == 'single':
                    rec.travel_value = travel_value
                else:
                    rec.travel_value = ((rec.employee_id.children if rec.employee_id.children <= 3 else 3) + 1) * travel_value

    @api.onchange('department_id')
    def _onchange_department_id(self):
        for rec in self:
            # rec.analytic_account_id = False
            if rec.department_id and rec.ref:
                rec.ref_analytic_account = str(rec.department_id.ref_analytic_account) + '-' + str(rec.ref)

                analytic = self.env['account.analytic.account'].sudo().search([('code', '=', rec.ref_analytic_account)], limit=1)
                if analytic:
                    rec.analytic_account_id = analytic.id
                else:
                    analytic_account_id = self.env['account.analytic.account'].sudo().create(
                        {'name': rec.name, 'group_id': rec.department_id.group_analytic_account.id,
                         'code': rec.ref_analytic_account})
                    rec.analytic_account_id = analytic_account_id.id

    @api.model
    def create(self, vals):
        vals['ref'] = self.env['ir.sequence'].next_by_code('hr.contract')
        res = super(HrContract, self).create(vals)
        res.ref_analytic_account = str(res.department_id.ref_analytic_account) + '-' + str(res.ref)
        analytic_account_id = self.env['account.analytic.account'].sudo().create(
            {'name': res.name, 'group_id': res.department_id.group_analytic_account.id, 'code': res.ref_analytic_account})
        res.analytic_account_id = analytic_account_id.id
        return res

    @api.model
    def name_search(self, name='', args=None, operator='ilike', limit=100):
        args = args or []
        domain = ['|', ('name', operator, name), ('ref', operator, name)] + args
        recs = self.search(domain + args, limit=limit)
        return recs.name_get()

    @api.depends('wage', 'transportation_allowance','food_allowance','housing_allowance',
                 'mobile_allowance','fuel_allowance','ticket_allowance','commission_allowance','other_allowance')
    def _compute_all_total(self):
        for cont in self:
            total= cont.transportation_allowance+cont.food_allowance+cont.housing_allowance+cont.mobile_allowance+cont.fuel_allowance+cont.ticket_allowance+cont.commission_allowance+cont.other_allowance
            cont.allowance_total = total
            cont.gross_wage = total + cont.wage

    @api.depends('gosi_percent', 'wage','housing_allowance')
    def _compute_gosi_amount(self):
        for contract in self:
            gosi_deduction = 0.0
            if contract.gosi_percent and contract.wage:
                gosi_deduction = (contract.wage + contract.housing_allowance)* contract.gosi_percent
            contract.gosi_deduction = gosi_deduction

    @api.onchange('tax_deduction', 'wage')
    def _onchange_tax_deduction_amount(self):
        for contract in self:
            tax_amount = 0.0
            if contract.tax_deduction and contract.wage:
                tax_amount = contract.wage * contract.tax_deduction
            contract.tax_deduction_amount = tax_amount

    @api.onchange('medical_insurance_type_id')
    def _onchange_medical_insurance_amount(self):
        self.medical_insurance_deduction = self.medical_insurance_type_id and self.medical_insurance_type_id.amount or 0.0

    @api.depends('date_start', 'date_end')
    def _compute_duration(self):
        for contract in self:
            difference_in_years = relativedelta(contract.date_end, contract.date_start).years
            difference_in_months = relativedelta(contract.date_end, contract.date_start).months
            difference_in_days = relativedelta(contract.date_end, contract.date_start).days

            self.contract_duration = str(difference_in_years)+ " Year/s " + " | or | " + str(difference_in_months) + " Months " + " | or | "  + str(difference_in_days)+ " Days"

    @api.depends('wage')
    def _compute_daily_wage(self):
        for contract in self:
            contract.wage_day = float(contract.wage/30)

    @api.depends('gosi_type')
    def _compute_gosi_percent(self):

        for contract in self:
            if contract.gosi_type=='national':
                contract.gosi_percent=22/100
            else :
                contract.gosi_percent=2/100
