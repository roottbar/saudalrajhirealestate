from odoo import models, fields

class HrEmployeeInherit(models.Model):
    _inherit = 'hr.employee'

    biometric_id = fields.Char(string='Biometric ID')
