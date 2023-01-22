# -*- coding: utf-8 -*-
from odoo import models, fields, _
from datetime import datetime
from odoo.osv import expression


class AttendanceReinsertWizard(models.TransientModel):
    """
    This wizard is used to reinsert into hr attendance
    """
    _name = 'attendance.reinsert.wizard'
    _description = 'Attendance Reinsert Wizard'

    from_date = fields.Date(string='From Date', default=lambda self: datetime.now(), required=True)
    to_date = fields.Date(string='To Date', default=lambda self: datetime.now(), required=True)

    department_id = fields.Many2one('hr.department', string="Department")
    dept_check = fields.Boolean(string="All Departments Under this Dep.")
    category_ids = fields.Many2many('hr.employee.category', string='Tags')

    def reinsert(self):
        # Delete HR Attendance
        domain = [('check_in', '<=', self.to_date), ('check_in', '>=', self.from_date), ('is_used_in_Payroll', '=', False), ('inserted_by_finger_print', '=', True)]
        if self.category_ids:
            domain = expression.AND([domain, [('employee_id.category_ids', 'in', self.category_ids.ids)]])
        if self.department_id and self.dept_check:
            domain = expression.AND([domain, [('employee_id.department_id', 'child_of', self.department_id.id)]])
        if self.department_id and not self.dept_check:
            domain = expression.AND([domain, [('employee_id.department_id', '=', self.department_id.id)]])
        if not self.env.user.has_group('hr_attendance.group_hr_attendance_manager'):
            domain = expression.AND([domain, ['|', ('parent_id.user_id', '=', self.env.user.id),('user_id', '=', self.env.user.id)]])
        hr_attendance = self.env["hr.attendance"].search(domain).unlink()

        # update attendance_data
        attendance_data_domain = [('action_time', '<=', self.to_date), ('action_time', '>=', self.from_date), ('transfer_to_hr_attendance', '=', True)]
        if self.category_ids:
            attendance_data_domain = expression.AND([attendance_data_domain, [('employee_id.category_ids', 'in', self.category_ids.ids)]])
        if self.department_id and self.dept_check:
            attendance_data_domain = expression.AND([attendance_data_domain, [('employee_id.department_id', 'child_of', self.department_id.id)]])
        if self.department_id and not self.dept_check:
            attendance_data_domain = expression.AND([attendance_data_domain, [('employee_id.department_id', '=', self.department_id.id)]])
        if not self.env.user.has_group('hr_attendance.group_hr_attendance_manager'):
            attendance_data_domain = expression.AND(
                [attendance_data_domain, ['|', ('parent_id.user_id', '=', self.env.user.id), ('user_id', '=', self.env.user.id)]])
        attendance_data_ids = self.env["attendance.data"].search(attendance_data_domain)
        attendance_data_ids.transfer_to_hr_attendance = False

        self.push_data_to_hr_attendance()

        return {'type': 'ir.actions.act_window_close'}

    def push_data_to_hr_attendance(self):
        attendance_data = self.env["attendance.data"].search([('is_exception', '=', False),('transfer_to_hr_attendance', '=', False)],
                                                             order="employee_id,id")
        # order="employee_id,action_time,action_type"
        attendances = []
        prev_emp = prev_action = False
        for rec in attendance_data:
            if rec.action_type == '0':
                attendances.append({
                    "employee_id": rec.employee_id.id,
                    "check_in": rec.action_time,
                    "check_out": False,
                    "inserted_by_finger_print": True
                })
                rec.transfer_to_hr_attendance = True
            elif len(attendances)>0 and rec.action_type == '1' and attendance_data.employee_id == prev_emp and not attendances[len(attendances) - 1]["check_out"]:
                attendances[len(attendances) - 1]["check_out"] = rec.action_time
                rec.transfer_to_hr_attendance = True
            else:
                rec.transfer_to_hr_attendance = False
            prev_emp = attendance_data.employee_id
        attendance = self.env["hr.attendance"].create(attendances)
