from odoo import api, fields, models


class Issues(models.Model):
    _name = "issues"
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = "Issues"
    _rec_name = "case_no"

    implement=fields.Boolean()
    case_no = fields.Char(string='Case No.', tracking=True)
    date_of_the_invitation = fields.Date(string='Date of invitation', default= fields.Date.context_today, tracking=True)
    court = fields.Char(string='Court')
    type_of_court = fields.Many2one('type.court', string='Type of court')

    judge = fields.Char(string='Judge', tracking=True)
    prosecut = fields.Char(string='Prosecut', tracking=True)
    defendant = fields.Char(string='Defendant', tracking=True)
    company_id = fields.Many2one('res.company', store=True, copy=False,
                                 string="Company",
                                 default=lambda self: self.env.user.company_id.id)
    currency_id = fields.Many2one('res.currency', string="Currency",
                                  related='company_id.currency_id',
                                  default=lambda
                                      self: self.env.user.company_id.currency_id.id)
    fee = fields.Monetary(string="Fee")
    state = fields.Selection([('unforeseen','Unforeseen'), ('finished','Finished')], string="Status")
    appeal_count = fields.Integer(string='Appeal Count', compute='_compute_appeal_count')
    hearing_count = fields.Integer(string='Hearing Count', compute='_compute_hearing_count')
    verdict_no = fields.Integer(string="Verdict No.")
    date_of_verdict = fields.Date(string='Date Of Verdict', default=fields.Datetime.now, tracking=True)
    court_2 = fields.Char(string='Court')
    attachment_verdict = fields.Many2many(comodel_name="ir.attachment", relation="m2m_ir_verdict_rel",
                                          column1="m2m_id",
                                          column2="attachment_id", string="Attachment Verdict")
    transcript_of_verdict = fields.Text(string='description')



    def _compute_appeal_count(self):
        for rec in self:
            appeal_count = self.env['appeal'].search_count([('issues','=',rec.id)])
            rec.appeal_count = appeal_count

    def action_appeal(self):
        return{
            "type": 'ir.actions.act_window',
            'name': "Appeal",
            'res_model': 'appeal',
            "view_mode": "tree,form",
            'domain': [('issues', '=', self.id)]
        }

    def _compute_hearing_count(self):
        for rec in self:
            hearing_count = self.env['appeal'].search_count([('issues', '=', rec.id)])
            rec.hearing_count = hearing_count

    def action_hearing(self):
        return {
            "type": 'ir.actions.act_window',
            'name': "hearing",
            'res_model': 'hearing',
            "view_mode": "tree,form",
            'domain': [('issues', '=', self.id)]

        }


    def action_invoice(self):
        line_vals = {
            'product_id': self.env.company.product_id.id,
            'name':  'ISSUES',
            'price_unit': self.fee,
            'account_id': self.env.company.product_id.property_account_expense_id.id,
            'tax_ids': [(6, 0, self.env.company.product_id.taxes_id.ids)],
        }
        vals = {
            'partner_id': self.env.company.partner_id.id,
            'move_type': 'out_invoice',
            'invoice_date': self.date_of_the_invitation,
            'invoice_line_ids': [(0, 0, line_vals)],
        }
        inv = self.env['account.move'].create(vals)






