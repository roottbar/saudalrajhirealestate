from odoo import api, fields, models
from datetime import datetime


class PowerOfAttorney(models.Model):
    _name = "power.of.attorney"
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = "Power Of Attorney"
    _rec_name = "ref"

    ref = fields.Char(string='Reference')
    partner = fields.Many2one('res.partner', string='Partner', required=True)
    principal = fields.Char(string='Principal')
    beginning_power = fields.Date(String='Date', default=fields.Date.context_today, tracking=True)
    end_power = fields.Date(tracking=True)
    duration= fields.Integer(string='Duration', compute='calculate_date', tracking=True)
    attachment_attorney = fields.Many2many(comodel_name="ir.attachment", relation="m2m_ir_attachment_attorney_rel",
                                           column1="m2m_id", column2="attachment_id", string="Attachment Power Of Attorney")

    @api.model
    def create(self, vals):
        vals['ref'] = self.env["ir.sequence"].next_by_code('power.of.attorney.sequence')
        return super(PowerOfAttorney, self).create(vals)

    @api.onchange('beginning_power', 'end_power', 'duration')
    def calculate_date(self):
        # contract_obj = self.env['contract'].search([])
        self.duration = 0
        day_today = fields.Date.today()
        if self.beginning_power and self.end_power:
            t1 = datetime.strptime(str(day_today), '%Y-%m-%d')
            t2 = datetime.strptime(str(self.end_power), '%Y-%m-%d')
            t3 = t2 - t1
            self.duration = str(t3.days)


