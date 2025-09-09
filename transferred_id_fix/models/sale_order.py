# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import UserError


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    # الحقول المفقودة التي تسبب أخطاء التحقق
    # Missing fields that cause validation errors
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

    # الطرق المطلوبة للتوافق مع العروض
    # Required methods for view compatibility
    def payment_action_capture(self):
        """التقاط المعاملة المالية"""
        for order in self:
            if order.authorized_transaction_ids:
                # منطق التقاط المعاملة
                order.authorized_transaction_ids.filtered(
                    lambda t: t.state == 'authorized'
                ).action_capture()
                return {
                    'type': 'ir.actions.client',
                    'tag': 'display_notification',
                    'params': {
                        'title': _('Success'),
                        'message': _('Transaction captured successfully'),
                        'type': 'success',
                    }
                }
        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': _('Warning'),
                'message': _('No authorized transactions found'),
                'type': 'warning',
            }
        }

    def payment_action_void(self):
        """إلغاء المعاملة المالية"""
        for order in self:
            if order.authorized_transaction_ids:
                # منطق إلغاء المعاملة
                order.authorized_transaction_ids.filtered(
                    lambda t: t.state == 'authorized'
                ).action_void()
                return {
                    'type': 'ir.actions.client',
                    'tag': 'display_notification',
                    'params': {
                        'title': _('Success'),
                        'message': _('Transaction voided successfully'),
                        'type': 'success',
                    }
                }
        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': _('Warning'),
                'message': _('No authorized transactions found'),
                'type': 'warning',
            }
        }

    def resume_subscription(self):
        """استئناف الاشتراك"""
        for order in self:
            if order.subscription_state == '4_paused':
                order.subscription_state = '2_active'
                return {
                    'type': 'ir.actions.client',
                    'tag': 'display_notification',
                    'params': {
                        'title': _('Success'),
                        'message': _('Subscription resumed successfully'),
                        'type': 'success',
                    }
                }
        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': _('Warning'),
                'message': _('Subscription is not paused'),
                'type': 'warning',
            }
        }

    @api.model
    def create(self, vals):
        """إنشاء طلب جديد مع القيم الافتراضية"""
        # تعيين القيم الافتراضية للحقول الجديدة
        if 'locked' not in vals:
            vals['locked'] = False
        if 'subscription_state' not in vals:
            vals['subscription_state'] = '1_draft'
        
        return super(SaleOrder, self).create(vals)