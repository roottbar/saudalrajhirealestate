# -*- coding: utf-8 -*-
from odoo import models, fields


class AccountAsset(models.Model):
    _inherit = 'account.asset'

    plate_no = fields.Char(string="Plate No", copy=False, tracking=True)
    chaises_no = fields.Char(string="Chaises No", copy=False, tracking=True)
    location = fields.Char(string="Location", copy=False, tracking=True)
    project_code = fields.Char(string="Project Code", copy=False, tracking=True)
    employee_id = fields.Many2one('hr.employee', string='Employee', tracking=True,
                                  domain="['|', ('company_id', '=', False), ('company_id', '=', company_id)]")
