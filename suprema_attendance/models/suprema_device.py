# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import UserError
import logging
import pkg_resources

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
    company_id = fields.Many2one('res.company', string='Company', default=lambda self: self.env.company)

    def _get_zk_library(self):
        try:
            from pyzk import zk
            # تسجيل إصدار المكتبة
            try:
                version = pkg_resources.get_distribution("pyzk").version
                _logger.info("Using pyzk version: %s", version)
            except Exception:
                _logger.warning("Could not determine pyzk version")
            return zk
        except ImportError:
            _logger.error("pyzk library not found")
            raise UserError(_("Please install pyzk library: pip install pyzk"))

    def connect_device(self):
        """Establish connection with biometric device"""
        _logger.info("Attempting to connect to device %s at %s:%s", 
                    self.name, self.ip_address, self.port)
        
        try:
            zk = self._get_zk_library()
            device = zk.ZK(
                self.ip_address,
                port=self.port,
                timeout=60,
                password=0,  # Default password
                force_udp=False,
                ommit_ping=False,
                verbose=True  # Enable verbose logging
            )
            
            conn = device.connect()
            if not conn:
                raise UserError(_("Connection failed: No connection object returned"))
                
            _logger.info("Successfully connected to device %s", self.name)
            conn.disable_device()  # Disable device during operations
            return conn
            
        except Exception as e:
            error_msg = _("Connection failed: %s") % str(e)
            _logger.error("Device %s connection error: %s", self.name, error_msg)
            raise UserError(error_msg)

    def test_connection(self):
        """Test device connection with detailed feedback"""
        conn = None
        try:
            conn = self.connect_device()
            if conn:
                # Get detailed device info
                device_name = conn.get_device_name()
                firmware = conn.get_firmware_version()
                platform = conn.get_platform()
                serial = conn.get_serialnumber()
                
                conn.enable_device()
                
                return {
                    'type': 'ir.actions.client',
                    'tag': 'display_notification',
                    'params': {
                        'title': _("Connection Successful"),
                        'message': _(
                            "Device Info:\n"
                            "Name: %s\n"
                            "Firmware: %s\n"
                            "Platform: %s\n"
                            "Serial: %s"
                        ) % (device_name, firmware, platform, serial),
                        'sticky': True,
                        'type': 'success',
                    }
                }
                
        except Exception as e:
            error_msg = _("Test connection failed: %s") % str(e)
            _logger.error(error_msg)
            raise UserError(error_msg)
            
        finally:
            if conn:
                conn.disconnect()
                _logger.info("Disconnected from device %s", self.name)

    def download_attendance(self):
        """Download attendance logs from device"""
        conn = None
        try:
            conn = self.connect_device()
            attendance_logs = conn.get_attendance()
            
            if not attendance_logs:
                _logger.warning("No attendance records found on device %s", self.name)
                return {
                    'type': 'ir.actions.client',
                    'tag': 'display_notification',
                    'params': {
                        'title': _("Warning"),
                        'message': _("No attendance records found on device"),
                        'sticky': False,
                        'type': 'warning',
                    }
                }
            
            # Process attendance logs
            AttendanceLog = self.env['suprema.attendance.log']
            employees = self.env['hr.employee'].search([])
            
            for log in attendance_logs:
                employee = employees.filtered(
                    lambda e: e.biometric_id == str(log.user_id))
                
                if not employee:
                    _logger.warning("No employee found with biometric ID: %s", log.user_id)
                    continue
                    
                AttendanceLog.create({
                    'device_id': self.id,
                    'employee_id': employee.id,
                    'punch_time': fields.Datetime.to_string(log.timestamp),
                    'status': self._determine_status(employee, log.timestamp),
                })
            
            self.last_sync = fields.Datetime.now()
            
            return {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'title': _("Success"),
                    'message': _("Downloaded %s attendance records") % len(attendance_logs),
                    'sticky': False,
                    'type': 'success',
                }
            }
            
        except Exception as e:
            error_msg = _("Download failed: %s") % str(e)
            _logger.error(error_msg)
            raise UserError(error_msg)
            
        finally:
            if conn:
                conn.enable_device()
                conn.disconnect()

    def _determine_status(self, employee, timestamp):
        """Determine if check-in or check-out based on existing records"""
        domain = [
            ('employee_id', '=', employee.id),
            ('check_in', '<=', timestamp),
            ('check_out', '>=', timestamp),
        ]
        attendance = self.env['hr.attendance'].search(domain, limit=1)
        return 'check_out' if attendance else 'check_in'

    def cron_sync_attendance(self):
        """Scheduled method to sync attendance automatically"""
        devices = self.search([('active', '=', True)])
        for device in devices:
            try:
                device.download_attendance()
            except Exception as e:
                _logger.error("Failed to sync device %s: %s", device.name, str(e))
                continue
