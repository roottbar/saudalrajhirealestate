# -*- coding: utf-8 -*-
from odoo import api, fields, models

class AccountArchiveLog(models.Model):
    _name = 'account.archive.log'
    _description = 'Account Archive Log'
    _order = 'date desc'
    
    account_id = fields.Many2one(
        'account.account',
        string='Account',
        required=True
    )
    target_account_id = fields.Many2one(
        'account.account',
        string='Target Account'
    )
    action_type = fields.Selection([
        ('archive', 'Archive'),
        ('unarchive', 'Unarchive'),
        ('merge', 'Merge')
    ], string='Action Type', required=True)
    date = fields.Datetime(
        string='Date',
        required=True,
        default=fields.Datetime.now
    )
    user_id = fields.Many2one(
        'res.users',
        string='User',
        required=True,
        default=lambda self: self.env.user
    )
    reason = fields.Text(string='Reason')