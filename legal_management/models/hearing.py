from odoo import api, fields, models

class Hearing(models.Model):
    _name = "hearing"
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = "Hearing"
    _rec_name='issues'

    issues = fields.Many2one('issues',string="Issues",tracking=True)
    court = fields.Char(string='Court', tracking=True)
    hearing_time = fields.Datetime(string='Date and Time Hearing', default= fields.Datetime.now, tracking=True)
    transcript_of_hearing = fields.Text(string='Transcript Of Hearing',tracking=True)
    attachment_hearing = fields.Many2many(comodel_name="ir.attachment", relation="m2m_ir_hearing_rel",
                                     column1="m2m_id", column2="attachment_id", string="Attachment Hearing")
    name = fields.Char(string='Name')




