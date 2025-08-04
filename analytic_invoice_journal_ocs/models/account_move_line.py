from odoo import models, fields

class AccountMoveLine(models.Model):
    _inherit = 'account.move.line'
    
    analytic_account_id = fields.Many2one(
        string='الحساب التحليلي',
        readonly=False,  # جعل الحقل قابل للتعديل حتى في بنود الإقفال
    )
    
    analytic_tag_ids = fields.Many2many(
        string='الوسوم التحليلية',
        readonly=False,  # جعل الحقل قابل للتعديل حتى في بنود الإقفال
    )