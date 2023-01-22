# -*- coding: utf-8 -*-
import logging

from odoo import models, fields, api, _
from odoo.exceptions import UserError

_logger = logging.getLogger(__name__)


class AccountMove(models.Model):
    _inherit = "account.move"

    def _post(self, soft=True):
        # This code for solve problem creating duplicate names
        for rec in self:
            if rec.state == 'draft' and rec.name and rec.name != '/':
                move = rec.env["account.move"].search_count([("id", "!=", rec.id), ("name", "=", rec.name)])
                if move > 0:
                    rec.name = False
        #############################################

        result = super(AccountMove, self)._post()
        for rec in self:
            if rec.operating_unit_id.journal_sequence_id and rec.move_type == 'entry':
                seq = self.env['ir.sequence'].browse(rec.operating_unit_id.journal_sequence_id.id).next_by_id()
                rec.name = seq
            if rec.operating_unit_id.invoice_sequence_id and rec.move_type != 'entry':
                seq = self.env['ir.sequence'].browse(rec.operating_unit_id.invoice_sequence_id.id).next_by_id()
                rec.name = seq
            # else:
            #     raise UserError(_("لابد من انشاء مسلسل للفواتير والقيود في اعدادات الفروع"))
        return result
