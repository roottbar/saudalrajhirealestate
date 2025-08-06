from odoo import models, fields, api

class AccountPayment(models.Model):
    _inherit = 'account.payment'
    
    analytic_account_id = fields.Many2one(
        'account.analytic.account',
        string='الحساب التحليلي',
        readonly=True,
        states={'draft': [('readonly', False)]}
    )
    analytic_tag_ids = fields.Many2many(
        'account.analytic.tag',
        string='الوسوم التحليلية',
        readonly=True,
        states={'draft': [('readonly', False)]}
    )
    
    def _prepare_move_line_default_vals(self, write_off_line_vals=None):
        """Override to include analytic account and tags in move lines"""
        res = super(AccountPayment, self)._prepare_move_line_default_vals(write_off_line_vals)
        
        for line in res:
            if self.analytic_account_id:
                line['analytic_account_id'] = self.analytic_account_id.id
            if self.analytic_tag_ids:
                line['analytic_tag_ids'] = [(6, 0, self.analytic_tag_ids.ids)]
        
        return res
    
    sale_order_id = fields.Many2one(
        'sale.order', 
        string='أمر المبيعات'
    )
    
    # استخدام Many2one بدلاً من Many2many لتجنب التضارب
    selected_invoice_id = fields.Many2one(
        'account.move',
        string='الفاتورة المحددة'
    )
    
    # حقل محسوب لعرض الفواتير المتاحة
    @api.depends('partner_id', 'sale_order_id')
    def _compute_available_invoices(self):
        for record in self:
            if record.sale_order_id:
                # الفواتير المرتبطة بأمر المبيعات
                invoices = self.env['account.move'].search([
                    ('invoice_origin', '=', record.sale_order_id.name),
                    ('move_type', 'in', ['out_invoice', 'out_refund']),
                    ('state', '=', 'posted')
                ])
                record.available_invoice_ids = invoices
            elif record.partner_id:
                # جميع فواتير العميل
                invoices = self.env['account.move'].search([
                    ('partner_id', '=', record.partner_id.id),
                    ('move_type', 'in', ['out_invoice', 'out_refund']),
                    ('state', '=', 'posted')
                ])
                record.available_invoice_ids = invoices
            else:
                record.available_invoice_ids = False
    
    available_invoice_ids = fields.Many2many(
        'account.move',
        compute='_compute_available_invoices',
        string='الفواتير المتاحة'
    )
    
    # تغيير إلى One2many لإضافة فواتير متعددة مع حساب تحليلي منفصل
    payment_invoice_line_ids = fields.One2many(
        'payment.invoice.line',
        'payment_id',
        string='فواتير الدفع'
    )

class PaymentInvoiceLine(models.Model):
    _name = 'payment.invoice.line'
    _description = 'خط فاتورة الدفع'
    
    payment_id = fields.Many2one('account.payment', string='الدفع', required=True, ondelete='cascade')
    invoice_id = fields.Many2one('account.move', string='الفاتورة', required=True)
    analytic_account_id = fields.Many2one('account.analytic.account', string='الحساب التحليلي')
    analytic_tag_ids = fields.Many2many('account.analytic.tag', string='الوسوم التحليلية')
    amount = fields.Monetary(string='المبلغ', currency_field='currency_id')
    currency_id = fields.Many2one(related='payment_id.currency_id', store=True, readonly=True)

class AccountMove(models.Model):
    _inherit = 'account.move'
    
    analytic_account_id = fields.Many2one(
        'account.analytic.account',
        string='الحساب التحليلي',
        readonly=True,
        states={'draft': [('readonly', False)]}
    )
    analytic_tag_ids = fields.Many2many(
        'account.analytic.tag',
        string='الوسوم التحليلية',
        readonly=True,
        states={'draft': [('readonly', False)]}
    )
    
    def _prepare_move_line_default_vals(self, write_off_line_vals=None):
        """Override to include analytic account and tags in move lines"""
        res = super(AccountMove, self)._prepare_move_line_default_vals(write_off_line_vals)
        
        for line in res:
            if self.analytic_account_id:
                line['analytic_account_id'] = self.analytic_account_id.id
            if self.analytic_tag_ids:
                line['analytic_tag_ids'] = [(6, 0, self.analytic_tag_ids.ids)]
        
        return res
    
    invoice_ids = fields.Many2many(
        'account.move', 
        string='الفواتير'
    )
