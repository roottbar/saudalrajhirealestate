from odoo import fields, models, api
from datetime import date
import datetime


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    def send_up_contract_mail(self):
        mail_template = self.env.ref('notify_upcoming_and_overdue.customer_up_contract_mail')
        mail_template.send_mail(self.id, force_send=True)
    def notify_upcoming_overdue_contract(self):
        upcoming_days = self.env['ir.config_parameter'].sudo().get_param('notify_upcoming_and_overdue.upcoming_days')
        over_days = self.env['ir.config_parameter'].sudo().get_param('notify_upcoming_and_overdue.over_days')
        send_email = self.env['ir.config_parameter'].sudo().get_param('notify_upcoming_and_overdue.send_email')
        send_notify = self.env['ir.config_parameter'].sudo().get_param('notify_upcoming_and_overdue.send_user_notify')

        today = date.today()
        upcoming_day = today + datetime.timedelta(days=int(upcoming_days))
        over_day = today - datetime.timedelta(days=int(over_days))
        if send_notify == 'True':
            upcoming_contract_ids = self.env['sale.order'].search([
                ('is_rental_order', '=', True),
                ('todate', '>=', datetime.datetime.combine(upcoming_day, datetime.time(0, 0, 0))),
                ('todate', '<=', datetime.datetime.combine(upcoming_day, datetime.time(23, 59, 59))),
                ('state', '=', 'sale'),
            ])
            for up_contract in upcoming_contract_ids:
                recipient_partners = []
                user_ids = self.env.user.company_id.notify_user_ids
                for user in user_ids:
                    if user.partner_id:
                        if user.partner_id:
                            recipient_partners.append(user.partner_id.id)
                for partner in recipient_partners:
                    vals = {
                        'subject': "Upcoming Contract",
                        'body': "Please note Contract Will Start %s After %s Days at %s" % (up_contract.name, upcoming_days, over_day),
                        'res_id': up_contract.id,
                        'model': 'sale.order',
                        'message_type': 'notification',
                        'partner_ids': [(4, partner)]
                    }
                    message_ids = self.env['mail.message'].create(vals)
                    message = self.env['mail.notification'].create({'mail_message_id': message_ids.id, 'res_partner_id': partner})


            over_contract_ids = self.env['sale.order'].search([
                ('is_rental_order', '=', True),
                ('todate', '>=', datetime.datetime.combine(over_day, datetime.time(0, 0, 0))),
                ('todate', '<=', datetime.datetime.combine(over_day, datetime.time(23,59,59))),
                ('state', '=', 'sale'),
            ])

            for ov_contract in over_contract_ids:
                recipient_partners = []
                user_ids = self.env.user.company_id.notify_user_ids
                for user in user_ids:
                    if user.partner_id:
                        if user.partner_id:
                            recipient_partners.append(user.partner_id.id)
                for partner in recipient_partners:
                    vals = {
                        'subject': "Upcoming Contract",
                        'body': "Please note Contract %s was due in %s Days ago at %s" % (ov_contract.name, upcoming_days, over_day),
                        'res_id': ov_contract.id,
                        'model': 'sale.order',
                        'message_type': 'notification',
                        'partner_ids': [(4, partner)]
                    }
                    message_ids = self.env['mail.message'].create(vals)
                    message = self.env['mail.notification'].create({'mail_message_id': message_ids.id, 'res_partner_id': partner})
        if send_email == 'True':
            over_contract_ids = self.env['sale.order'].search([
                ('is_rental_order', '=', True),
                ('todate', '>=', datetime.datetime.combine(over_day, datetime.time(0, 0, 0))),
                ('todate', '<=', datetime.datetime.combine(over_day, datetime.time(23,59,59))),
                ('state', '=', 'sale'),
            ])
            upcoming_contract_ids = self.env['sale.order'].search([
                ('is_rental_order', '=', True),
                ('todate', '>=', datetime.datetime.combine(upcoming_day, datetime.time(0, 0, 0))),
                ('todate', '<=', datetime.datetime.combine(upcoming_day, datetime.time(23, 59, 59))),
                ('state', '=', 'sale'),
            ])
            for up_contract in upcoming_contract_ids:
                up_contract.send_up_contract_mail()
            for ov_contract in over_contract_ids:
                ov_contract.send_up_contract_mail()
