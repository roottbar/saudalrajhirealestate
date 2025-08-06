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
        
        # تطبيق المراكز التحليلية على بنود القيد
        for line in res:
            if self.analytic_account_id:
                line['analytic_account_id'] = self.analytic_account_id.id
            if self.analytic_tag_ids:
                line['analytic_tag_ids'] = [(6, 0, self.analytic_tag_ids.ids)]
        
        # ربط الدفع بالفواتير المحددة
        if self.payment_invoice_line_ids:
            for inv_line in self.payment_invoice_line_ids:
                for move_line in res:
                    if move_line.get('credit') > 0:  # بند الدفع
                        move_line['invoice_id'] = inv_line.invoice_id.id
                        if inv_line.analytic_account_id:
                            move_line['analytic_account_id'] = inv_line.analytic_account_id.id
                        if inv_line.analytic_tag_ids:
                            move_line['analytic_tag_ids'] = [(6, 0, inv_line.analytic_tag_ids.ids)]
        
        return res
    
    sale_order_id = fields.Many2one(
        'sale.order', 
        string='أمر المبيعات',
        domain="[('partner_id', '=', partner_id), ('state', 'in', ['sale', 'done'])]"
    )
    
    @api.depends('partner_id', 'sale_order_id')
    def _compute_available_invoices(self):
        for payment in self:
            domain = [
                ('partner_id', '=', payment.partner_id.id),
                ('state', '=', 'posted'),
                ('payment_state', '!=', 'paid')
            ]
            if payment.sale_order_id:
                domain.append(('invoice_origin', '=', payment.sale_order_id.name))
            
            payment.available_invoice_ids = self.env['account.move'].search(domain)
    
    available_invoice_ids = fields.Many2many(
        'account.move',
        compute='_compute_available_invoices',
        string='الفواتير المتاحة'
    )
    
    payment_invoice_line_ids = fields.One2many(
        'payment.invoice.line',
        'payment_id',
        string='فواتير الدفع'
    )
    
    @api.onchange('amount', 'payment_invoice_line_ids')
    def _onchange_amount_distribution(self):
        if self.amount and self.payment_invoice_line_ids:
            total_amount = sum(line.amount for line in self.payment_invoice_line_ids)
            if total_amount != self.amount:
                # توزيع المبلغ المتبقي على الفواتير
                remaining = self.amount - total_amount
                if remaining > 0 and len(self.payment_invoice_line_ids) > 0:
                    per_invoice = remaining / len(self.payment_invoice_line_ids)
                    for line in self.payment_invoice_line_ids:
                        line.amount += per_invoice

class PaymentInvoiceLine(models.Model):
    _name = 'payment.invoice.line'
    _description = 'خط فاتورة الدفع'
    
    payment_id = fields.Many2one('account.payment', string='الدفع', required=True, ondelete='cascade')
    parent = fields.Many2one('account.payment', related='payment_id', store=True)
    
    invoice_id = fields.Many2one(
        'account.move', 
        string='الفاتورة',
        required=True,
        domain="[('id', 'in', parent.available_invoice_ids)]"
    )    available_invoice_ids = fields.Many2many(
        related='payment_id.available_invoice_ids',
        string='الفواتير المتاحة'
    )
    analytic_account_id = fields.Many2one(
        'account.analytic.account', 
        string='مركز التكلفة'
    )
    analytic_tag_ids = fields.Many2many(
        'account.analytic.tag', 
        string='الوسوم التحليلية'
    )
    amount = fields.Monetary(
        string='المبلغ', 
        currency_field='currency_id',
        readonly=True
    )
    currency_id = fields.Many2one(
        related='payment_id.currency_id', 
        store=True, 
        readonly=True
    )
    invoice_amount_residual = fields.Monetary(
        related='invoice_id.amount_residual',
        string='المبلغ المتبقي في الفاتورة',
        readonly=True
    )
    
    @api.onchange('invoice_id')
    def _onchange_invoice_id(self):
        if self.invoice_id:
            # تعيين المبلغ التلقائي عند اختيار الفاتورة
            self.amount = min(self.invoice_id.amount_residual, self.payment_id.amount)
            # تعيين المراكز التحليلية من الفاتورة
            if self.invoice_id.analytic_account_id:
                self.analytic_account_id = self.invoice_id.analytic_account_id
            if self.invoice_id.analytic_tag_ids:
                self.analytic_tag_ids = [(6, 0, self.invoice_id.analytic_tag_ids.ids)]
