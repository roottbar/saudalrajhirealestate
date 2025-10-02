from odoo import models, fields, api, _
from odoo.exceptions import UserError


class SupremaAttendanceLog(models.Model):
    _name = 'suprema.attendance.log'
    _description = 'Suprema Attendance Logs'
    _order = 'punch_time desc'

    device_id = fields.Many2one(
        'suprema.device',
        string='Device',
        required=True,
        ondelete='cascade'
    )
    employee_id = fields.Many2one(
        'hr.employee',
        string='Employee',
        required=True
    )
    punch_time = fields.Datetime(
        string='Punch Time',
        required=True
    )
    status = fields.Selection([
        ('check_in', 'Check In'),
        ('check_out', 'Check Out'),
        ('unknown', 'Unknown'),
    ], string='Status', default='unknown')
    is_processed = fields.Boolean(
        string='Processed',
        default=False,
        index=True
    )
    attendance_id = fields.Many2one(
        'hr.attendance',
        string='Odoo Attendance'
    )

    def process_attendance(self):
        HrAttendance = self.env['hr.attendance']
        unprocessed_logs = self.search([('is_processed', '=', False)], order='punch_time')

        for log in unprocessed_logs:
            try:
                if log.status == 'check_in':
                    attendance = HrAttendance.create({
                        'employee_id': log.employee_id.id,
                        'check_in': log.punch_time,
                    })
                    log.write({
                        'attendance_id': attendance.id,
                        'is_processed': True,
                    })
                elif log.status == 'check_out':
                    # Find last check-in without check-out
                    attendance = HrAttendance.search([
                        ('employee_id', '=', log.employee_id.id),
                        ('check_out', '=', False),
                    ], order='check_in desc', limit=1)

                    if attendance:
                        attendance.check_out = log.punch_time
                        log.write({
                            'attendance_id': attendance.id,
                            'is_processed': True,
                        })
            except Exception as e:
                _logger.error("Failed to process attendance log %s: %s", log.id, str(e))

        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': _("Success"),
                'message': _("Attendance logs processed successfully!"),
                'sticky': False,
                'type': 'success',
            }
        }

    def cron_process_attendance_logs(self):
        self.search([('is_processed', '=', False)]).process_attendance()