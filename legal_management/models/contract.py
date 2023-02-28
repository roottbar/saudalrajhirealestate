from odoo import api, fields, models
from datetime import   date
import datetime


class Contract(models.Model):
    _name = "contract"
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = "Contract"
    _rec_name='ref'


    ref= fields.Char(string='Reference', readonly=True)
    product = fields.Many2one('product.template', string = 'Product')
    beginning_contract = fields.Date(String='Date',default= fields.Date.context_today, tracking=True)
    end_contract = fields.Date(tracking=True)
    duration= fields.Integer(string='Duration', compute='calculate_date', tracking=True)
    attachment_contract = fields.Many2many(comodel_name="ir.attachment", relation="m2m_ir_attachment_contract_rel",
                                           column1="m2m_id", column2="attachment_id", string="Attachment Contract")

    @api.model
    def create (self,vals):
        vals['ref'] = self.env["ir.sequence"].next_by_code('contract.sequence')
        return super(Contract,self).create(vals)

    @api.onchange('beginning_contract', 'end_contract', 'duration')
    def calculate_date(self):
        # contract_obj = self.env['contract'].search([])
        for rec in self:
            rec.duration = 0
            day_today = fields.Date.today()
            if rec.beginning_contract and rec.end_contract:
                t1 = datetime.datetime.strptime(str(day_today), '%Y-%m-%d')
                t2 = datetime.datetime.strptime(str(rec.end_contract), '%Y-%m-%d')
                t3 = t2 - t1
                rec.duration = str(t3.days)

    def _send_notification(self, res_id, note, user_id):
        notification = {
            'activity_type_id': self.env.ref('legal_management.need_approve').id,
            'res_id': res_id,
            'res_model_id': self.env['ir.model'].search([('model', '=', 'contract')], limit=1).id,
            'icon': 'fa-pencil-square-o',
            'date_deadline': fields.Date.today(),
            'user_id': user_id,
            'note': note
        }
        try:
            self.env['mail.activity'].create(notification)
        except:
            pass

    def notify_contract(self):

        upcoming_days = self.env['ir.config_parameter'].sudo().get_param('notify_upcoming_and_overdue.upcoming_days')
        send_notify = self.env['ir.config_parameter'].sudo().get_param('notify_upcoming_and_overdue.send_user_notify')
        today = date.today()
        upcoming_day = today + datetime.timedelta(days=int(upcoming_days))
        print("XXXXXXXXXXXXXXXXXXX", upcoming_day)
        print("XXXXXXXXXXXXXXXXXXX", upcoming_days)
        print("XXXXXXXXXXXXXXXXXXX", send_notify)
        if send_notify == 'True':
            upcoming_contract_ids = self.env['contract'].search([('end_contract', '=', upcoming_day)])
            print(upcoming_contract_ids)
            for up_contract in upcoming_contract_ids:
                recipient_partners = []
                user_ids = self.env.user.company_id.notify_user_ids
                for user in user_ids:
                    if user.partner_id:
                        if user.partner_id:
                            recipient_partners.append(user.partner_id.id)
                for partner in recipient_partners:
                    vals = {
                        'subject': "Ending Contract",
                        'body': "Please note Contract %s Will End After %s Days at %s" % ( up_contract.ref, upcoming_days, upcoming_day),
                        'res_id': up_contract.id,
                        'model': 'contract',
                        'message_type': 'notification',
                        'partner_ids': [(4, partner)]
                    }
                    message_ids = self.env['mail.message'].create(vals)
                    message = self.env['mail.notification'].create({'mail_message_id': message_ids.id, 'res_partner_id': partner})

# @api.model
    # def cron_job(self):
    #     print("################### self",self)
    #     for rec in self :
    #         print(rec)
    #     contract_ids = self.env['contract'].search([])
    #         # self.env.company.FIELD_NAME
    #         if rec.duration  == 2 :
    #             msg = "dsdsds"
    #             # rec._send_notification(rec,msg,2)


