# -*- coding: utf-8 -*-

from odoo import models, fields, api
from odoo.exceptions import UserError


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    partner_identity_number = fields.Char(
        related='partner_id.identity_number',
        string='رقم الهوية/الإقامة',
        readonly=True,
        store=True
    )
    
    approval_required = fields.Boolean(
        string='يتطلب موافقة المدير',
        default=False
    )
    
    approval_status = fields.Selection([
        ('pending', 'في انتظار الموافقة'),
        ('approved', 'تمت الموافقة'),
        ('rejected', 'مرفوض')
    ], string='حالة الموافقة', default=False)
    
    approval_request_id = fields.Many2one(
        'approval.request',
        string='طلب الموافقة'
    )

    @api.model
    def create(self, vals):
        """فحص الأسعار عند إنشاء أمر تأجير جديد"""
        order = super().create(vals)
        if order.is_rental_order and order.partner_id:
            order._check_rental_price_reduction()
        return order

    def write(self, vals):
        """فحص الأسعار عند تعديل أمر التأجير"""
        result = super().write(vals)
        if 'order_line' in vals:
            for order in self:
                if order.is_rental_order and order.partner_id:
                    order._check_rental_price_reduction()
        return result

    def _check_rental_price_reduction(self):
        """فحص تقليل الأسعار في أوامر التأجير"""
        if not self.partner_id.identity_number:
            return
            
        # البحث عن أوامر تأجير سابقة لنفس العميل
        previous_orders = self.search([
            ('partner_id.identity_number', '=', self.partner_id.identity_number),
            ('is_rental_order', '=', True),
            ('state', 'in', ['sale', 'done']),
            ('id', '!=', self.id)
        ])
        
        if not previous_orders:
            return
            
        # فحص المنتجات والأسعار
        for line in self.order_line:
            if not line.product_id:
                continue
                
            # البحث عن نفس المنتج في الأوامر السابقة
            previous_lines = previous_orders.mapped('order_line').filtered(
                lambda l: l.product_id.id == line.product_id.id
            )
            
            if previous_lines:
                # أخذ أعلى سعر من الأوامر السابقة
                max_previous_subtotal = max(previous_lines.mapped('price_subtotal'))
                
                if line.price_subtotal < max_previous_subtotal:
                    # إنشاء طلب موافقة
                    self._create_approval_request(line, max_previous_subtotal)
                    self.approval_required = True
                    self.approval_status = 'pending'

    def _create_approval_request(self, order_line, previous_price):
        """إنشاء طلب موافقة المدير"""
        approval_request = self.env['approval.request'].create({
            'name': f'طلب موافقة تقليل السعر - {self.name}',
            'sale_order_id': self.id,
            'product_id': order_line.product_id.id,
            'current_price': order_line.price_subtotal,
            'previous_price': previous_price,
            'partner_identity': self.partner_id.identity_number,
            'reason': f'تقليل سعر المنتج {order_line.product_id.name} من {previous_price} إلى {order_line.price_subtotal}',
            'state': 'pending'
        })
        
        self.approval_request_id = approval_request.id
        
        # إرسال إشعار للمديرين
        managers = self.env.ref('partner_identity_number.group_rental_manager').users
        approval_request.message_post(
            body=f'طلب موافقة جديد على تقليل السعر للعميل: {self.partner_id.name}',
            partner_ids=managers.mapped('partner_id').ids
        )

    def action_confirm(self):
        """منع تأكيد الطلب إذا كان يتطلب موافقة ولم تتم الموافقة"""
        for order in self:
            if order.approval_required and order.approval_status != 'approved':
                raise UserError(
                    'لا يمكن تأكيد هذا الطلب. يتطلب موافقة المدير أولاً.'
                )
        return super().action_confirm()

    def action_approve_price_reduction(self):
        """موافقة المدير على تقليل السعر"""
        if not self.env.user.has_group('partner_identity_number.group_rental_manager'):
            raise UserError('ليس لديك صلاحية الموافقة على هذا الطلب.')
            
        self.approval_status = 'approved'
        self.approval_required = False
        
        if self.approval_request_id:
            self.approval_request_id.state = 'approved'
            self.approval_request_id.approved_by = self.env.user.id
            self.approval_request_id.approval_date = fields.Datetime.now()
            
        self.message_post(
            body=f'تمت موافقة المدير {self.env.user.name} على تقليل السعر'
        )

    def action_reject_price_reduction(self):
        """رفض المدير لتقليل السعر"""
        if not self.env.user.has_group('partner_identity_number.group_rental_manager'):
            raise UserError('ليس لديك صلاحية رفض هذا الطلب.')
            
        self.approval_status = 'rejected'
        
        if self.approval_request_id:
            self.approval_request_id.state = 'rejected'
            self.approval_request_id.rejected_by = self.env.user.id
            self.approval_request_id.rejection_date = fields.Datetime.now()
            
        self.message_post(
            body=f'تم رفض الطلب من قبل المدير {self.env.user.name}'
        )