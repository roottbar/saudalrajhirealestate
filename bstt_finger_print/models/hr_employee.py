# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import UserError


class Employee(models.Model):
    _inherit = 'hr.employee'

    emp_Attendance_code = fields.Char(string="Employee Attendance Code")

    @api.constrains("emp_Attendance_code")
    def emp_Attendance_code_check(self):
        emp_obj = self.env["hr.employee"]
        for rec in self:
            if rec.emp_Attendance_code:
                emp = emp_obj.search_count([('emp_Attendance_code', '=', rec.emp_Attendance_code)])
                if emp > 1:
                    raise UserError(_("There Are more than one employee registerd with the same Attendance employee code for: %s") % rec.emp_Attendance_code)
