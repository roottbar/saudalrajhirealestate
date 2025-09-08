# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import UserError


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    # إضافة الحقول المفقودة التي تسبب أخطاء التحقق
    transferred_id = fields.Many2one(
        'sale.order',
        string='Transferred Order',
        help='Reference to transferred order for compatibility'
    )
    
    locked = fields.Boolean(
        string='Locked',
        default=False,
        help='Field for compatibility with payment views'
    )
    
    authorized_transaction_ids = fields.Many2many(
        'payment.transaction',
        string='Authorized Transactions',
        domain=[('state', '=', 'authorized')],
        help='Authorized payment transactions for this order'
    )
    
    subscription_state = fields.Selection([
        ('1_draft', 'Draft'),
        ('2_active', 'Active'),
        ('3_closed', 'Closed'),
        ('4_paused', 'Paused'),
    ], string='Subscription State', default='1_draft',
       help='State of subscription for compatibility')

    def payment_action_capture(self):
        """
        طريقة لالتقاط المعاملات المالية المعتمدة
        """
        if not self.authorized_transaction_ids:
            raise UserError(_('No authorized transactions found to capture.'))
        
        for transaction in self.authorized_transaction_ids:
            if transaction.state == 'authorized':
                try:
                    transaction._set_done()
                    transaction.write({'state': 'done'})
                except Exception as e:
                    raise UserError(_('Failed to capture transaction: %s') % str(e))
        
        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': _('Success'),
                'message': _('Transactions captured successfully.'),
                'type': 'success',
            }
        }

    def payment_action_void(self):
        """
        طريقة لإلغاء المعاملات المالية المعتمدة
        """
        if not self.authorized_transaction_ids:
            raise UserError(_('No authorized transactions found to void.'))
        
        for transaction in self.authorized_transaction_ids:
            if transaction.state == 'authorized':
                try:
                    transaction.write({'state': 'cancel'})
                except Exception as e:
                    raise UserError(_('Failed to void transaction: %s') % str(e))
        
        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': _('Success'),
                'message': _('Transactions voided successfully.'),
                'type': 'success',
            }
        }

    def resume_subscription(self):
        """
        طريقة لاستئناف الاشتراك المتوقف
        """
        if self.subscription_state != '4_paused':
            raise UserError(_('Only paused subscriptions can be resumed.'))
        
        self.write({'subscription_state': '2_active'})
        
        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': _('Success'),
                'message': _('Subscription resumed successfully.'),
                'type': 'success',
            }
        }

    @api.model
    def create(self, vals):
        """
        تخصيص إنشاء الطلب لضمان التوافق
        """
        # تعيين القيم الافتراضية للحقول الجديدة
        if 'locked' not in vals:
            vals['locked'] = False
        if 'subscription_state' not in vals:
            vals['subscription_state'] = '1_draft'
        
        return super(SaleOrder, self).create(vals)