# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

import logging
from odoo import api, fields, models, _
from odoo.tools.misc import format_date
from odoo.osv import expression
from datetime import date, datetime, timedelta
from odoo.tools import DEFAULT_SERVER_DATE_FORMAT
from odoo.exceptions import UserError

_logger = logging.getLogger(__name__)

class ResPartner(models.Model):
    _name = 'res.partner'
    _inherit = 'res.partner'

    over_due_report = fields.Boolean(string="Over Due Report", copy=False)


    def open_action_followup(self):
        result = super(ResPartner, self).open_action_followup()
        self.over_due_report = False
        return result


    def open_action_over_due(self):
        self.ensure_one()
        self.over_due_report = True
        return {
            'name': _("Overdue Payments for %s", self.display_name),
            'type': 'ir.actions.act_window',
            'view_mode': 'form',
            'views': [[self.env.ref('account_over_due.customer_over_due_form_view').id, 'form']],
            'res_model': 'res.partner',
            'res_id': self.id,
        }

    def get_over_due_html(self):
        """
        Return the content of the follow-up report in HTML
        """
        options = {
            'partner_id': self.id,
            'followup_level': (self.followup_level.id, self.followup_level.delay),
            'keep_summary': True
        }
        return self.env['account.over.due.report'].with_context(print_mode=True, lang=self.lang or self.env.user.lang).get_html(options)
