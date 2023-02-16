# -*- coding: utf-8 -*-
import logging

from odoo import models, fields, api, _
from odoo.exceptions import UserError
from datetime import date

_logger = logging.getLogger(__name__)


class AccountMove(models.Model):
    _inherit = "account.move"

    seq_created = fields.Boolean("Sequence Created")
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
            #ToDo: Abdulrhman Code
            # if rec.seq_created != True:
                # if rec.operating_unit_id.journal_sequence_id and rec.move_type == 'entry':
                #     branch = str(rec.operating_unit_id.code)
                #     type = str(rec.journal_id.code)
                #     journal = str(rec.journal_id.name).split()[0]
                #     year = str(date.today().year)
                #     next = str(rec.operating_unit_id.journal_sequence_id.number_next_actual)
                #     rec.operating_unit_id.journal_sequence_id.number_next_actual += 1
                #     seq_name = branch + '/' + type + '/' + journal + '/' + year + '/' + next
                #     print(">>>>>>>>>>>>>>>>>>>>>>>>. ", seq_name)
                #     rec.name = seq_name
                #     rec.seq_created = True
                # if rec.operating_unit_id.invoice_sequence_id and rec.move_type != 'entry':
                #     rec.name = ''
                #     branch = str(rec.operating_unit_id.code)
                #     type = str(rec.journal_id.code)
                #     journal = str(rec.journal_id.name).split()[0]
                #     year = str(date.today().year)
                #     next = str(rec.operating_unit_id.invoice_sequence_id.number_next_actual)
                #     rec.operating_unit_id.invoice_sequence_id.number_next_actual += 1
                #     seq_name = branch + '/' + type + '/' + journal + '/' + year + '/' + next
                #     print(">>>>>>>>>>>>>>>>>>>>22>>>>. ", seq_name)
                #     rec.name= seq_name
                #     rec.seq_created = True
            # else:
            #     raise UserError(_("لابد من انشاء مسلسل للفواتير والقيود في اعدادات الفروع"))
        return result
