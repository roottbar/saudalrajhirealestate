# -*- coding: utf-8 -*-

##############################################################################
#
#
#    Copyright (C) 2020-TODAY .
#    Author: Eng.Hassan Abdallah
#
#    It is forbidden to publish, distribute, sublicense, or sell copies
#    of the Software or modified copies of the Software.
#
##############################################################################

from odoo import models, fields, api
DATETIME_FORMAT = "%Y-%m-%d %H:%M:%S"
TIME_FORMAT = "%H:%M:%S"


class HrAttendanceException(models.Model):
    _name = 'hr.attendance.exception'
    _inherit = ['mail.thread']
    _description = 'Hr Attendance Exception'
    _order = 'id desc'

    name = fields.Char(readonly=True)
    employee_id = fields.Many2one(comodel_name='hr.employee', string='Employee',
                                  required=True)
    department_id = fields.Many2one(related='employee_id.department_id',
                                    string='Department', store=True)
    transaction_id = fields.Many2one('attendance.transaction')
    request_date = fields.Date("Request Date", default=fields.Date.today())
    exception_reason = fields.Text(string='Explanation')
    exception_type = fields.Selection([
        ('absence', 'Absence'),
        ('forget', 'Check Out Forget'),
    ], 'Exception Type', default='absence')
    state = fields.Selection([
        ('draft', 'Draft'),
        ('submit', 'Submitted'),
        ('approve', 'Approved'),
        ('refuse', 'Refused'),
        ('cancel', 'Cancelled'),
    ], 'Status', default='draft')
    absence_date = fields.Date(string='Absence Date')
    check_out = fields.Datetime(string='Check Out')

    @api.model
    def create(self, vals):
        """Add sequence."""
        name_request = self.env['ir.sequence'].next_by_code('attendance.exception.request.seq')
        vals.update({'name': name_request})
        return super(HrAttendanceException, self).create(vals)

    def action_approve(self):
        for rec in self:
            if rec.transaction_id:
                if rec.exception_type == 'absence':
                    rec.transaction_id.update({'status': 'leave'})
            elif rec.exception_type == 'forget':
                rec.transaction_id.update({'status': 'ex',
                                           'ac_sign_out': rec.transaction_id.pl_sign_out,
                                           })
            rec.write({'state': 'approve'})

    def action_submit(self):
        for rec in self:
            rec.write({'state': 'submit'})

    def action_refuse(self):
        for rec in self:
            rec.write({'state': 'refuse'})
