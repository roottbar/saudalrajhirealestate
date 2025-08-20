from odoo import models, fields, api, _
from odoo.exceptions import UserError


class AccountMoveLine(models.Model):
    _inherit = 'account.move.line'

    def write(self, vals):
        # إذا كان المستخدم لديه الصلاحية لتعديل اليومية بعد التأكيد
        if self.env.user.has_group('account_journal_edit.group_journal_edit_after_confirm'):
            # السماح بتعديل الحساب حتى لو كانت الفاتورة مؤكدة
            for line in self:
                if line.move_id.state == 'posted' and 'account_id' in vals:
                    # التحقق من أن الحساب الجديد صالح
                    new_account = self.env['account.account'].browse(vals['account_id'])
                    if not new_account:
                        raise UserError(_('الحساب المحدد غير صالح.'))

                    # السماح بتعديل الحساب
                    return super(AccountMoveLine, line).write(vals)

        # السلوك الافتراضي للمستخدمين الآخرين
        return super(AccountMoveLine, self).write(vals)