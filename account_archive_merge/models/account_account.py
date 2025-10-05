# -*- coding: utf-8 -*-
from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError

class AccountAccount(models.Model):
    _inherit = 'account.account'
    
    # إضافة حقول الأرشفة
    is_archived = fields.Boolean(
        string='Archived',
        default=False,
        help='Mark this account as archived'
    )
    archived_date = fields.Datetime(
        string='Archived Date',
        readonly=True
    )
    archived_by = fields.Many2one(
        'res.users',
        string='Archived By',
        readonly=True
    )
    archive_reason = fields.Text(
        string='Archive Reason',
        readonly=True
    )
    
    # حقول الدمج
    merged_into_account_id = fields.Many2one(
        'account.account',
        string='Merged Into Account',
        readonly=True
    )
    merged_date = fields.Datetime(
        string='Merged Date',
        readonly=True
    )
    merged_by = fields.Many2one(
        'res.users',
        string='Merged By',
        readonly=True
    )
    
    def action_archive_account(self):
        """أرشفة الحساب"""
        for account in self:
            if account.is_archived:
                raise UserError(_('Account %s is already archived.') % account.name)
            
            # التحقق من وجود قيود محاسبية
            if account.move_line_ids:
                raise UserError(_('Cannot archive account %s because it has journal entries.') % account.name)
            
            account.write({
                'is_archived': True,
                'archived_date': fields.Datetime.now(),
                'archived_by': self.env.user.id,
                'active': False
            })
            
            # إنشاء سجل في الأرشيف
            self.env['account.archive.log'].create({
                'account_id': account.id,
                'action_type': 'archive',
                'date': fields.Datetime.now(),
                'user_id': self.env.user.id,
                'reason': account.archive_reason or 'Manual archive'
            })
    
    def action_unarchive_account(self):
        """إلغاء أرشفة الحساب"""
        for account in self:
            if not account.is_archived:
                raise UserError(_('Account %s is not archived.') % account.name)
            
            account.write({
                'is_archived': False,
                'archived_date': False,
                'archived_by': False,
                'archive_reason': False,
                'active': True
            })
            
            # إنشاء سجل في الأرشيف
            self.env['account.archive.log'].create({
                'account_id': account.id,
                'action_type': 'unarchive',
                'date': fields.Datetime.now(),
                'user_id': self.env.user.id,
                'reason': 'Manual unarchive'
            })
    
    def merge_accounts(self, target_account_id, reason=''):
        """دمج الحسابات"""
        target_account = self.env['account.account'].browse(target_account_id)
        
        for account in self:
            if account.id == target_account_id:
                continue
                
            # التحقق من إمكانية الدمج
            if account.account_type != target_account.account_type:
                raise UserError(_('Cannot merge accounts with different account types.'))
            
            # نقل القيود المحاسبية
            account.move_line_ids.write({'account_id': target_account_id})
            
            # تحديث الحساب المدموج
            account.write({
                'merged_into_account_id': target_account_id,
                'merged_date': fields.Datetime.now(),
                'merged_by': self.env.user.id,
                'is_archived': True,
                'active': False
            })
            
            # إنشاء سجل الدمج
            self.env['account.archive.log'].create({
                'account_id': account.id,
                'target_account_id': target_account_id,
                'action_type': 'merge',
                'date': fields.Datetime.now(),
                'user_id': self.env.user.id,
                'reason': reason or 'Account merge'
            })