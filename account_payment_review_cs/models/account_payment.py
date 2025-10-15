# -*- coding: utf-8 -*-
from odoo import models, fields, _
from odoo.exceptions import UserError


class AccountPayment(models.Model):
    _inherit = 'account.payment'

    # Add an intermediate review state
    # Extend the base payment state with a 'review' option using the
    # standard selection_add pattern. Avoid custom ondelete to prevent
    # selection reflection KeyError during module install.
    # Explicitly set the full selection to satisfy Odoo's field setup
    # assertion and include the new 'review' state.
    state = fields.Selection(selection=[
        ('draft', 'Draft'),
        ('review', 'Reviewed'),
        ('posted', 'Posted'),
        ('cancelled', 'Cancelled'),
    ])

    def action_review(self):
        # Require either review or confirm group to review
        user = self.env.user
        if not (user.has_group('account_payment_review_cs.group_payment_review') or
                user.has_group('account_payment_review_cs.group_payment_confirm')):
            raise UserError(_('You do not have permission to review payments.'))

        for payment in self:
            if payment.state != 'draft':
                raise UserError(_('Only draft payments can be reviewed.'))
            payment.state = 'review'
        return True

    def action_post(self):
        # Enforce confirm permission to post payments
        user = self.env.user
        if not user.has_group('account_payment_review_cs.group_payment_confirm'):
            raise UserError(_('You do not have permission to confirm payments.'))

        # Allow posting from 'review' by resetting to 'draft' before super
        review_to_draft = self.filtered(lambda p: p.state == 'review')
        if review_to_draft:
            review_to_draft.write({'state': 'draft'})
        return super(AccountPayment, self).action_post()
