from odoo import models, fields, api, exceptions, _


class PurchaseOrder(models.Model):
    _inherit = 'purchase.order'

    budget_project_id = fields.Many2one('budget.project', string='المشروع', ondelete='restrict')
    budget_department_id = fields.Many2one('budget.department', string='القسم', ondelete='restrict')
    
    @api.onchange('budget_project_id')
    def _onchange_budget_project_id_domain(self):
        # ضبط دومين الأقسام بحسب المشروع المختار
        if self.budget_project_id:
            return {'domain': {'budget_department_id': [('id', 'in', self.budget_project_id.department_ids.ids)]}}
        return {'domain': {'budget_department_id': []}}
    budget_id = fields.Many2one(
        'budget.budget',
        string='الميزانية',
        domain="[('department_id', '=', budget_department_id), '|', ('project_id', '=', False), ('project_id', '=', budget_project_id), ('date_start', '<=', date_order), ('date_end', '>=', date_order)]",
        ondelete='restrict',
    )
    budget_move_id = fields.Many2one('account.move', string='قيد الميزانية', readonly=True, copy=False)
    budget_move_reversal_id = fields.Many2one('account.move', string='عكس القيد', readonly=True, copy=False)

    # عرض المبلغ المتبقي في الميزانية في شاشة المشتريات
    budget_currency_id = fields.Many2one('res.currency', string='عملة الميزانية', compute='_compute_budget_remaining', readonly=True)
    budget_remaining_amount = fields.Monetary(string='المتبقي في الميزانية', currency_field='budget_currency_id', compute='_compute_budget_remaining', readonly=True)

    @api.onchange('budget_department_id', 'budget_project_id', 'date_order')
    def _onchange_budget_fields(self):
        # محاولة تعيين ميزانية تلقائياً إذا كانت واحدة مطابقة
        for order in self:
            domain = [
                ('department_id', '=', order.budget_department_id.id),
                '|', ('project_id', '=', False), ('project_id', '=', order.budget_project_id.id),
            ]
            if order.date_order:
                domain += [('date_start', '<=', order.date_order.date() if hasattr(order.date_order, 'date') else order.date_order),
                           ('date_end', '>=', order.date_order.date() if hasattr(order.date_order, 'date') else order.date_order)]
            budgets = self.env['budget.budget'].search(domain)
            order.budget_id = budgets[:1]

    def _get_applicable_budget(self):
        self.ensure_one()
        budget = self.budget_id
        if not budget and self.budget_department_id:
            domain = [
                ('department_id', '=', self.budget_department_id.id),
                '|', ('project_id', '=', False), ('project_id', '=', self.budget_project_id.id),
            ]
            if self.date_order:
                domain += [('date_start', '<=', self.date_order.date() if hasattr(self.date_order, 'date') else self.date_order),
                           ('date_end', '>=', self.date_order.date() if hasattr(self.date_order, 'date') else self.date_order)]
            budget = self.env['budget.budget'].search(domain, limit=1)
        return budget

    @api.depends('budget_id')
    def _compute_budget_remaining(self):
        for order in self:
            if order.budget_id:
                order.budget_currency_id = order.budget_id.currency_id
                order.budget_remaining_amount = order.budget_id.remaining_amount or 0.0
            else:
                order.budget_currency_id = order.currency_id
                order.budget_remaining_amount = 0.0

    @api.constrains('amount_total', 'budget_id')
    def _check_budget_remaining(self):
        for order in self:
            if order.budget_id:
                # احتساب المنع على المبلغ بدون ضريبة
                amount = order.amount_untaxed or 0.0
                # تحويل العملة إذا اختلفت عملة أمر الشراء عن عملة الميزانية
                if order.currency_id and order.budget_id.currency_id and order.currency_id != order.budget_id.currency_id:
                    amount = order.currency_id._convert(amount, order.budget_id.currency_id, order.company_id, order.date_order or fields.Date.today())
                remaining = order.budget_id.remaining_amount or 0.0
                if amount > remaining:
                    raise exceptions.ValidationError(_("لا يمكن حفظ أمر الشراء لأن المبلغ يتجاوز المتبقي في الميزانية (%s).") % remaining)

    def button_confirm(self):
        for order in self:
            budget = order._get_applicable_budget()
            if not budget:
                raise exceptions.UserError(_('لا توجد ميزانية مطابقة للقسم/المشروع والتاريخ المحدد.'))

            # تحويل مبلغ أمر الشراء إلى عملة الميزانية (إن لزم)
            # استخدام المبلغ بدون ضريبة بدل الإجمالي مع الضريبة
            order_amount_in_budget_currency = order.currency_id._convert(
                order.amount_untaxed,
                budget.currency_id,
                order.company_id,
                order.date_order or fields.Date.today(),
            )

            if order_amount_in_budget_currency > budget.remaining_amount:
                raise exceptions.UserError(_('المبلغ المطلوب يتجاوز الميزانية المتاحة للقسم/المشروع المحدد.'))
        res = super(PurchaseOrder, self).button_confirm()
        # إنشاء قيد الالتزام المحاسبي بعد التأكيد
        for order in self:
            try:
                order._create_budget_commitment_entry()
            except Exception as e:
                # إذا فشل القيد، لا نمنع التأكيد لكن نعرض رسالة للمستخدم
                # يمكن تغيير السلوك لاحقاً لفرض القيد
                order.message_post(body=_('تعذّر إنشاء قيد ميزانية تلقائي: %s') % e)
        return res

    def button_cancel(self):
        # عكس قيد الالتزام عند إلغاء أمر الشراء
        for order in self:
            move = order.budget_move_id
            if move and move.state == 'posted' and not order.budget_move_reversal_id:
                reversal_moves = move._reverse_moves(default_values_list=[{
                    'ref': _('Reversal of Budget Commitment for %s') % (order.name),
                }], cancel=False)
                for rev in reversal_moves:
                    rev.action_post()
                order.budget_move_reversal_id = reversal_moves and reversal_moves[0]
        return super(PurchaseOrder, self).button_cancel()

    def _create_budget_commitment_entry(self):
        self.ensure_one()
        if not self.budget_department_id:
            return False
        dept = self.budget_department_id
        if not dept.budget_journal_id or not dept.account_budget_allocation_id or not dept.account_commitment_id:
            raise exceptions.UserError(_('يرجى ضبط دفتر القيود وحسابات الميزانية في القسم المحدد.'))

        # حساب المبلغ بعملة الشركة للمحاسبة
        # ترحيل قيد الالتزام على صافي المبلغ بدون ضريبة
        amount_company = self.currency_id._convert(
            self.amount_untaxed,
            self.company_id.currency_id,
            self.company_id,
            self.date_order or fields.Date.today(),
        )

        if amount_company <= 0.0:
            return False

        vals = {
            'move_type': 'entry',
            'date': self.date_order or fields.Date.today(),
            'journal_id': dept.budget_journal_id.id,
            'ref': _('Budget Commitment for %s') % (self.name),
            'line_ids': [
                (0, 0, {
                    'name': _('Commitment %s') % (self.name),
                    'account_id': dept.account_commitment_id.id,
                    'debit': amount_company,
                    'credit': 0.0,
                    'partner_id': self.partner_id.id,
                }),
                (0, 0, {
                    'name': _('Allocation %s') % (self.name),
                    'account_id': dept.account_budget_allocation_id.id,
                    'debit': 0.0,
                    'credit': amount_company,
                    'partner_id': self.partner_id.id,
                }),
            ],
        }
        move = self.env['account.move'].create(vals)
        move.action_post()
        self.budget_move_id = move.id
        return move