from odoo import models, fields, api, _


class BudgetBudget(models.Model):
    _name = 'budget.budget'
    _description = 'Department/Project Budget'

    name = fields.Char(string='اسم الميزانية', required=True)
    department_id = fields.Many2one('budget.department', string='القسم', required=True, ondelete='restrict')
    project_id = fields.Many2one('budget.project', string='المشروع', ondelete='restrict')
    company_id = fields.Many2one('res.company', string='الشركة', required=True, default=lambda self: self.env.company)

    currency_id = fields.Many2one('res.currency', string='العملة', required=True, default=lambda self: self.env.company.currency_id)
    total_amount = fields.Monetary(string='المبلغ الكلي', required=True, currency_field='currency_id')

    date_start = fields.Date(string='تاريخ البداية')
    date_end = fields.Date(string='تاريخ النهاية')
    period_type = fields.Selection([
        ('monthly', 'شهري'),
        ('quarterly', 'ربع سنوي'),
        ('yearly', 'سنوي'),
        ('custom', 'مخصص'),
    ], string='فترة الميزانية', default='yearly')

    spent_amount = fields.Monetary(string='المبلغ المصروف', compute='_compute_spent_amount', store=True, currency_field='currency_id')
    remaining_amount = fields.Monetary(string='المتبقي', compute='_compute_remaining_amount', store=True, currency_field='currency_id')
    spent_percentage = fields.Float(string='نسبة الإنفاق %', compute='_compute_spent_percentage', store=True)

    purchase_order_ids = fields.One2many('purchase.order', 'budget_id', string='أوامر الشراء ذات الصلة')

    # مربع نص الملاحظات لواجهة الميزانية
    note = fields.Text(string='ملاحظات')

    # حالة الميزانية: مسودة أو معمد
    state = fields.Selection([
        ('draft', 'مسودة'),
        ('approved', 'معمد'),
    ], string='الحالة', default='approved', required=True)

    @api.depends('purchase_order_ids.state', 'purchase_order_ids.amount_total', 'currency_id')
    def _compute_spent_amount(self):
        for budget in self:
            total = 0.0
            for po in budget.purchase_order_ids.filtered(lambda p: p.state in ('purchase', 'done')):
                # تحويل مبلغ أمر الشراء إلى عملة الميزانية
                total += po.currency_id._convert(po.amount_total, budget.currency_id, budget.company_id, po.date_order or fields.Date.today())
            budget.spent_amount = total

    @api.depends('total_amount', 'spent_amount')
    def _compute_remaining_amount(self):
        for budget in self:
            budget.remaining_amount = (budget.total_amount or 0.0) - (budget.spent_amount or 0.0)

    @api.depends('total_amount', 'spent_amount')
    def _compute_spent_percentage(self):
        for budget in self:
            total = budget.total_amount or 0.0
            budget.spent_percentage = (budget.spent_amount / total * 100.0) if total else 0.0

    @api.model_create_multi
    def create(self, vals_list):
        # ضمان أن الميزانية تبدأ بالحالة "معمد" حتى في حال تمرير حالة مختلفة
        for vals in vals_list:
            vals['state'] = 'approved'
        return super(BudgetBudget, self).create(vals_list)

    def write(self, vals):
        # منع تعديل الحقول الحساسة عندما تكون الحالة "معمد"
        protected_fields = {'total_amount', 'date_start', 'date_end', 'period_type'}
        for rec in self:
            final_state = vals.get('state', rec.state)
            if final_state == 'approved' and any(f in vals for f in protected_fields):
                raise exceptions.UserError(_('لا يمكن تعديل المبلغ الكلي أو فترة الميزانية أثناء حالة التعمييد. أعد الميزانية إلى مسودة أولاً.'))
        return super(BudgetBudget, self).write(vals)

    def action_set_draft(self):
        self.write({'state': 'draft'})
        return True

    def action_approve(self):
        self.write({'state': 'approved'})
        return True