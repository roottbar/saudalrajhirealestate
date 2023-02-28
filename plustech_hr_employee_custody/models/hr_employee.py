from odoo import fields, models, api


class HrEmployee(models.Model):
    _inherit = 'hr.employee'

    custody_count = fields.Integer(string='Custodies', compute='compute_custody')

    def compute_custody(self):
        for record in self:
            custodies = self.env['employee.custody'].search([('employee_id', '=', record.id)])
            record.custody_count = len(custodies)

    def action_custody_view(self):
        self.ensure_one()
        result = self.env.ref('plustech_hr_employee_custody.employee_custody_action').read()[0]
        result['domain'] = [('employee_id', '=', self.id)]
        return result


