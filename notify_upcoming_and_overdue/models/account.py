from odoo import fields, models, api
from datetime import date
import datetime


class AccountMove(models.Model):
    _inherit = 'account.move'

    def send_customer_mail(self):
        mail_template = self.env.ref('notify_upcoming_and_overdue.customer_invoice_mail')
        mail_template.send_mail(self.id, force_send=True)
    def notify_upcoming_overdue(self):
        upcoming_days = self.env['ir.config_parameter'].sudo().get_param('notify_upcoming_and_overdue.upcoming_days')
        over_days = self.env['ir.config_parameter'].sudo().get_param('notify_upcoming_and_overdue.over_days')
        send_email = self.env['ir.config_parameter'].sudo().get_param('notify_upcoming_and_overdue.send_email')
        send_notify = self.env['ir.config_parameter'].sudo().get_param('notify_upcoming_and_overdue.send_user_notify')

        today = date.today()
        upcoming_day = today + datetime.timedelta(days=int(upcoming_days))
        over_day = today - datetime.timedelta(days=int(over_days))
        if send_notify == 'True':
            upcoming_move_ids = self.env['account.move'].search([
                ('move_type', '=', 'out_invoice'),
                ('payment_state', 'in', ['partial', 'not_paid']),
                ('invoice_date_due', '=', upcoming_day),
            ])
            for up_move in upcoming_move_ids:
                recipient_partners = []
                # group_id = self.env.ref('account.group_account_manager').id
                # user_ids = self.env['res.users'].search([('groups_id', '=', group_id)])
                user_ids = self.env.user.company_id.notify_user_ids
                for user in user_ids:
                    if user.partner_id:
                        if user.partner_id:
                            recipient_partners.append(user.partner_id.id)
                for partner in recipient_partners:
                    vals = {
                        'subject': "Upcoming Payment",
                        'body': "Please note Payment Invoice %s After %s Days at %s" % (
                        up_move.name, upcoming_days, over_day),
                        'res_id': up_move.id,
                        'model': 'account.move',
                        'message_type': 'notification',
                        'partner_ids': [(4, partner)]
                    }
                    message_ids = self.env['mail.message'].create(vals)
                    message = self.env['mail.notification'].create({'mail_message_id': message_ids.id, 'res_partner_id': partner})

            over_move_ids = self.env['account.move'].search([
                ('move_type', '=', 'out_invoice'),
                ('payment_state', 'in', ['partial', 'not_paid']),
                ('invoice_date_due', '=', over_day),
            ])
            for ov_move in over_move_ids:
                recipient_partners = []
                user_ids = self.env.user.company_id.notify_user_ids
                for user in user_ids:
                    if user.partner_id:
                        if user.partner_id:
                            recipient_partners.append(user.partner_id.id)
                for partner in recipient_partners:
                    vals = {
                        'subject': "Upcoming Payment",
                        'body': "Please note Payment Invoice %s is due in %s Days ago at %s" % (ov_move.name, upcoming_days, over_day),
                        'res_id': ov_move.id,
                        'model': 'account.move',
                        'message_type': 'notification',
                        'partner_ids': [(4, partner)]
                    }
                    message_ids = self.env['mail.message'].create(vals)
                    message = self.env['mail.notification'].create({'mail_message_id': message_ids.id, 'res_partner_id': partner})
        if send_email == 'True':
            over_move_ids = self.env['account.move'].search([
                ('move_type', '=', 'out_invoice'),
                ('payment_state', 'in', ['partial', 'not_paid']),
                ('invoice_date_due', '=', over_day),
            ])
            upcoming_move_ids = self.env['account.move'].search([
                ('move_type', '=', 'out_invoice'),
                ('payment_state', 'in', ['partial', 'not_paid']),
                ('invoice_date_due', '=', upcoming_day),
            ])
            for up_move in upcoming_move_ids:
                up_move.send_customer_mail()
            for ov_move in over_move_ids:
                ov_move.send_customer_mail()
