# -*- coding: utf-8 -*-

from odoo import fields, models, _


class PettyCashTransfersWizard(models.TransientModel):
    _name = 'petty.cash.transfer.wizard'
    _description = 'Petty Cash Transfers'

    managers = fields.Many2many('res.users', string='Managers', domain=lambda self: [
        ("groups_id", "=", self.sudo().env.ref("petty_cash.group_petty_cash_manager").id)])
    notes = fields.Text(string="Notes")

    def action_transfer(self):
        petty_cash_id = self.env['petty.cash'].browse(self._context['active_id'])

        current_user = self.env.user
        # send message to managers

        if self.managers:
            partners = []
            petty_cash_transfer_obj = self.env['petty.cash.transfer']

            for manager in self.managers:
                if current_user != manager:
                    if manager.partner_id.id not in petty_cash_id.message_partner_ids.ids:
                        petty_cash_id.add_follower_id(petty_cash_id.id, manager.partner_id)

                    partners.append(manager.partner_id.id)

                    vals = {
                        'description': self.notes,
                        'manager': manager.id,
                        'petty_cash_id': petty_cash_id.id
                    }
                    petty_cash_transfer_obj.create(vals)

            if partners:
                msg = _("<b>Transfer petty cash %s, created by %s</b>") % (
                    petty_cash_id.name, petty_cash_id.create_uid.name)
                if self.notes:
                    msg += '<br/>' + self.notes

                msg += _('''<ul>
                                    <li>Date: %s</li>
                                    <li>Responsible Box: %s</li>
                                    <li>Box: %s</li>
                                </ul>''') % (
                    petty_cash_id.start_date, petty_cash_id.responsible_id.name, petty_cash_id.user_rule.name)

                petty_cash_id.message_post(partner_ids=partners, body=msg, subtype='mail.mt_comment')
        return True
