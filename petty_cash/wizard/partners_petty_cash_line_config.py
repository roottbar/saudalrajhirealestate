# -*- coding: utf-8 -*-

from odoo import fields, models, api, _
from odoo.exceptions import ValidationError


class PartnersPettyCashLineConfigWizard(models.TransientModel):
    _name = 'partners.petty.cash.line.config'
    _description = 'Partners of Petty Cash Line Config'

    partner_ids = fields.Many2many('res.partner', string='Partners')

    @api.model
    def default_get(self, fields):
        res = super(PartnersPettyCashLineConfigWizard, self).default_get(fields)

        partner_ids = self.env["ir.config_parameter"].sudo().get_param('petty_cash.partner_ids', '[]')

        # check partners exists or not
        partners = self.env['res.partner'].search([('id', 'in', eval(partner_ids))])

        res.update({'partner_ids': [(6, 0, partners.ids)]})

        return res

    def execute(self):
        config_parameters = self.env["ir.config_parameter"].sudo()

        # check if remove partner from settings that is already used in petty cash
        partner_ids = eval(config_parameters.get_param('petty_cash.partner_ids', '[]'))

        if partner_ids:
            diff_partners = list(set(partner_ids) - set(self.partner_ids.ids))

            if diff_partners:
                petty_cash_lines = self.env['petty.cash.line'].search([('partner_id', 'in', diff_partners)])

                if petty_cash_lines:
                    raise ValidationError(
                        _("You cannot delete this partners from settings,there are already used in petty cash"))

        # update partners of petty cash Line in settings
        config_parameters.set_param("petty_cash.partner_ids", str(self.partner_ids.ids))
        return True
