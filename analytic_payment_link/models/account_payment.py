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
    
    partner_id = fields.Many2one('res.partner', string='العميل')
    sale_order_id = fields.Many2one('sale.order', string='أمر المبيعات',
        domain="[('partner_id', '=', partner_id)]")
    invoice_ids = fields.Many2many('account.move', string='الفواتير',
        domain="[('sale_order_id', '=', sale_order_id)]")
