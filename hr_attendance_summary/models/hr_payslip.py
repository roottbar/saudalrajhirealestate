from odoo import models, api, fields


class PayslipAttendanceSummary(models.Model):
    _inherit = 'hr.payslip'

    summary_ids = fields.Many2many('hr.attendance.summary')

    @api.onchange('employee_id', 'date_from', 'date_to')
    def _onchange_employee(self):
        super(PayslipAttendanceSummary, self)._onchange_employee()
        if (not self.employee_id) or (not self.date_from) or (not self.date_to) or (not self.contract_id):
            return
        self.check_attendance_summary_inputs()

    @api.model
    def check_attendance_summary_inputs(self):
        summary_ids = self.env['hr.attendance.summary'].search([('date', '<=', self.date_to),
                                                                ('date', '>=', self.date_from),
                                                                ('employee_id', '=', self.employee_id.id),
                                                                ('exception', '=', False),
                                                                ('payslip_paid', '=', False)])
        total_late = sum(summary_ids.mapped('total_late'))
        self.summary_ids = summary_ids
        rule_id = self.env.ref('hr_attendance_summary.hr_rule_input_late').id

        if summary_ids:
            input_line = self.input_line_ids.search([('input_type_id', '=', rule_id)], limit=1)
            if input_line:
                input_line.update({'amount': total_late})
            else:
                input_line = self.env['hr.payslip.input'].new({
                    'input_type_id': rule_id,
                    'amount': total_late,
                })
                self.input_line_ids += input_line

    def action_payslip_done(self):
        """
        function used for marking paid overtime
        request.

        """
        for rec in self.summary_ids:
            rec.payslip_paid = True
        return super(PayslipAttendanceSummary, self).action_payslip_done()
