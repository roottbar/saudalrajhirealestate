# -*- coding: utf-8 -*-
from odoo import models, fields, _
from odoo.exceptions import UserError, ValidationError


class AccountMove(models.Model):
    _inherit = "account.move"

    petty_cash_id = fields.Many2one('petty.cash', string='Petty Cash', copy=False)
    request_feeding_id = fields.Many2one('petty.cash.request.feeding', string='Request Feeding', copy=False)

    def unlink(self):
        for move in self:
            if move.state == 'draft' and move.petty_cash_id:
                raise UserError(_("You cannot delete a journal entry linked to petty cash."))

        return super(AccountMove, self).unlink()

    def write(self, vals):
        force_petty_cash = self._context.get('force_petty_cash')
        for move in self:
            if move.state == 'draft' and move.petty_cash_id and not force_petty_cash:
                raise ValidationError(_("You cannot modify a journal entry linked to petty cash."))

        res = super(AccountMove, self).write(vals)
        return res


class AccountMoveLine(models.Model):
    _inherit = "account.move.line"

    petty_cash_line = fields.Many2one('petty.cash.line', string='Petty Cash Line', copy=False)
    petty_cash_id = fields.Many2one('petty.cash', string='Petty Cash', copy=False)

    def unlink(self):
        force_petty_cash = self._context.get('force_petty_cash')
        for line in self:
            if line.parent_state == 'draft' and line.petty_cash_line and not force_petty_cash:
                raise UserError(_("You cannot delete a journal item linked to petty cash."))

        return super(AccountMoveLine, self).unlink()

    def write(self, vals):
        force_petty_cash = self._context.get('force_petty_cash')
        for line in self:
            if line.parent_state == 'draft' and line.petty_cash_line and not force_petty_cash:
                raise ValidationError(_("You cannot modify a journal item linked to petty cash."))

        res = super(AccountMoveLine, self).write(vals)
        return res
