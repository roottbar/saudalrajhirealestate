# -*- coding: utf-8 -*-

from odoo import models, api


class AccountAccount(models.Model):
    _inherit = 'account.account'

    @api.model
    def search(self, args, offset=0, limit=None, order=None, count=False):
        """Override search to exclude restricted accounts for current user"""
        # Get restricted accounts for current user
        restricted_accounts = self.env.user.restricted_account_ids.ids
        
        if restricted_accounts:
            # Add domain to exclude restricted accounts
            args = args + [('id', 'not in', restricted_accounts)]
        
        return super(AccountAccount, self).search(args, offset=offset, limit=limit, order=order, count=count)

    @api.model
    def name_search(self, name='', args=None, operator='ilike', limit=100):
        """Override name_search to exclude restricted accounts"""
        if args is None:
            args = []
        
        # Get restricted accounts for current user
        restricted_accounts = self.env.user.restricted_account_ids.ids
        
        if restricted_accounts:
            # Add domain to exclude restricted accounts
            args = args + [('id', 'not in', restricted_accounts)]
        
        return super(AccountAccount, self).name_search(name=name, args=args, operator=operator, limit=limit)

    def read(self, fields=None, load='_classic_read'):
        """Override read to prevent access to restricted accounts"""
        # Check if any of the records are restricted for current user
        restricted_accounts = self.env.user.restricted_account_ids.ids
        
        if restricted_accounts:
            # Filter out restricted accounts
            allowed_records = self.filtered(lambda r: r.id not in restricted_accounts)
            return super(AccountAccount, allowed_records).read(fields=fields, load=load)
        
        return super(AccountAccount, self).read(fields=fields, load=load)