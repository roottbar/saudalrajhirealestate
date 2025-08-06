from odoo import models, fields, api, _
from odoo.exceptions import UserError

class AccountPayment(models.Model):
    _inherit = 'account.payment'
    
    renting_order_id = fields.Many2one(
        'sale.order', 
        string='أمر التأجير',
        domain="[('partner_id', '=', partner_id), ('state', 'in', ['sale', 'done'])]"
    )
    
    @api.onchange('renting_order_id')
    def _onchange_renting_order_id(self):
        if self.renting_order_id and not self._is_rental_order(self.renting_order_id):
            return {
                'warning': {
                    'title': 'تحذير',
                    'message': 'يجب اختيار أمر تأجير صالح'
                }
            }
    
    def _is_rental_order(self, order):
        """تحقق مما إذا كان الأمر هو أمر تأجير"""
        return any(line.product_id.rental for line in order.order_line)
    
    @api.depends('partner_id', 'renting_order_id')
    def _compute_available_invoices(self):
        for payment in self:
            domain = [
                ('partner_id', '=', payment.partner_id.id),
                ('state', '=', 'posted'),
                ('payment_state', '!=', 'paid'),
                ('move_type', 'in', ['out_invoice', 'out_refund'])
            ]
            
            if payment.renting_order_id:
                domain.append(('invoice_origin', '=', payment.renting_order_id.name))
                domain.append(('line_ids.sale_line_ids.order_id', '=', payment.renting_order_id.id))
            
            payment.available_invoice_ids = self.env['account.move'].search(domain)
    
    available_invoice_ids = fields.Many2many(
        'account.move',
        compute='_compute_available_invoices',
        string='فواتير التأجير المتاحة'
    )
    
    payment_invoice_line_ids = fields.One2many(
        'payment.invoice.line',
        'payment_id',
        string='فواتير الدفع'
    )
    
    def write(self, vals):
        if 'invoice_id' in vals and not vals['invoice_id']:
            del vals['invoice_id']
        return super(AccountPayment, self).write(vals)
    
    def _prepare_move_line_default_vals(self, write_off_line_vals=None):
        res = super(AccountPayment, self)._prepare_move_line_default_vals(write_off_line_vals)
        
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

class PaymentInvoiceLine(models.Model):
    _name = 'payment.invoice.line'
    _description = 'خط فاتورة الدفع'
    
    payment_id = fields.Many2one('account.payment', string='الدفع', required=True, ondelete='cascade')
    parent = fields.Many2one('account.payment', related='payment_id', store=True)
    
    invoice_id = fields.Many2one(
        'account.move', 
        string='فاتورة التأجير',
        required=True,
        domain="[('id', 'in', parent.available_invoice_ids)]"
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
    
    @api.model
    def create(self, vals):
        if 'invoice_id' not in vals or not vals['invoice_id']:
            raise UserError(_('يجب تحديد فاتورة صالحة'))
        return super(PaymentInvoiceLine, self).create(vals)
    
    def write(self, vals):
        if 'invoice_id' in vals and not vals['invoice_id']:
            raise UserError(_('لا يمكن إزالة الفاتورة المحددة'))
        return super(PaymentInvoiceLine, self).write(vals)
    
    @api.onchange('invoice_id')
    def _onchange_invoice_id(self):
        if self.invoice_id:
            self.amount = min(self.invoice_id.amount_residual, self.payment_id.amount)
            invoice_lines = self.invoice_id.invoice_line_ids.filtered(
                lambda l: l.display_type not in ('line_section', 'line_note')
            )
            if invoice_lines:
                self.analytic_account_id = invoice_lines[0].analytic_account_id
                all_tags = invoice_lines.mapped('analytic_tag_ids')
                self.analytic_tag_ids = [(6, 0, all_tags.ids)] if all_tags else False
