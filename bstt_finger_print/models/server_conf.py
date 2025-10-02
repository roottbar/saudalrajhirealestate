# -*- coding: utf-8 -*-

from odoo import api, fields, models, exceptions, _
from odoo.exceptions import UserError, ValidationError
import psycopg2
from odoo.addons.resource.models.resource import float_to_time
from pytz import timezone, utc, UTC
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
from odoo.tools import format_datetime


class ServerDatabaseType(models.Model):
    _name = 'server.database.type'
    _description = "Server Database Type"
    _order = 'name'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    name = fields.Char(string="DB Type Name")
    active = fields.Boolean(default=True)


class ServerConfigurations(models.Model):
    _name = 'server.configuration'
    _description = "Server Configurations"
    _order = 'name'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    name = fields.Char(string="Server Name", required=True, tracking=True)
    db_ib = fields.Char(string="DB IP", required=True, tracking=True)
    db_port = fields.Integer(string="DB Port", required=True, tracking=True)
    db_name = fields.Char(string="DB Name", required=True, tracking=True)
    db_user = fields.Char(string="DB User", required=True, tracking=True)
    db_password = fields.Char(string="DB Pasword", required=True, tracking=True)
    db_type = fields.Many2one('server.database.type', string="DB Type", required=True, tracking=True)
    diff_gmt_hour = fields.Integer(string="Deff/GMT Hours", tracking=True)

    last_sync_time = fields.Datetime(string="Last Sync Time", tracking=True)
    last_record_id = fields.Integer(string="Last Record ID", tracking=True)
    table_name = fields.Char(string="Table Name", tracking=True)

    # DB Fields
    record_id_field_name = fields.Char(string="Record ID", tracking=True)
    emp_code_field_name = fields.Char(string="Attendance Employee Code", tracking=True)
    action_type_field_name = fields.Char(string="Action Type", help="0 = CHeck In and 1 = Check Out", tracking=True)
    action_time_field_name = fields.Char(string="Time", help="TimeStamp with TimeZone", tracking=True)
    upload_time_field_name = fields.Char(string="Upload Time", help="TimeStamp with TimeZone", tracking=True)
    ###################

    employees_exceptions = fields.Many2many('hr.employee', 'employee_exception_attendance_rel', 'server_conf_id', 'emp_id', string='Employees Exceptions', domain="[('emp_Attendance_code', '!=', False)]", tracking=True)
    attendance_ids = fields.One2many('attendance.data', 'server_id', string='Attendance Data')

    active = fields.Boolean(default=True)

    first_insertion = fields.Integer('attendance.data', compute="count_data")

    state = fields.Selection([
        ('draft', 'Draft'),
        ('confirm', 'Confirmed'),
        ('cancel', 'Canceled'),
    ], string="State", default='draft', track_visibility='onchange', copy=False)

    def action_confirm(self):
        self.write({'state': 'confirm'})

    def action_draft(self):
        self.write({'state': 'draft'})

    def action_cancel(self):
        self.write({'state': 'cancel'})

    def count_data(self):
        attendance_count = self.env["attendance.data"].search_count([])
        for rec in self:
            rec.first_insertion = attendance_count

    def connection(self):
        """ Test Connect to the PostgreSQL database server """
        conn = None
        try:
            # connect to the PostgreSQL server
            print('Connecting to the PostgreSQL database...')
            conn = psycopg2.connect(
                host=self.db_ib,
                port=self.db_port,
                database=self.db_name,
                user=self.db_user,
                password=self.db_password,
            )

        except (Exception, psycopg2.DatabaseError) as error:
            raise UserError(error)
            print(error)
        finally:
            if conn is not None:
                return conn

    def test_connect(self):
        conn = self.connection()
        if conn is not None:
            conn.close()
            raise ValidationError('The Database Connection Succeed')

    def get_weekday_id(self, day):
        if day == 'Monday':
            return 1
        if day == 'Tuesday':
            return 2
        if day == 'Wednesday':
            return 3
        if day == 'Thursday':
            return 4
        if day == 'Friday':
            return 5
        if day == 'Saturday':
            return 6
        if day == 'Sunday':
            return 7

    def conv_time_float(self, value):
        vals = value.split(':')
        t, hours = divmod(float(vals[0]), 24)
        t, minutes = divmod(float(vals[1]), 60)
        minutes = minutes / 60.0
        return hours + minutes

    def action_connect(self):
        """ Connect to the PostgreSQL database server and fetch Data"""
        conn = self.connection()
        # create a cursor
        cur = conn.cursor()
        where_clause = ' WHERE ' + self.record_id_field_name + ' > ' + str(self.last_record_id) + ' and ' + self.action_type_field_name + " in ('0','1') "
        if self.employees_exceptions:
            employees_exceptions = ()
            for emp in self.employees_exceptions:
                employees_exceptions += (emp.emp_Attendance_code,)
            where_clause += ' AND ' + self.emp_code_field_name + ' not in ' + str(employees_exceptions)
        # execute a statement
        cur.execute(' SELECT ' + self.record_id_field_name + ' , ' + self.emp_code_field_name + ' , '
                    + self.action_type_field_name + ' , ' + self.action_time_field_name + ' , '
                    + self.upload_time_field_name + " , min(TO_CHAR("+self.action_time_field_name+" :: DATE, 'dd-mm-yyyy'))"
                    +",(select count("+self.emp_code_field_name+") from "+self.table_name+" t2 where t1."+self.emp_code_field_name+" =t2."+self.emp_code_field_name+ " and TO_CHAR(t1."+self.action_time_field_name+" :: DATE, 'dd-mm-yyyy') =TO_CHAR(t2."+self.action_time_field_name+" :: DATE, 'dd-mm-yyyy')) as count_emp"
                    +" FROM "
                    + self.table_name + ' t1 ' + where_clause+' group by 1,2,3,4,5 order by '+ self.emp_code_field_name+' , '
                    + self.action_time_field_name)

        rows = cur.fetchall()
        values = []
        tz = 'UTC'
        # diff_gmt_hour = float_to_time(self.diff_gmt_hour)
        emp_obj = self.env["hr.employee"]
        resource_calendar_obj = self.env['resource.calendar']
        calendar_attendance_obj = self.env['resource.calendar.attendance']
        prev_emp = prev_action = prev_date = prev_action_time = False
        for r in rows:
            emp = emp_obj.search([('emp_Attendance_code', '=', r[1])])
            employee_tz = timezone(emp.tz or 'UTC')

            is_exception = exception_reason = exp_action_time = exp_upload_time = action_type = False
            action_type = str(r[2])

            now_utc_action_time = r[3].astimezone(employee_tz).replace(tzinfo=None)
            action_time = now_utc_action_time + relativedelta(hours=self.diff_gmt_hour)

            now_utc_upload_time = r[4].astimezone(employee_tz).replace(tzinfo=None)
            upload_time = now_utc_upload_time + relativedelta(hours=self.diff_gmt_hour)

            if not emp.id:
                raise ValidationError(_('The Employee Attendance code %s not found in Odoo ERP data, Please Add him') % (r[1]))
            resource_calendar = resource_calendar_obj.search([('id', '=', emp.resource_calendar_id.id)])
            ##########################################
            # There are one Check-In without Check-Out
            ##########################################
            if r[6] == 1 and action_type == '0':
                check_out = False
                dayofweek = self.get_weekday_id(datetime.strftime(r[3], '%A'))
                check_in_time = self.conv_time_float(action_time.strftime("%I:%M"))
                if resource_calendar.checkin_without_checkout == 'option1':  # Get check out of the shift

                    calendar_check_out = calendar_attendance_obj.search([('calendar_id', '=', resource_calendar.id),
                                                                         ('dayofweek', '=', dayofweek),
                                                                         ('hour_to', '>', check_in_time),
                                                                         ], order="hour_from desc", limit=1)
                if resource_calendar.checkin_without_checkout == 'option2':  # Get check out of the Day
                    calendar_check_out = calendar_attendance_obj.search([('calendar_id', '=', resource_calendar.id),
                                                                         ('dayofweek', '=', dayofweek)],
                                                                        order="hour_to desc", limit=1)
                if resource_calendar.checkin_without_checkout in ('option1','option2'):
                    values.append({
                        "server_id": self.id,
                        "record_id": r[0],
                        "attendance_emp_code": r[1],
                        'action_type': action_type or False,
                        "action_time": action_time,
                        "upload_time": upload_time,
                        "employee_id": emp.id,
                        "is_exception": is_exception,
                        "exception_reason": exception_reason,
                    })
                    prev_emp = r[1]
                    prev_action = action_type
                    prev_date = r[5]
                    prev_action_time = action_time

                    hour_to = float_to_time(calendar_check_out.hour_to)
                    check_out = timezone(tz).localize(datetime.combine(action_time.date(),hour_to)).astimezone(UTC).replace(tzinfo=None)
                    values.append({
                        "server_id": self.id,
                        "record_id": False,
                        "attendance_emp_code": r[1],
                        'action_type': '1',
                        "action_time": check_out,
                        "upload_time": False,
                        "employee_id": emp.id,
                        "is_exception": False,
                        "exception_reason": exception_reason,
                    })

                    continue
                if resource_calendar.checkin_without_checkout == 'option3':
                    is_exception = True
                    exception_reason = 'There are Check-In without Check-Out'
            ##########################################
            # There are one Check-Out without Check-in or the first record is checkout
            ##########################################
            elif (r[6] == 1 and action_type == '1') or (action_type == '1' and prev_emp != r[1]):
                dayofweek = self.get_weekday_id(datetime.strftime(r[3], '%A'))
                check_out_time = self.conv_time_float(action_time.strftime("%I:%M"))
                if resource_calendar.checkout_without_checkin == 'option1':  # Get check out of the shift

                    calendar_check_in = calendar_attendance_obj.search([('calendar_id', '=', resource_calendar.id),
                                                                        ('dayofweek', '=', dayofweek),
                                                                        ('hour_from', '<', check_out_time),
                                                                        ], order="hour_from desc", limit=1)
                if resource_calendar.checkout_without_checkin == 'option2':  # Get check out of the Day
                    calendar_check_in = calendar_attendance_obj.search([('calendar_id', '=', resource_calendar.id),
                                                                        ('dayofweek', '=', dayofweek)],
                                                                       order="hour_from", limit=1)
                if resource_calendar.checkout_without_checkin in ('option1', 'option2'):
                    hour_from = float_to_time(calendar_check_in.hour_from)
                    check_in = timezone(tz).localize(datetime.combine(action_time.date(),hour_from)).astimezone(UTC).replace(tzinfo=None)
                    values.append({
                        "server_id": self.id,
                        "record_id": False,
                        "attendance_emp_code": r[1],
                        'action_type': '0',
                        "action_time": check_in,
                        "upload_time": False,
                        "employee_id": emp.id,
                        "is_exception": False,
                        "exception_reason": exception_reason,
                    })
                if resource_calendar.checkout_without_checkin == 'option3':
                    is_exception = True
                    exception_reason = "There are Check-Out Without Check-In"
            ##########################################
            # There are 2 Check-In
            ##########################################
            elif prev_emp == r[1] and prev_action == action_type and action_type == '0' and prev_date == r[5]:
                # check_in Calculation ##################
                if resource_calendar.checkin_2 == 'option1':
                    is_exception = True
                    exception_reason = 'There are 2 Check-In'
                if resource_calendar.checkin_2 == 'option2':
                    values[len(values) - 1]["is_exception"] = True
                    values[len(values) - 1]["exception_reason"] = 'There are 2 Check-In'
                if resource_calendar.checkin_2 == 'option3':
                    exception_reason = "There are 2 Check-In"
                    exp_action_time = values[len(values) - 1]["action_time"]
                    exp_upload_time = values[len(values) - 1]["upload_time"]
                if resource_calendar.checkin_2 == 'option4':
                    exception_reason = "There are 2 Check-In"
                    exp_action_time = action_time
                    exp_upload_time = upload_time
                if resource_calendar.checkin_2 in ('option3','option4'):
                    values.append({
                        "server_id": self.id,
                        "record_id": False,
                        "attendance_emp_code": r[1],
                        'action_type': '1',
                        "action_time": exp_action_time,
                        "upload_time": exp_upload_time,
                        "employee_id": emp.id,
                        "is_exception": False,
                        "exception_reason": exception_reason,
                    })
            ##########################################
            # There are 2 Check-Out
            ##########################################
            elif prev_emp == r[1] and prev_action == action_type and action_type == '1' and prev_date == r[5]:
                # check_in Calculation ##################
                if resource_calendar.checkout_2 == 'option1':
                    is_exception = True
                    exception_reason = 'There are 2 Check-Out'
                if resource_calendar.checkout_2 == 'option2':
                    values[len(values) - 1]["is_exception"] = True
                    values[len(values) - 1]["exception_reason"] = 'There are 2 Check-Out'
                if resource_calendar.checkout_2 == 'option3':
                    exp_action_time = values[len(values) - 1]["action_time"]
                    exp_upload_time = values[len(values) - 1]["upload_time"]
                    exception_reason = 'There are 2 Check-Out'
                if resource_calendar.checkout_2 == 'option4':
                    exp_action_time = action_time
                    exp_upload_time = upload_time
                    exception_reason = 'There are 2 Check-Out'
                if resource_calendar.checkout_2 in ('option3','option4'):
                    values.append({
                        "server_id": self.id,
                        "record_id": False,
                        "attendance_emp_code": r[1],
                        'action_type': '0',
                        "action_time": exp_action_time,
                        "upload_time": exp_upload_time,
                        "employee_id": emp.id,
                        "is_exception": False,
                        "exception_reason": exception_reason,
                    })

            values.append({
                "server_id": self.id,
                "record_id": r[0],
                "attendance_emp_code": r[1],
                'action_type': action_type or False,
                "action_time": action_time,
                "upload_time": upload_time,
                "employee_id": emp.id,
                "is_exception": is_exception,
                "exception_reason": exception_reason,
            })
            prev_emp = r[1]
            prev_action = action_type
            prev_date = r[5]
            prev_action_time = action_time
            # r[3] + relativedelta(hours=self.diff_gmt_hour) if r[3] else False
        attendance_data = self.env["attendance.data"].create(values)

        # close the communication with the PostgreSQL
        cur.close()
        conn.close()
        self.env.cr.execute('SELECT max(record_id) FROM attendance_data WHERE server_id= ' + str(self.id))
        self.last_record_id = self.env.cr.fetchone()[0] or False

        self.env.cr.execute('SELECT max(action_time) FROM attendance_data WHERE server_id= ' + str(self.id))
        self.last_sync_time = self.env.cr.fetchone()[0] or False

        self.push_data_to_hr_attendance()

    def push_data_to_hr_attendance(self):
        attendance_data_obj = self.env["attendance.data"]
        attendance_data = attendance_data_obj.search([('is_exception', '=', False),('transfer_to_hr_attendance', '=', False)],
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
            elif len(attendances) > 0 and rec.action_type == '1' and attendance_data.employee_id == prev_emp \
                    and not attendances[len(attendances) - 1]["check_out"] \
                    and rec.action_time.strftime("%d%m%Y") == attendances[len(attendances) - 1]["check_in"].strftime("%d%m%Y"):

                attendances[len(attendances) - 1]["check_out"] = rec.action_time
                rec.transfer_to_hr_attendance = True
            else:
                rec.transfer_to_hr_attendance = False
            prev_emp = attendance_data.employee_id

        # Delete records that have only check in without checkout
        i = 0
        for line in attendances:
            if not line.get('check_out', False):
                get_record = attendance_data_obj.search([('employee_id', '=', line.get('employee_id', False)),
                                            ('action_time', '=', line.get('check_in', False)),
                                            ('action_type', '=', '0')], limit=1)
                get_record.transfer_to_hr_attendance = False
                attendances.pop(i)
            i += 1

        attendance = self.env["hr.attendance"].create(attendances)
