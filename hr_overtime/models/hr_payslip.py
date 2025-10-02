from odoo import models, api, fields


class PayslipOverTime(models.Model):
    _inherit = 'hr.payslip'

    overtime_ids = fields.Many2many('hr.overtime')

    @api.onchange('employee_id', 'date_from', 'date_to')
    def _onchange_employee(self):
        super(PayslipOverTime, self)._onchange_employee()
        if (not self.employee_id) or (not self.date_from) or (not self.date_to) or (not self.contract_id):
            return
        self.input_line_ids = False
        self.input_line_ids = self.get_overtime_inputs()

    @api.model
    def get_overtime_inputs(self):
        res = []
        overtime_ids = self.env['hr.overtime'].search([('date', '<', self.date_to),
                                                      ('date', '>', self.date_from),
                                                      ('employee_id', '=', self.employee_id.id),
                                                      ('state', '=', 'approved'), ('payslip_paid', '=', False)])
        overtime_amount = sum(overtime_ids.mapped('overtime_amount'))
        self.overtime_ids = overtime_ids
        if overtime_ids:

            vals = {
                'input_type_id': self.env.ref('hr_overtime.hr_rule_input_overtime').id,
                'amount': overtime_amount,
            }
            res = [(0, 0, vals)]
        return res

    def action_payslip_done(self):
        """
        function used for marking paid overtime
        request.

        """
        for rec in self.overtime_ids:
           rec.payslip_paid = True
        return super(PayslipOverTime, self).action_payslip_done()
