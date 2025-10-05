# -*- coding: utf-8 -*-
from odoo import api, fields, models, _
from odoo.exceptions import UserError

class AccountArchiveWizard(models.TransientModel):
    _name = 'account.archive.wizard'
    _description = 'Account Archive Wizard'
    
    account_ids = fields.Many2many(
        'account.account',
        string='Accounts to Archive',
        required=True
    )
    reason = fields.Text(
        string='Archive Reason',
        required=True
    )
    
    @api.model
    def default_get(self, fields_list):
        res = super().default_get(fields_list)
        active_ids = self._context.get('active_ids', [])
        if active_ids:
            res['account_ids'] = [(6, 0, active_ids)]
        return res
    
    def action_archive_accounts(self):
        """تنفيذ أرشفة الحسابات"""
        for account in self.account_ids:
            account.archive_reason = self.reason
            account.action_archive_account()
        
        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': _('Success'),
                'message': _('Accounts archived successfully.'),
                'type': 'success',
            }
        }