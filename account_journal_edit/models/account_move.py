from odoo import models, fields, api, _
from odoo.exceptions import UserError


class AccountMove(models.Model):
    _inherit = 'account.move'

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