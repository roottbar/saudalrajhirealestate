from odoo import models, fields, api, _
from odoo.exceptions import UserError
from datetime import datetime
import logging

_logger = logging.getLogger(__name__)


class SupremaDevice(models.Model):
    _name = 'suprema.device'
    _description = 'Suprema Biometric Device'

    name = fields.Char(string='Device Name', required=True)
    ip_address = fields.Char(string='IP Address', required=True)
    port = fields.Integer(string='Port', default=4370)
    device_id = fields.Integer(string='Device ID', default=1)
    connection_type = fields.Selection([
        ('tcp', 'TCP/IP'),
        ('usb', 'USB'),
    ], string='Connection Type', default='tcp')
    active = fields.Boolean(string='Active', default=True)
    last_sync = fields.Datetime(string='Last Synchronization')
    attendance_ids = fields.One2many(
        'suprema.attendance.log',
        'device_id',
        string='Attendance Logs'
    )
    company_id = fields.Many2one(
        'res.company',
        string='Company',
        default=lambda self: self.env.company
    )

    def connect_device(self):
        try:
            zk = self._get_zk_library()
            device = zk.ZK(
                self.ip_address,
                port=self.port,
                timeout=60,
                password=0,
                force_udp=False,
                ommit_ping=False
            )
            conn = device.connect()
            return conn
        except Exception as e:
            _logger.error("Suprema connection error: %s", str(e))
            raise UserError(_("Connection failed: %s") % str(e))

    def _get_zk_library(self):
        try:
            from pyzk import zk
            return zk
        except ImportError:
            raise UserError(_("Please install pyzk library: pip install pyzk"))

    def test_connection(self):
        conn = None
        try:
            conn = self.connect_device()
            if conn:
                conn.disable_device()
                conn.enable_device()
                return {
                    'type': 'ir.actions.client',
                    'tag': 'display_notification',
                    'params': {
                        'title': _("Success"),
                        'message': _("Connection to device successful!"),
                        'sticky': False,
                        'type': 'success',
                    }
                }
        except Exception as e:
            raise UserError(_("Test connection failed: %s") % str(e))
        finally:
            if conn:
                conn.disconnect()

    def download_attendance(self):
        conn = None
        try:
            conn = self.connect_device()
            conn.disable_device()
            attendance_logs = conn.get_attendance()
            conn.enable_device()

            AttendanceLog = self.env['suprema.attendance.log']
            employees = self.env['hr.employee'].search([])

            for log in attendance_logs:
                employee = employees.filtered(
                    lambda e: e.biometric_id == str(log.user_id)

                if not employee:
                    continue

                AttendanceLog.create({
                    'device_id': self.id,
                    'employee_id': employee.id,
                    'punch_time': self._convert_time(log.timestamp),
                    'status': self._determine_status(employee, log.timestamp),
                })

            self.last_sync = fields.Datetime.now()

            return {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'title': _("Success"),
                    'message': _("Attendance data downloaded successfully!"),
                    'sticky': False,
                    'type': 'success',
                }
            }
        except Exception as e:
            raise UserError(_("Download failed: %s") % str(e))
        finally:
            if conn:
                conn.disconnect()

    def _convert_time(self, timestamp):
        return fields.Datetime.to_string(timestamp)

    def _determine_status(self, employee, timestamp):
        # Implement your logic to determine check-in/check-out
        # This is a simple example - you may need more complex logic
        domain = [
            ('employee_id', '=', employee.id),
            ('check_in', '<=', timestamp),
            ('check_out', '>=', timestamp),
        ]
        attendance = self.env['hr.attendance'].search(domain, limit=1)
        return 'check_out' if attendance else 'check_in'

    def cron_sync_attendance(self):
        devices = self.search([('active', '=', True)])
        for device in devices:
            try:
                device.download_attendance()
            except Exception as e:
                _logger.error("Failed to sync device %s: %s", device.name, str(e))