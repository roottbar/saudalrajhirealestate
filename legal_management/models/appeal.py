from odoo import api, fields, models

class Appeal(models.Model):
    _name = "appeal"
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = "Appeal"
    _rec_name='issues'

    state = fields.Selection([('unforeseen','Unforeseen'), ('finished','Finished')], string="Status")
    issues = fields.Many2one('issues',string="Issues",tracking=True)
    date_of_appeal = fields.Date(string='Date Of Appeal',default= fields.Datetime.now, tracking=True)
    judge = fields.Char(string='Judge', tracking=True, related='issues.judge',readonly=False)
    description_of_appeal=fields.Text(string='description')
    name = fields.Char(string='Name')

    verdict_no = fields.Integer(string="Verdict No.")
    date_of_verdict = fields.Date(string='Date Of Verdict', default=fields.Datetime.now, tracking=True)
    court_2 = fields.Char(string='Court')
    attachment_verdict = fields.Many2many(comodel_name="ir.attachment", relation="m2m_ir_attachment_verdict_rel",
                                          column1="m2m_id",
                                          column2="attachment_id", string="Attachment Verdict")
    transcript_of_verdict = fields.Text(string='description')





