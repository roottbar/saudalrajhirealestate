from odoo import models, fields


class BudgetDepartment(models.Model):
    _name = 'budget.department'
    _description = 'Budget Department'

    name = fields.Char(string='اسم القسم', required=True)
    active = fields.Boolean(string='نشط', default=True)
    note = fields.Text(string='ملاحظات')

    # تكامل محاسبي خاص بالميزانية
    budget_journal_id = fields.Many2one('account.journal', string='دفتر قيود الميزانية', domain=[('type', '=', 'general')])
    account_budget_allocation_id = fields.Many2one('account.account', string='حساب مخصصات الميزانية')
    account_commitment_id = fields.Many2one('account.account', string='حساب الالتزامات')
    account_expense_id = fields.Many2one('account.account', string='حساب المصروف')