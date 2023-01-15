# -*- coding: utf-8 -*-
import babel
import time
from datetime import datetime

from odoo import models, fields, api, tools, _


class HrPayslip(models.Model):
    _inherit = 'hr.payslip'

    def action_payslip_done(self):
        res = super(HrPayslip, self).action_payslip_done()
        for payslip in self:
            hr_attendance = self.env["hr.attendance"].search([('employee_id','=',payslip.employee_id),('check_in','>=',payslip.date_from),('check_in','<=',payslip.date_to)])
            hr_attendance.is_used_in_Payroll = True
        return res

    def action_payslip_cancel(self):
        res = super(HrPayslip, self).action_payslip_cancel()
        for payslip in self:
            hr_attendance = self.env["hr.attendance"].search([('employee_id', '=', payslip.employee_id),('check_in', '>=', payslip.date_from),('check_in', '<=', payslip.date_to),('is_used_in_Payroll', '=', True)])
            hr_attendance.is_used_in_Payroll = False
        return res

