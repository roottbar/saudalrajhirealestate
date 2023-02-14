# -*- coding: utf-8 -*-
####################################
# Author: Bashier Elbashier
# Date: 27th February, 2021
####################################

from odoo import models, fields, api, _
from odoo.exceptions import UserError


class HREmployee(models.Model):
    _inherit = "hr.employee"

    biometric_device_id = fields.Integer("Attendance Device ID")
    attendance_device_id = fields.Char(string='Attendance Device ID')
    # biometric_device_name = fields.Char(string='Attendance Device Name')

    @api.constrains('attendance_device_id')
    def check_device_id_uniqueness(self):
        emps_with_id = self.search([('attendance_device_id', '=', self.attendance_device_id)])
        if len(emps_with_id) > 1 and self.attendance_device_id:
            employees = ', '.join([str(elem) for elem in emps_with_id.mapped('name')])
            raise UserError(_("You cannot set the same device ID for two employees: {}.".
                              format(employees)))


class HrEmployeePublic(models.Model):
    _inherit = 'hr.employee.public'

    biometric_device_id = fields.Integer("Attendance Device ID")
    attendance_device_id = fields.Char(string='Attendance Device ID')
