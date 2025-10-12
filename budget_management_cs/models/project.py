from odoo import models, fields


class BudgetProject(models.Model):
    _name = 'budget.project'
    _description = 'Budget Project'

    name = fields.Char(string='اسم المشروع', required=True)
    department_id = fields.Many2one('budget.department', string='القسم', ondelete='restrict')
    active = fields.Boolean(string='نشط', default=True)
    note = fields.Text(string='ملاحظات')