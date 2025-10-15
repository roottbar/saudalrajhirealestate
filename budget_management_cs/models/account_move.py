from odoo import models, fields, api, exceptions, _


class AccountMove(models.Model):
    _inherit = 'account.move'

    budget_project_id = fields.Many2one('budget.project', string='المشروع', ondelete='restrict')
    budget_department_id = fields.Many2one('budget.department', string='القسم', ondelete='restrict')
    budget_id = fields.Many2one(
        'budget.budget',
        string='الميزانية',
        domain="[('department_id', '=', budget_department_id), '|', ('project_id', '=', False), ('project_id', '=', budget_project_id), ('date_start', '<=', invoice_date), ('date_end', '>=', invoice_date)]",
        ondelete='restrict',
    )
    budget_move_id = fields.Many2one('account.move', string='قيد الميزانية', readonly=True, copy=False)
    budget_move_reversal_id = fields.Many2one('account.move', string='عكس القيد', readonly=True, copy=False)

    budget_currency_id = fields.Many2one('res.currency', string='عملة الميزانية', compute='_compute_budget_remaining', readonly=True)
    budget_remaining_amount = fields.Monetary(string='المتبقي في الميزانية', currency_field='budget_currency_id', compute='_compute_budget_remaining', readonly=True)

    @api.onchange('budget_project_id')
    def _onchange_budget_project_id_domain(self):
        if self.budget_project_id:
            return {'domain': {'budget_department_id': [('id', 'in', self.budget_project_id.department_ids.ids)]}}
        return {'domain': {'budget_department_id': []}}

    @api.onchange('budget_department_id', 'budget_project_id', 'invoice_date')
    def _onchange_budget_fields(self):
        for move in self:
            domain = [
                ('department_id', '=', move.budget_department_id.id),
                '|', ('project_id', '=', False), ('project_id', '=', move.budget_project_id.id),
            ]
            date_value = move.invoice_date or move.date
            if date_value:
                domain += [('date_start', '<=', date_value), ('date_end', '>=', date_value)]
            budgets = self.env['budget.budget'].search(domain)
            move.budget_id = budgets[:1]

    def _get_applicable_budget(self):
        self.ensure_one()
        budget = self.budget_id
        if not budget and self.budget_department_id:
            domain = [
                ('department_id', '=', self.budget_department_id.id),
                '|', ('project_id', '=', False), ('project_id', '=', self.budget_project_id.id),
            ]
            date_value = self.invoice_date or self.date
            if date_value:
                domain += [('date_start', '<=', date_value), ('date_end', '>=', date_value)]
            budget = self.env['budget.budget'].search(domain, limit=1)
        return budget

    @api.depends('budget_id')
    def _compute_budget_remaining(self):
        for move in self:
            if move.budget_id:
                move.budget_currency_id = move.budget_id.currency_id
                move.budget_remaining_amount = move.budget_id.remaining_amount or 0.0
            else:
                move.budget_currency_id = move.currency_id
                move.budget_remaining_amount = 0.0

    @api.constrains('amount_total', 'budget_id', 'move_type')
    def _check_budget_remaining(self):
        for move in self:
            if move.move_type == 'in_invoice' and move.budget_id:
                amount = move.amount_untaxed or 0.0
                if move.currency_id and move.budget_id.currency_id and move.currency_id != move.budget_id.currency_id:
                    amount = move.currency_id._convert(amount, move.budget_id.currency_id, move.company_id, move.invoice_date or fields.Date.today())
                remaining = move.budget_id.remaining_amount or 0.0
                if amount > remaining:
                    raise exceptions.ValidationError(_("لا يمكن حفظ الفاتورة لأن المبلغ يتجاوز المتبقي في الميزانية (%s).") % remaining)

    def action_post(self):
        res = super(AccountMove, self).action_post()
        for move in self:
            if move.move_type == 'in_invoice':
                budget = move._get_applicable_budget()
                if not budget:
                    raise exceptions.UserError(_('لا توجد ميزانية مطابقة للقسم/المشروع والتاريخ المحدد.'))

                amount_in_budget_currency = move.currency_id._convert(
                    move.amount_untaxed,
                    budget.currency_id,
                    move.company_id,
                    move.invoice_date or fields.Date.today(),
                )

                if amount_in_budget_currency > budget.remaining_amount:
                    raise exceptions.UserError(_('المبلغ المطلوب يتجاوز الميزانية المتاحة للقسم/المشروع المحدد.'))
                try:
                    move._create_budget_expense_entry()
                except Exception as e:
                    move.message_post(body=_('تعذّر إنشاء قيد ميزانية تلقائي: %s') % e)
        return res

    def button_cancel(self):
        for move in self:
            bm = move.budget_move_id
            if move.move_type == 'in_invoice' and bm and bm.state == 'posted' and not move.budget_move_reversal_id:
                reversal_moves = bm._reverse_moves(default_values_list=[{
                    'ref': _('Reversal of Budget Expense for %s') % (move.name),
                }], cancel=False)
                for rev in reversal_moves:
                    rev.action_post()
                move.budget_move_reversal_id = reversal_moves and reversal_moves[0]
        return super(AccountMove, self).button_cancel()

    def _create_budget_expense_entry(self):
        self.ensure_one()
        if not self.budget_department_id:
            return False
        dept = self.budget_department_id
        if not dept.budget_journal_id or not dept.account_budget_allocation_id or not dept.account_expense_id:
            raise exceptions.UserError(_('يرجى ضبط دفتر القيود وحسابات الميزانية في القسم المحدد.'))

        amount_company = self.currency_id._convert(
            self.amount_untaxed,
            self.company_id.currency_id,
            self.company_id,
            self.invoice_date or fields.Date.today(),
        )

        if amount_company <= 0.0:
            return False

        budget = self._get_applicable_budget()
        vals = {
            'move_type': 'entry',
            'date': self.invoice_date or fields.Date.today(),
            'journal_id': dept.budget_journal_id.id,
            'ref': _('Budget Expense for %s') % (self.name),
            'budget_id': budget.id if budget else False,
            'line_ids': [
                (0, 0, {
                    'name': _('Expense %s') % (self.name),
                    'account_id': dept.account_expense_id.id,
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
        self.budget_move_id = move
        return move