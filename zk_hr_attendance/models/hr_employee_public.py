from odoo import fields, models, api, _


class HrEmployeePublic(models.Model):
    _inherit = "hr.employee.public"

    biometric_device_id = fields.Integer("Attendance Device ID")
