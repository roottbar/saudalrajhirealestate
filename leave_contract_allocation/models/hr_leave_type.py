from odoo import models, api, fields


class LeaveType(models.Model):
    _inherit = 'hr.leave.type'

    allocation_per_contract = fields.Boolean(
        help="If selected, the leave will be linked to the employee’s contract - when one year is completed, the employee’s balance will be zero.")
