# -*- coding: utf-8 -*-
from odoo import api, fields, models, _


class AttendanceData(models.Model):
    _name = 'attendance.data'
    _description = "Attendance Data"
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _rec_name = "employee_id"
    _order = "id"

    server_id = fields.Many2one('server.configuration', 'Server Name')
    record_id = fields.Integer(string="Record ID")
    attendance_emp_code = fields.Char(string="Attendance Employee Code")
    employee_id = fields.Many2one('hr.employee', string="Employee")
    # employee_id = fields.Many2one('hr.employee', string="Employee", compute="get_employee", store=True)
    action_type = fields.Selection([('0', 'Check-In'), ('1', 'Check-out')], string="Action Type", help="0 = CHeck In and 1 = Check Out")
    action_time = fields.Datetime(string="Puch Time")
    action_time_with_timezone = fields.Datetime(string="Puch Time", help="TimeStamp with TimeZone",  compute="get_time", store=True)
    upload_time = fields.Datetime(string="Upload Time", help="TimeStamp with TimeZone")
    is_exception = fields.Boolean(string="Exception?", default=False)
    exception_reason = fields.Char(string="Exception Reason")
    active = fields.Boolean(default=True)
    transfer_to_hr_attendance = fields.Boolean(string="Transfer to Odoo Attendance", default=False)
    new_rec = fields.Boolean(default=False,  compute="compute_new_rec")

    def compute_new_rec(self):
        for rec in self:
            rec.new_rec = False
            if rec.record_id == 0:
                rec.new_rec = True

    # @api.depends("attendance_emp_code")
    # def get_employee(self):
    #     emp_obj = self.env["hr.employee"]
    #     for rec in self:
    #         rec.employee_id = False
    #         if rec.attendance_emp_code:
    #             emp = emp_obj.search([('emp_Attendance_code', '=', rec.attendance_emp_code)])
    #             rec.employee_id = emp.id if len(emp) == 1 else False
