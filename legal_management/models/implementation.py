from odoo import api, fields, models

class Implementation(models.Model):
    _name = "implementation"
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = "Implementation"
    _rec_name = "type_verdict"

    state = fields.Selection([('new','New'), ('in-progress','In Progress'),('done','Done')], string="Status")
    type_verdict = fields.Selection([('trial','Trial'), ('appeal','Appeal')], string="Type of court verdict", default='trial', required=True)
    appeal = fields.Many2one('appeal',string='Appeal')
    issue = fields.Many2one('issues',string='Issue')
    attachment_implementation = fields.Many2many(comodel_name="ir.attachment", relation="m2m_ir_implementation_rel",
                                      column1="m2m_id", column2="attachment_id", string="Attachment implementation")

    @api.onchange('state')
    def onchange_state(self):
        if self.state =='done':
            self.issue.implement = True
