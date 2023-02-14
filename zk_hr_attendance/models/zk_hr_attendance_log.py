# -*- coding: utf-8 -*-
####################################
# Author: Bashier Elbashier
# Date: 27th February, 2021
####################################
from odoo import models, fields, api


class ZKMachineAttendanceLog(models.Model):
    _name = 'zk_hr_attendance.log'
    _description = "ZK Machine Raw Attendance Log"
    _order = 'attendance_timestamp desc'

    name = fields.Char("Attendance Record", compute='_compute_attendance_log_name')
    machine_employee_id = fields.Char("ZK Machine Employee ID", required=1)
    device_serialnumber = fields.Char(string='Attending Device SerialNumber')
    attendance_timestamp = fields.Datetime("Attendance Timestamp", required=1)
    operation = fields.Integer("Operation")
    operation_type = fields.Selection([('0', 'Check In'),
                                       ('1', 'Check Out'),
                                       ('2', 'Break Out'),
                                       ('3', 'Break In'),
                                       ('4', 'Overtime In'),
                                       ('5', 'Overtime Out')],
                                      string='Operation Type',
                                      compute='_compute_operation_type')
    # This field indicates whether this attendance record has been processed to odoo attendance or not
    state = fields.Selection([('done', 'Processed'), ('new', 'New')], "Status", default="new")

    @api.depends('operation')
    def _compute_operation_type(self):
        for record in self:
            record.operation_type = str(record.operation)

    def _compute_attendance_log_name(self):
        for rec in self:
            employee = rec.env['hr.employee'].search([('attendance_device_id', '=', rec.machine_employee_id)])
            if employee:
                attendance = fields.Datetime.context_timestamp(rec, rec.attendance_timestamp)
                computed_name = employee.name + "-" + attendance.strftime("%Y/%m/%d %H:%M:%S")
            else:
                ats = fields.Datetime.context_timestamp(self, rec.attendance_timestamp).strftime("%Y/%m/%d %H:%M:%S")
                computed_name = "EMP " + str(rec.machine_employee_id) + "-" + ats
            rec.name = computed_name

    def process_zk_machine_attendance_log_daily(self):
        """
        Process machine attendance log records daily (first record in the day is the check in
        and the last is the check out).
        :return: None
        """


        employees = self.env['hr.employee'].search([])
        for employee in employees:
            employee_machine_attendance_ids = self.search([('machine_employee_id',
                                                            '=',
                                                            employee.attendance_device_id),
                                                           ('state', '=', 'new')])
            if len(employee_machine_attendance_ids) > 0:
                attendances_of_emp_sorted = employee_machine_attendance_ids.sorted(
                    lambda att_emp: att_emp.attendance_timestamp)
                dates_of_attendance = attendances_of_emp_sorted. \
                    mapped(lambda att_rec: att_rec.attendance_timestamp.strftime("%Y/%m/%d"))
                dates_of_attendance = set(dates_of_attendance)
                for date_of_attendance in dates_of_attendance:
                    current_date_attendances = attendances_of_emp_sorted.filtered(
                        lambda att: att.attendance_timestamp.strftime("%Y/%m/%d") == date_of_attendance)
                    all_current_date_attendances = self.search([('machine_employee_id', '=',
                                                                 employee.attendance_device_id)])
                    all_current_date_attendances = all_current_date_attendances.filtered(
                        lambda att: att.attendance_timestamp.strftime("%Y/%m/%d") == date_of_attendance)
                    if len(all_current_date_attendances) > 0:
                        current_date_hr_attendances = \
                            self.env['hr.attendance'].search([('employee_id', '=', employee.id)])
                        current_date_hr_attendances = current_date_hr_attendances.filtered(
                            lambda att: att.check_in.strftime("%Y/%m/%d") == date_of_attendance)
                        if len(current_date_hr_attendances) > 0:
                            current_date_hr_attendances[-1].write(
                                {"check_out": current_date_attendances[-1].attendance_timestamp,
                                 'check_out_device': current_date_attendances[0].device_serialnumber,
                                 })
                        else:
                            check_out = current_date_attendances[-1]
                            self.env['hr.attendance']. \
                                create({
                                "employee_id": employee.id,
                                "check_in": current_date_attendances[0].attendance_timestamp,
                                'check_in_device': current_date_attendances[0].device_serialnumber,
                                "check_out": check_out.attendance_timestamp,
                                'check_out_device': current_date_attendances[0].device_serialnumber,
                                "company_id": employee.company_id.id})
                    for cr_date_att in current_date_attendances:
                        cr_date_att.state = 'done'

    def process_zk_machine_attendance_log_accurate(self):
        """
        Process machine attendance log records accurately (check in is check in & check out is check out).
        :return: None
        """

        employees = self.env['hr.employee'].search([])
        for employee in employees:
            employee_machine_attendance_ids = self.search([('machine_employee_id',
                                                            '=',
                                                            employee.attendance_device_id),
                                                           ('state', '=', 'new')])
            if len(employee_machine_attendance_ids) > 0:
                attendances_of_emp_sorted = employee_machine_attendance_ids.sorted(
                    lambda att_emp: att_emp.attendance_timestamp)
                dates_of_attendance = attendances_of_emp_sorted. \
                    mapped(lambda att_rec: att_rec.attendance_timestamp.strftime("%Y/%m/%d"))
                dates_of_attendance = sorted(set(dates_of_attendance))
                for date_of_attendance in dates_of_attendance:
                    all_current_date_attendances = self.search([('machine_employee_id', '=',
                                                                 employee.attendance_device_id)])
                    all_current_date_attendances = all_current_date_attendances.filtered(
                        lambda att: att.attendance_timestamp.strftime("%Y/%m/%d") == date_of_attendance)
                    all_current_date_attendances = all_current_date_attendances.sorted(
                        lambda att: att.attendance_timestamp)
                    if len(all_current_date_attendances) > 0:
                        current_date_hr_attendances = \
                            self.env['hr.attendance'].search([('employee_id', '=', employee.id)])
                        current_date_hr_attendances = current_date_hr_attendances.filtered(
                            lambda att: att.check_in.strftime("%Y/%m/%d") == date_of_attendance)

                        if len(current_date_hr_attendances) > 0:
                            last_date_attendance = current_date_hr_attendances[-1]
                        else:
                            last_date_attendance = False
                        for attendance in all_current_date_attendances:
                            if attendance.operation == 1 and last_date_attendance and attendance.attendance_timestamp > last_date_attendance.check_in:
                                last_date_attendance.write(
                                    {"check_out": attendance.attendance_timestamp,
                                     'check_out_device': attendance.device_serialnumber},
                                )
                                attendance.state = 'done'
                            elif attendance.operation == 0 and not last_date_attendance:
                                last_date_attendance = self.env['hr.attendance'].create(
                                    {"employee_id": employee.id,
                                     "check_in": attendance.attendance_timestamp,
                                     'check_in_device': attendance.device_serialnumber,
                                     'check_out_device': attendance.device_serialnumber,
                                     "check_out": attendance.attendance_timestamp,
                                     "company_id": employee.company_id.id})
                                attendance.state = 'done'
                            else:
                                pass


    def process_zk_machine_attendance_log_sequential(self):
        """
        Process machine attendance log records sequentially (first is check in & second is check out & so forth)
        :return: None
        """

        employees = self.env['hr.employee'].search([])
        for employee in employees:
            employee_machine_attendance_ids = self.search([('machine_employee_id',
                                                            '=',
                                                            employee.attendance_device_id),
                                                           ('state', '=', 'new')])
            if len(employee_machine_attendance_ids) > 0:
                attendances_of_emp_sorted = employee_machine_attendance_ids.sorted(
                    lambda att_emp: att_emp.attendance_timestamp)
                dates_of_attendance = attendances_of_emp_sorted. \
                    mapped(lambda att_rec: att_rec.attendance_timestamp.strftime("%Y/%m/%d"))
                dates_of_attendance = set(dates_of_attendance)
                for date_of_attendance in dates_of_attendance:
                    all_current_date_attendances = self.search([('machine_employee_id', '=',
                                                                 employee.attendance_device_id)])
                    all_current_date_attendances = all_current_date_attendances.filtered(
                        lambda att: att.attendance_timestamp.strftime("%Y/%m/%d") == date_of_attendance)
                    all_current_date_attendances = all_current_date_attendances.sorted(
                        lambda att: att.attendance_timestamp)
                    if len(all_current_date_attendances) > 0:
                        current_date_hr_attendances = \
                            self.env['hr.attendance'].search([('employee_id', '=', employee.id)])
                        current_date_hr_attendances = current_date_hr_attendances.filtered(
                            lambda att: att.check_in.strftime("%Y/%m/%d") == date_of_attendance)

                        if len(current_date_hr_attendances) > 0:
                            last_date_attendance = current_date_hr_attendances[-1]
                        else:
                            last_date_attendance = False

                        for attendance in all_current_date_attendances:
                            if last_date_attendance and last_date_attendance.check_in == last_date_attendance.check_out:
                                last_date_attendance.write({"check_out": attendance.attendance_timestamp})
                            else:
                                last_date_attendance = self.env['hr.attendance'].create(
                                    {"employee_id": employee.id,
                                     "check_in": attendance.attendance_timestamp,
                                     "check_out": attendance.attendance_timestamp,
                                     "company_id": employee.company_id.id})
                            # attendance.state = 'done'

    def clear_processed_zk_machine_attendance_log(self):
        attendance_ids = self.search([('state', '=', 'done')])
        attendance_ids.unlink()
