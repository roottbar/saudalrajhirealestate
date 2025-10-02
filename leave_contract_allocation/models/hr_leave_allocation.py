from odoo import models, api, fields
from dateutil.relativedelta import relativedelta
from datetime import date, timedelta


class LeaveAllocation(models.Model):
    _inherit = 'hr.leave.allocation'

    allocation_per_contract = fields.Boolean(related='holiday_status_id.allocation_per_contract')

    def flush_allocation(self):
        self.number_of_days = self.leaves_taken

    def check_leave_allocation(self):
        for rec in self.env['hr.leave.allocation'].search([('allocation_per_contract', '=', True)]):
            if rec.employee_id.contract_id:
                date_start = rec.employee_id.contract_id.date_start + relativedelta(years=1)
                today = date.today()
                while date_start <= today:
                    if today == date_start:
                        rec.flush_allocation()
                    date_start += relativedelta(years=1)
