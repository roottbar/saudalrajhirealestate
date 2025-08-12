# -*- coding: utf-8 -*-

from odoo import models, fields, api


class ApprovalRequest(models.Model):
    _name = 'approval.request'
    _description = 'طلبات الموافقة'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'create_date desc'

    name = fields.Char(
        string='اسم الطلب',
        required=True
    )
    
    sale_order_id = fields.Many2one(
        'sale.order',
        string='أمر البيع',
        required=True
    )
    
    product_id = fields.Many2one(
        'product.product',
        string='المنتج',
        required=True
    )
    
    current_price = fields.Float(
        string='السعر الحالي',
        required=True
    )
    
    previous_price = fields.Float(
        string='السعر السابق',
        required=True
    )
    
    partner_identity = fields.Char(
        string='رقم هوية العميل',
        required=True
    )
    
    reason = fields.Text(
        string='سبب الطلب'
    )
    
    state = fields.Selection([
        ('pending', 'في انتظار الموافقة'),
        ('approved', 'تمت الموافقة'),
        ('rejected', 'مرفوض')
    ], string='الحالة', default='pending', tracking=True)
    
    approved_by = fields.Many2one(
        'res.users',
        string='تمت الموافقة من قبل'
    )
    
    rejected_by = fields.Many2one(
        'res.users',
        string='تم الرفض من قبل'
    )
    
    approval_date = fields.Datetime(
        string='تاريخ الموافقة'
    )
    
    rejection_date = fields.Datetime(
        string='تاريخ الرفض'
    )
    
    price_difference = fields.Float(
        string='فرق السعر',
        compute='_compute_price_difference',
        store=True
    )
    
    @api.depends('current_price', 'previous_price')
    def _compute_price_difference(self):
        for record in self:
            record.price_difference = record.previous_price - record.current_price

    def action_approve(self):
        """موافقة الطلب"""
        if not self.env.user.has_group('partner_identity_number.group_rental_manager'):
            raise UserError('ليس لديك صلاحية الموافقة على هذا الطلب.')
            
        self.state = 'approved'
        self.approved_by = self.env.user.id
        self.approval_date = fields.Datetime.now()
        
        # تحديث أمر البيع
        if self.sale_order_id:
            self.sale_order_id.approval_status = 'approved'
            self.sale_order_id.approval_required = False
            
        self.message_post(
            body=f'تمت الموافقة على الطلب من قبل {self.env.user.name}'
        )

    def action_reject(self):
        """رفض الطلب"""
        if not self.env.user.has_group('partner_identity_number.group_rental_manager'):
            raise UserError('ليس لديك صلاحية رفض هذا الطلب.')
            
        self.state = 'rejected'
        self.rejected_by = self.env.user.id
        self.rejection_date = fields.Datetime.now()
        
        # تحديث أمر البيع
        if self.sale_order_id:
            self.sale_order_id.approval_status = 'rejected'
            
        self.message_post(
            body=f'تم رفض الطلب من قبل {self.env.user.name}'
        )