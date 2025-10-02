from odoo import api, fields, models
from odoo import api, fields, models
from datetime import   date
import datetime


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
            t1 = datetime.datetime.strptime(str(day_today), '%Y-%m-%d')
            t2 = datetime.datetime.strptime(str(self.end_power), '%Y-%m-%d')
            t3 = t2 - t1
            self.duration = str(t3.days)


    def notify_power_of_attorney(self):
        legal_over_days = self.env['ir.config_parameter'].sudo().get_param('notify_upcoming_and_overdue.legal_over_days')
        send_notify = self.env['ir.config_parameter'].sudo().get_param('notify_upcoming_and_overdue.send_user_notify')
        today = date.today()
        legal_over_day = today + datetime.timedelta(days=int(legal_over_days))
        if send_notify == 'True':
            upcoming_power_ids = self.env['power.of.attorney'].search([('end_power', '=', legal_over_day)])
            print(upcoming_power_ids)
            for over_power in upcoming_power_ids:
                recipient_partners = []
                user_ids = self.env.user.company_id.notify_user_ids
                for user in user_ids:
                    if user.partner_id:
                        if user.partner_id:
                            recipient_partners.append(user.partner_id.id)
                for partner in recipient_partners:
                    vals = {
                        'subject': "Ending Power of Attorney",
                        'body': "Please note Power of Attorney %s Will End After %s Days at %s" % ( over_power.ref, legal_over_days, legal_over_day),
                        'res_id': over_power.id,
                        'model': 'power.of.attorney',
                        'message_type': 'notification',
                        'partner_ids': [(4, partner)]
                    }
                    message_ids = self.env['mail.message'].create(vals)
                    message = self.env['mail.notification'].create({'mail_message_id': message_ids.id, 'res_partner_id': partner})
