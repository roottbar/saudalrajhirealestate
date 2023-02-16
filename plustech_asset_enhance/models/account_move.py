# -*- coding: utf-8 -*-

from odoo import models, fields


class AccountMove(models.Model):
    _inherit = "account.move"

    state = fields.Selection(selection=[
        ('draft', 'Draft'),
        ('review', 'Reviewed'),
        ('posted', 'Posted'),
        ('cancel', 'Cancelled'),
    ], string='Status', required=True, readonly=True, copy=False, tracking=True, default='draft')

    def action_review(self):
        self.state = 'review'
