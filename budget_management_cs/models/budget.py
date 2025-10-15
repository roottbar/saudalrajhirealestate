from odoo import models, fields, api, _, exceptions


class BudgetBudget(models.Model):
    _name = 'budget.budget'
    _description = 'Department/Project Budget'

    name = fields.Char(string='اسم الميزانية', required=True)
    department_id = fields.Many2one('budget.department', string='القسم', required=True, ondelete='restrict')
    project_id = fields.Many2one('budget.project', string='المشروع', ondelete='restrict')
    company_id = fields.Many2one('res.company', string='الشركة', required=True, default=lambda self: self.env.company)

    currency_id = fields.Many2one('res.currency', string='العملة', required=True, default=lambda self: self.env['res.currency'].search([('name', '=', 'SAR')], limit=1))
    sar_currency_id = fields.Many2one('res.currency', string='SAR', compute='_compute_sar_currency', store=False)
    total_amount = fields.Monetary(string='المبلغ الكلي', required=True, currency_field='sar_currency_id')

    date_start = fields.Date(string='تاريخ البداية')
    date_end = fields.Date(string='تاريخ النهاية')
    period_type = fields.Selection([
        ('monthly', 'شهري'),
        ('quarterly', 'ربع سنوي'),
        ('yearly', 'سنوي'),
        ('custom', 'مخصص'),
    ], string='فترة الميزانية', default='yearly')

    spent_amount = fields.Monetary(string='المبلغ المصروف', compute='_compute_spent_amount', store=True, currency_field='sar_currency_id')
    remaining_amount = fields.Monetary(string='المتبقي', compute='_compute_remaining_amount', store=True, currency_field='sar_currency_id')
    spent_percentage = fields.Float(string='نسبة الإنفاق %', compute='_compute_spent_percentage', store=True)

    purchase_order_ids = fields.One2many('purchase.order', 'budget_id', string='أوامر الشراء ذات الصلة')
    invoice_ids = fields.One2many('account.move', 'budget_id', string='الفواتير ذات الصلة')
    budget_move_ids = fields.One2many('account.move', 'budget_id', string='حركات الميزانية')

    # مربع نص الملاحظات لواجهة الميزانية
    note = fields.Text(string='ملاحظات')

    # حالة الميزانية: مسودة أو معمد
    state = fields.Selection([
        ('draft', 'مسودة'),
        ('approved', 'معمد'),
    ], string='الحالة', default='draft', required=True)

    @api.depends('purchase_order_ids.state', 'purchase_order_ids.amount_total', 'invoice_ids.state', 'invoice_ids.amount_untaxed', 'invoice_ids.move_type', 'currency_id')
    def _compute_spent_amount(self):
        for budget in self:
            total = 0.0
            sar = self.env['res.currency'].search([('name', '=', 'SAR')], limit=1)
            target_currency = sar or budget.currency_id
            # إنفاق المشتريات (أوامر الشراء في حالة شراء/تم)
            for po in budget.purchase_order_ids.filtered(lambda p: p.state in ('purchase', 'done')):
                total += po.currency_id._convert(po.amount_total or 0.0, target_currency, budget.company_id, po.date_order or fields.Date.today())
            # إنفاق الفواتير (فواتير الموردين المرحلة)
            vendor_invoices = budget.invoice_ids.filtered(lambda m: m.move_type == 'in_invoice' and m.state == 'posted')
            for inv in vendor_invoices:
                total += inv.currency_id._convert(inv.amount_untaxed or 0.0, target_currency, budget.company_id, inv.invoice_date or fields.Date.today())
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
        # ضمان توحيد العملة إلى الريال السعودي (SAR) عند الإنشاء، وتحويل المبلغ إن لزم
        sar = self.env['res.currency'].search([('name', '=', 'SAR')], limit=1)
        # ضمان أن الميزانية تبدأ بالحالة "مسودة" عند الإنشاء ما لم تُمرَّر قيمة أخرى صراحةً
        for vals in vals_list:
            vals.setdefault('state', 'draft')
            if sar:
                company = None
                if vals.get('company_id'):
                    company = self.env['res.company'].browse(vals['company_id'])
                else:
                    company = self.env.company
                # إن تم تمرير عملة غير SAR مع المبلغ، حوّلها إلى SAR ثم ثبّت العملة إلى SAR
                input_currency_id = vals.get('currency_id')
                if input_currency_id and input_currency_id != sar.id and vals.get('total_amount'):
                    src_cur = self.env['res.currency'].browse(input_currency_id)
                    date_ref = vals.get('date_start') or fields.Date.today()
                    vals['total_amount'] = src_cur._convert(vals['total_amount'], sar, company, date_ref)
                vals['currency_id'] = sar.id
        return super(BudgetBudget, self).create(vals_list)

    def write(self, vals):
        # توحيد العملة إلى SAR عند أي تعديل، وتحويل المبلغ إن لزم
        sar = self.env['res.currency'].search([('name', '=', 'SAR')], limit=1)
        if sar:
            # تجاهل أي محاولة لتغيير العملة إلى غير SAR، وحوّل المبلغ إذا تم تغييره مصحوباً بعملة مُمرَّرة
            if 'currency_id' in vals and vals['currency_id'] != sar.id:
                # سنحوّل المبلغ الحالي إلى SAR إذا لم يُمرَّر total_amount جديد
                for rec in self:
                    company = rec.company_id or self.env.company
                    date_ref = vals.get('date_start') or rec.date_start or fields.Date.today()
                    if 'total_amount' in vals:
                        src_cur = self.env['res.currency'].browse(vals['currency_id'])
                        vals['total_amount'] = src_cur._convert(vals['total_amount'], sar, company, date_ref)
                    else:
                        src_cur = rec.currency_id
                        vals['total_amount'] = src_cur._convert(rec.total_amount or 0.0, sar, company, date_ref)
                vals['currency_id'] = sar.id
            elif 'total_amount' in vals and ('currency_id' not in vals):
                # تأكد أن العملة في السجل هي SAR، إن لم تكن، حوّل القيمة وأجبِر العملة إلى SAR
                for rec in self:
                    if rec.currency_id and rec.currency_id.name != 'SAR':
                        company = rec.company_id or self.env.company
                        date_ref = vals.get('date_start') or rec.date_start or fields.Date.today()
                        vals['total_amount'] = rec.currency_id._convert(vals['total_amount'], sar, company, date_ref)
                        vals['currency_id'] = sar.id
        # منع تعديل الحقول الحساسة عندما تكون الحالة "معمد"
        protected_fields = {'total_amount', 'date_start', 'date_end', 'period_type'}
        for rec in self:
            final_state = vals.get('state', rec.state)
            if final_state == 'approved' and any(f in vals for f in protected_fields):
                raise exceptions.UserError(_('لا يمكن تعديل المبلغ الكلي أو فترة الميزانية أثناء حالة التعمييد. أعد الميزانية إلى مسودة أولاً.'))
        return super(BudgetBudget, self).write(vals)

    def _compute_sar_currency(self):
        sar = self.env['res.currency'].search([('name', '=', 'SAR')], limit=1)
        for budget in self:
            budget.sar_currency_id = sar or budget.company_id.currency_id

    def action_set_draft(self):
        self.write({'state': 'draft'})
        return True

    def action_approve(self):
        self.write({'state': 'approved'})
        return True