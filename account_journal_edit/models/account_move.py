from odoo import models, fields, api, _
from odoo.exceptions import UserError

class AccountMove(models.Model):
    _inherit = 'account.move'
    
    # إضافة حقل وظيفي للتحقق من الصلاحية
    user_has_journal_edit_group = fields.Boolean(
        string="يمكن تعديل اليومية",
        compute='_compute_user_has_journal_edit_group'
    )
    
    @api.depends_context('uid')
    def _compute_user_has_journal_edit_group(self):
        for move in self:
            move.user_has_journal_edit_group = self.env.user.has_group('account_journal_edit.group_journal_edit_after_confirm')
    
    def write(self, vals):
        # إذا كان المستخدم لديه الصلاحية لتعديل اليومية بعد التأكيد
        if self.env.user.has_group('account_journal_edit.group_journal_edit_after_confirm'):
            # السماح بالتعديل حتى لو كانت الفاتورة مؤكدة
            for move in self:
                if move.state == 'posted':
                    # منع تغيير حالة الفاتورة
                    if 'state' in vals and vals['state'] != 'posted':
                        raise UserError(_('لا يمكن تغيير حالة الفاتورة المؤكدة.'))
                    
                    # السماح بتعديل العناصر الأخرى
                    return super(AccountMove, move).write(vals)
        
        # السلوك الافتراضي للمستخدمين الآخرين
        return super(AccountMove, self).write(vals)
    
    def button_draft(self):
        # منع العودة إلى المسودة للمستخدمين المصرح لهم بالتعديل المباشر
        if self.env.user.has_group('account_journal_edit.group_journal_edit_after_confirm'):
            raise UserError(_('لا يمكن العودة إلى المسودة. يمكنك التعديل مباشرة على الفاتورة المؤكدة.'))
        return super(AccountMove, self).button_draft()
