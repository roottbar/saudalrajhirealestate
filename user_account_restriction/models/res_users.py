# -*- coding: utf-8 -*-

from odoo import models, fields, api


class ResUsers(models.Model):
    _inherit = 'res.users'

    restricted_account_ids = fields.Many2many(
        'account.account',
        'user_restricted_account_rel',
        'user_id',
        'account_id',
        string='Restricted Accounts',
        help='Select accounts that this user should not be able to see or access in financial screens'
    )

    @api.model
    def get_restricted_accounts(self):
        """Get restricted accounts for current user"""
        if self.env.user.restricted_account_ids:
            return self.env.user.restricted_account_ids.ids
        return []

    def write(self, vals):
        """Clear cache when restricted accounts are updated"""
        if 'restricted_account_ids' in vals:
            self.env['ir.model.access'].call_cache_clearing_methods()
            self.env['ir.rule'].clear_caches()
        return super(ResUsers, self).write(vals)