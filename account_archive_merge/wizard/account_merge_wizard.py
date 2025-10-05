# -*- coding: utf-8 -*-
from odoo import api, fields, models, _
from odoo.exceptions import UserError

class AccountMergeWizard(models.TransientModel):
    _name = 'account.merge.wizard'
    _description = 'Account Merge Wizard'
    
    source_account_ids = fields.Many2many(
        'account.account',
        string='Source Accounts',
        required=True
    )
    target_account_id = fields.Many2one(
        'account.account',
        string='Target Account',
        required=True
    )
    reason = fields.Text(
        string='Merge Reason',
        required=True
    )
    
    @api.model
    def default_get(self, fields_list):
        res = super().default_get(fields_list)
        active_ids = self._context.get('active_ids', [])
        if active_ids:
            res['source_account_ids'] = [(6, 0, active_ids)]
        return res
    
    def action_merge_accounts(self):
        """تنفيذ دمج الحسابات"""
        if not self.source_account_ids:
            raise UserError(_('Please select source accounts to merge.'))
        
        if not self.target_account_id:
            raise UserError(_('Please select target account.'))
        
        if self.target_account_id.id in self.source_account_ids.ids:
            raise UserError(_('Target account cannot be in source accounts list.'))
        
        # تنفيذ الدمج
        self.source_account_ids.merge_accounts(
            self.target_account_id.id,
            self.reason
        )
        
        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': _('Success'),
                'message': _('Accounts merged successfully.'),
                'type': 'success',
            }
        }