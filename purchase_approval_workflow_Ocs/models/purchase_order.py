from odoo import models, fields, api, _

class PurchaseOrder(models.Model):
    _inherit = 'purchase.order'

    approval_level = fields.Selection([
        ('draft', 'مسودة'),
        ('level1', 'في انتظار الموافقة الأولى'),
        ('level2', 'في انتظار الموافقة الثانية'),
        ('level3', 'في انتظار الموافقة الثالثة'),
        ('approved', 'تمت الموافقة'),
        ('rejected', 'مرفوض')
    ], string='مستوى الموافقة', default='draft', tracking=True)

    def action_request_approval(self):
        for order in self:
            if order.approval_level == 'draft':
                order.write({'approval_level': 'level1'})
            elif order.approval_level == 'level1':
                order.write({'approval_level': 'level2'})
            elif order.approval_level == 'level2':
                order.write({'approval_level': 'level3'})
        return True

    def action_approve_level1(self):
        self.ensure_one()
        if self.approval_level == 'level1':
            self.write({'approval_level': 'level2'})
            return {
                'effect': {
                    'fadeout': 'slow',
                    'message': 'تمت الموافقة الأولى بنجاح',
                    'type': 'rainbow_man',
                }
            }

    def action_approve_level2(self):
        self.ensure_one()
        if self.approval_level == 'level2':
            self.write({'approval_level': 'level3'})
            return {
                'effect': {
                    'fadeout': 'slow',
                    'message': 'تمت الموافقة الثانية بنجاح',
                    'type': 'rainbow_man',
                }
            }

    def action_approve_level3(self):
        self.ensure_one()
        if self.approval_level == 'level3':
            self.write({'approval_level': 'approved'})
            self.button_confirm()  # تأكيد أمر الشراء
            return {
                'effect': {
                    'fadeout': 'slow',
                    'message': 'تمت الموافقة النهائية بنجاح',
                    'type': 'rainbow_man',
                }
            }

    def action_reject(self):
        self.ensure_one()
        self.write({'approval_level': 'rejected'})
        return {
            'effect': {
                'fadeout': 'slow',
                'message': 'تم رفض أمر الشراء',
                'type': 'rainbow_man',
            }
        }