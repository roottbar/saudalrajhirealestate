# -*- coding: utf-8 -*-
from odoo import models


class PartnerLedger(models.Model):
    """
        Extends res.partner to add functionality for opening the partner ledger wizard.
    """
    _inherit = 'res.partner'

    def action_open_wizard_ledger(self):
        """
        Opens the partner ledger wizard in a new window.
        """
        action = (self.env["ir.actions.actions"]._for_xml_id
                  ("tk_partner_ledger.partner_ledger_wizard_action"))
        action['context'] = {
            'active_id': self._context.get('active_id'),
        }
        return action
