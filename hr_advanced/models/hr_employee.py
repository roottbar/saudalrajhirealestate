# -*- coding: utf-8 -*-
import datetime
from datetime import date
from dateutil import relativedelta


from odoo import models, fields, api


class Employee(models.Model):
    _inherit = 'hr.employee'

    age = fields.Integer(string='Age', compute='_compute_employee_age')
    ref = fields.Char(string='Reference', copy=False,compute='_compute_employee_ref')
    id_type = fields.Selection([
        ('national', 'National'),
        ('foreign', 'Foreign')], required=True, string='ID Type', index=True, copy=False,
        tracking=True)

    emp_id = fields.Char(string="ID", copy=False, tracking=True)
    arabic_name = fields.Char(string="Arabic Name", copy=False, tracking=True)
    iqama_no = fields.Char(string="IQAMA NO", copy=False, tracking=True)
    iqama_expiry_date = fields.Date(string="IQAMA Expiry date", copy=False, tracking=True)
    gosi = fields.Integer(string="GOSI", copy=False, tracking=True)
    position_iqama = fields.Char(string="Position - IQAMA", copy=False, tracking=True)
    insurance_class = fields.Char(string="Insurance class", copy=False, tracking=True)
    sponsorship = fields.Selection([
        ('under_guarantee', 'under Sponsorship'),
        ('out_of_guarantee', 'Free Worker')], required=True, string='Sponsorship', index=True, copy=False,
        tracking=True)
    payment_type = fields.Selection([
        ('cash', 'Cash'),
        ('bank', 'Bank')], required=True, string='Payment Type', index=True, copy=False, tracking=True)
    service_year = fields.Char(string="Total Service Years", compute='_compute_total_service', store=True, readonly=True)
    passport_no = fields.Char(string="Passport NO", copy=False, tracking=True)
    passport_expire = fields.Date(string="Passport Expiry Date")

    @api.depends('barcode')
    def _compute_employee_ref(self):
        self.ref = self.barcode

    @api.depends('first_contract_date')
    def _compute_total_service(self):
        for employee in self:
            date = datetime.datetime.now()

            join_date = employee.first_contract_date
            diff = relativedelta.relativedelta(date, join_date)
            years = diff.years
            months = diff.months
            days = diff.days
            total_service = ""
            if years != 0:
                total_service += str(years) + " Years "

            if months != 0:
                total_service += str(months) + " Months "
            if days != 0:
                total_service += str(days + 1) + " Days "
            employee.service_year = years
            # end_service.service_month = months
            # end_service.service_day = days
            #
            # end_service.total_service = total_service
            # employee.total_service_year = float(years + (months / 12))


    @api.model
    def create(self, vals):
        vals['barcode'] = self.env['ir.sequence'].next_by_code('hr.employee')
        return super(Employee, self).create(vals)

    @api.model
    def name_search(self, name='', args=None, operator='ilike', limit=100):
        args = args or []
        domain = ['|', ('name', operator, name), ('ref', operator, name)] + args
        recs = self.search(domain + args, limit=limit)
        return recs.name_get()

    @api.depends('birthday')
    def _compute_employee_age(self):
        age = False
        if self.birthday:
            dob = self.birthday
            today = date.today()
            age = today.year - dob.year - ((today.month, today.day) < (dob.month, dob.day))
        self.age = age
