# -*- coding: utf-8 -*-
####################################
# Author: Bashier Elbashier
# Date: 27th February, 2021
####################################

from odoo import http, fields
from odoo.http import request
from datetime import datetime
import pytz


class ZKTecoBiometricAttendance(http.Controller):
    @http.route(['/biometric-attendance/add'], type='json', methods=['POST'], auth="public")
    def add_biometric_attendance(self, **kwargs):
        # This key is used to verify requests which come from the ZKTeco service
        server_key = 996654132
        attendance_server_key = kwargs.get('attendance_server_key', False)
        machine_attendance_log = kwargs.get('attendance_log', False)
        attendance_log_obj = request.env['zk_hr_attendance.log']
        local_tz = pytz.timezone(kwargs.get('device_timezone', 'Asia/Riyadh'))
        if attendance_server_key and int(attendance_server_key) == server_key:
            if len(machine_attendance_log):
                for machine_attendance_entry in machine_attendance_log:
                    employee = request.env['hr.employee'].sudo().search([('attendance_device_id', '=', machine_attendance_entry['emp_id'])])
                    # Process machine attendance to fit in odoo timezone system
                    atten_time = machine_attendance_entry['att_timestamp']
                    atten_time = datetime.strptime(
                        atten_time, '%Y-%m-%d %H:%M:%S')
                    local_dt = local_tz.localize(atten_time, is_dst=None)
                    utc_dt = local_dt.astimezone(pytz.utc)
                    utc_dt = utc_dt.strftime("%Y-%m-%d %H:%M:%S")
                    atten_time = datetime.strptime(
                        utc_dt, "%Y-%m-%d %H:%M:%S")
                    atten_time = fields.Datetime.to_string(atten_time)
                    exisiting_attendance_record = request.env['zk_hr_attendance.log'].sudo().search(
                        [('attendance_timestamp', '=', atten_time)])
                    if employee and not exisiting_attendance_record:
                        # Process machine attendance to fit in odoo timezone system
                        # atten_time = machine_attendance_entry['att_timestamp']
                        # atten_time = datetime.strptime(
                        #     atten_time, '%Y-%m-%d %H:%M:%S')
                        # local_dt = local_tz.localize(atten_time, is_dst=None)
                        # utc_dt = local_dt.astimezone(pytz.utc)
                        # utc_dt = utc_dt.strftime("%Y-%m-%d %H:%M:%S")
                        # atten_time = datetime.strptime(
                        #     utc_dt, "%Y-%m-%d %H:%M:%S")
                        # atten_time = fields.Datetime.to_string(atten_time)
                        # Create ZKTeco machine attendance log entry
                        attendance_log_obj = attendance_log_obj.sudo().create({
                            "machine_employee_id": machine_attendance_entry['emp_id'],
                            'device_serialnumber': machine_attendance_entry['device_serialnumber'],
                            "attendance_timestamp": atten_time,
                            "operation": machine_attendance_entry['operation']})
        else:
            return {
                "success": False,
                "msg": "Authentication key used with request is invalid!",
            }
        return {
            "success": True,
            "msg": "Attendance log(s) created successfully"
        }

    @http.route(['/biometric-attendance/get/employee'], type='json', methods=['POST'], auth="public")
    def _biometric_attendance_get_employee(self, **kwargs):
        employee_id = False
        server_key = 996654132
        attendance_server_key = kwargs.get('attendance_server_key', False)
        emp_id = kwargs.get('emp_id', False)
        if attendance_server_key and int(attendance_server_key) == server_key and emp_id:
            employee = request.env['hr.employee'].sudo().search([('attendance_device_id', '=', emp_id)])
            if employee:
                employee_id = employee.attendance_device_id
        return {'employee_id': employee_id}
