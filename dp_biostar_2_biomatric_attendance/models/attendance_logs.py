# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
from odoo.exceptions import UserError
from datetime import datetime


class AttendanceLog(models.Model):
    _name = 'attendance.log'
    _description = 'attendance log'
    _order = 'punching_time desc'
    _rec_name = 'punching_time'

    status = fields.Selection([('0', 'Check In'),
                               ('1', 'Check Out'),
                               ('2', 'Punched')], string='Status')
    punching_time = fields.Datetime('Punching Time')
    device = fields.Char('Device')
    employee_id = fields.Many2one('hr.employee', string='Employee',
                                  store=True)
    employee_name = fields.Char('Employee Name',
                                )
    status_number = fields.Char("Status Number")
    number = fields.Char("Number")
    timestamp = fields.Integer("Time stamp")
    status_string = fields.Char("Status String")




class HrAttendance(models.Model):
    _inherit = "hr.attendance"

    punch_date = fields.Date(string='Punch Date')

    def compute_in_out_difference(self):
        for attendance in self:
            if attendance.check_in and attendance.check_out:
                check_in = datetime.strptime(str(attendance.check_in), '%Y-%m-%d %H:%M:%S')
                check_out = datetime.strptime(str(attendance.check_out), '%Y-%m-%d %H:%M:%S')
                diff1 = check_out - check_in
                total_seconds = diff1.seconds
                diff2 = total_seconds / 3600.0
                attendance.in_out_diff = diff2
            else:
                attendance.in_out_diff = 0

    in_out_diff = fields.Float('Difference', compute='compute_in_out_difference')

    def unlink(self):
        for record in self:
            domain = [('employee_id', '=', record.employee_id.id), '|',
                      ('punching_time', '=', record.check_in),
                      ('punching_time', '=', record.check_out)]
            attend_obj = self.env['attendance.log'].search(domain)
            for log in attend_obj:
                log.is_calculated = False
        return super(HrAttendance, self).unlink()
