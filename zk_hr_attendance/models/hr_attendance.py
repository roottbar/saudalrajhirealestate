from odoo import fields, models, api


class HRAttendance(models.Model):
    _inherit = 'hr.attendance'

    check_in_device = fields.Char(string='Check In Device')
    check_out_device = fields.Char(string='Check Out Device')
