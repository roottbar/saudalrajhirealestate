# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError
from datetime import datetime, date
from dateutil.relativedelta import relativedelta


class HrAnnualLeaveSettlement(models.Model):
    _name = 'hr.annual.leave.settlement'
    _description = 'تصفية الإجازة السنوية'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'calculation_date desc'
    _rec_name = 'display_name'
    
    # معلومات أساسية
    employee_id = fields.Many2one('hr.employee', string='الموظف', required=True, ondelete='cascade')
    contract_id = fields.Many2one('hr.contract', string='العقد', ondelete='set null')
    calculation_date = fields.Date(string='تاريخ الحساب', default=fields.Date.context_today, required=True)
    settlement_period_from = fields.Date(string='من تاريخ', required=True)
    settlement_period_to = fields.Date(string='إلى تاريخ', required=True)
    settlement_date = fields.Date(string='تاريخ التصفية', default=fields.Date.context_today)
    settlement_type = fields.Selection([
        ('annual', 'تصفية سنوية'),
        ('end_of_service', 'تصفية نهاية خدمة'),
        ('custom', 'تصفية مخصصة')
    ], string='نوع التصفية', default='annual', required=True)
    
    # معلومات الراتب
    basic_salary = fields.Float(string='الراتب الأساسي', required=True)
    housing_allowance = fields.Float(string='بدل السكن')
    transport_allowance = fields.Float(string='بدل المواصلات')
    other_allowances = fields.Float(string='بدلات أخرى')
    total_salary = fields.Float(string='إجمالي الراتب', compute='_compute_total_salary', store=True)
    monthly_salary = fields.Float(string='الراتب الشهري', compute='_compute_total_salary', store=True)
    daily_salary = fields.Float(string='الراتب اليومي', compute='_compute_daily_salary', store=True)
    
    # حساب الإجازة
    total_leave_days = fields.Float(string='إجمالي أيام الإجازة المستحقة', default=22.0, help='22 يوم حسب النظام السعودي')
    used_leave_days = fields.Float(string='أيام الإجازة المستخدمة', default=0.0)
    remaining_leave_days = fields.Float(string='أيام الإجازة المتبقية', compute='_compute_remaining_leave_days', store=True)
    
    # المبالغ
    leave_settlement_amount = fields.Float(string='مبلغ تصفية الإجازة', compute='_compute_leave_settlement_amount', store=True)
    settlement_amount = fields.Float(string='مبلغ التصفية', compute='_compute_settlement_amount', store=True)
    other_benefits = fields.Float(string='مزايا أخرى', default=0.0)
    gross_amount = fields.Float(string='إجمالي المبلغ', compute='_compute_gross_amount', store=True)
    
    # الخصومات
    loan_deductions = fields.Float(string='خصم القروض', default=0.0)
    advance_deductions = fields.Float(string='خصم السلف', default=0.0)
    other_deductions = fields.Float(string='خصومات أخرى', default=0.0)
    total_deductions = fields.Float(string='إجمالي الخصومات', compute='_compute_total_deductions', store=True)
    deductions = fields.Float(string='الخصومات', compute='_compute_total_deductions', store=True)
    net_amount = fields.Float(string='صافي المبلغ', compute='_compute_net_amount', store=True)
    
    # معلومات إضافية
    notes = fields.Text(string='ملاحظات')
    state = fields.Selection([
        ('draft', 'مسودة'),
        ('confirmed', 'مؤكد'),
        ('approved', 'معتمد'),
        ('paid', 'مدفوع'),
        ('cancelled', 'ملغي')
    ], string='الحالة', default='draft', tracking=True)
    
    # معلومات النظام
    company_id = fields.Many2one('res.company', string='الشركة', default=lambda self: self.env.company)
    currency_id = fields.Many2one('res.currency', related='company_id.currency_id', string='العملة')
    create_uid = fields.Many2one('res.users', string='أنشأ بواسطة', default=lambda self: self.env.user)
    create_date = fields.Datetime(string='تاريخ الإنشاء', default=fields.Datetime.now)
    color = fields.Integer(string='اللون', default=0)
    
    display_name = fields.Char(string='الاسم', compute='_compute_display_name')
    
    @api.depends('employee_id', 'calculation_date')
    def _compute_display_name(self):
        for record in self:
            if record.employee_id and record.calculation_date:
                record.display_name = f"تصفية إجازة {record.employee_id.name} - {record.calculation_date}"
            else:
                record.display_name = "تصفية إجازة سنوية"
    
    @api.depends('basic_salary', 'housing_allowance', 'transport_allowance', 'other_allowances')
    def _compute_total_salary(self):
        for record in self:
            record.total_salary = record.basic_salary + record.housing_allowance + record.transport_allowance + record.other_allowances
            record.monthly_salary = record.total_salary
    
    @api.depends('total_salary')
    def _compute_daily_salary(self):
        for record in self:
            # حساب الراتب اليومي (الراتب الشهري / 30 يوم)
            record.daily_salary = record.total_salary / 30 if record.total_salary else 0
    
    @api.depends('total_leave_days', 'used_leave_days')
    def _compute_remaining_leave_days(self):
        for record in self:
            record.remaining_leave_days = record.total_leave_days - record.used_leave_days
    
    @api.depends('remaining_leave_days', 'daily_salary')
    def _compute_leave_settlement_amount(self):
        for record in self:
            # حساب مبلغ تصفية الإجازة = أيام الإجازة المتبقية × الراتب اليومي
            record.leave_settlement_amount = record.remaining_leave_days * record.daily_salary
    
    @api.depends('leave_settlement_amount')
    def _compute_settlement_amount(self):
        for record in self:
            # مبلغ التصفية هو نفس مبلغ تصفية الإجازة
            record.settlement_amount = record.leave_settlement_amount
    
    @api.depends('settlement_amount', 'other_benefits')
    def _compute_gross_amount(self):
        for record in self:
            # إجمالي المبلغ = مبلغ التصفية + المزايا الأخرى
            record.gross_amount = record.settlement_amount + record.other_benefits
    
    @api.depends('loan_deductions', 'advance_deductions', 'other_deductions')
    def _compute_total_deductions(self):
        for record in self:
            # إجمالي الخصومات = خصم القروض + خصم السلف + خصومات أخرى
            total = record.loan_deductions + record.advance_deductions + record.other_deductions
            record.total_deductions = total
            record.deductions = total
    
    @api.depends('gross_amount', 'total_deductions')
    def _compute_net_amount(self):
        for record in self:
            # صافي المبلغ = إجمالي المبلغ - إجمالي الخصومات
            record.net_amount = record.gross_amount - record.total_deductions
    
    @api.onchange('employee_id')
    def _onchange_employee_id(self):
        if self.employee_id:
            # جلب العقد الحالي
            contract = self.env['hr.contract'].search([
                ('employee_id', '=', self.employee_id.id),
                ('state', '=', 'open')
            ], limit=1)
            
            if contract:
                self.contract_id = contract.id
                self.monthly_salary = contract.wage
            
            # تعيين فترة التصفية (سنة كاملة من تاريخ التوظيف)
            if self.employee_id.hire_date:
                hire_date = self.employee_id.hire_date
                current_year = date.today().year
                
                # حساب بداية ونهاية السنة المالية للإجازة
                year_start = date(current_year, hire_date.month, hire_date.day)
                if year_start > date.today():
                    year_start = date(current_year - 1, hire_date.month, hire_date.day)
                
                year_end = year_start + relativedelta(years=1) - relativedelta(days=1)
                
                self.settlement_period_from = year_start
                self.settlement_period_to = min(year_end, date.today())
            
            # حساب أيام الإجازة المستخدمة من نظام الإجازات
            self._compute_used_leave_days()
    
    def _compute_used_leave_days(self):
        """حساب أيام الإجازة المستخدمة من نظام الإجازات"""
        if self.employee_id and self.settlement_period_from and self.settlement_period_to:
            # البحث عن إجازات الموظف في الفترة المحددة
            leave_requests = self.env['hr.leave'].search([
                ('employee_id', '=', self.employee_id.id),
                ('state', '=', 'validate'),
                ('request_date_from', '>=', self.settlement_period_from),
                ('request_date_to', '<=', self.settlement_period_to),
                ('holiday_status_id.unpaid', '=', False),  # الإجازات المدفوعة فقط
            ])
            
            total_used_days = sum(leave_requests.mapped('number_of_days'))
            self.used_leave_days = total_used_days
    
    @api.constrains('settlement_period_from', 'settlement_period_to')
    def _check_settlement_period(self):
        for record in self:
            if record.settlement_period_from and record.settlement_period_to:
                if record.settlement_period_from >= record.settlement_period_to:
                    raise ValidationError(_('تاريخ البداية يجب أن يكون قبل تاريخ النهاية!'))
    
    @api.constrains('total_leave_days', 'used_leave_days')
    def _check_leave_days(self):
        for record in self:
            if record.used_leave_days < 0:
                raise ValidationError(_('أيام الإجازة المستخدمة لا يمكن أن تكون سالبة!'))
            if record.total_leave_days < 0:
                raise ValidationError(_('إجمالي أيام الإجازة لا يمكن أن يكون سالباً!'))
    
    def action_confirm(self):
        """تأكيد التصفية"""
        for record in self:
            if record.state != 'draft':
                raise UserError(_('يمكن تأكيد التصفيات في حالة المسودة فقط!'))
            
            # التحقق من البيانات المطلوبة
            if not record.employee_id:
                raise UserError(_('يجب تحديد الموظف!'))
            if not record.monthly_salary:
                raise UserError(_('يجب تحديد الراتب الشهري!'))
            
            record.state = 'confirmed'
    
    def action_approve(self):
        """اعتماد التصفية"""
        for record in self:
            if record.state != 'confirmed':
                raise UserError(_('يمكن اعتماد التصفيات المؤكدة فقط!'))
            
            record.state = 'approved'
    
    def action_set_to_paid(self):
        """تعيين كمدفوع"""
        for record in self:
            if record.state != 'approved':
                raise UserError(_('يمكن تعيين التصفيات المعتمدة كمدفوعة فقط!'))
            
            record.state = 'paid'
    
    def action_cancel(self):
        """إلغاء التصفية"""
        for record in self:
            if record.state == 'paid':
                raise UserError(_('لا يمكن إلغاء التصفيات المدفوعة!'))
            
            record.state = 'cancelled'
    
    def action_reset_to_draft(self):
        """إعادة تعيين كمسودة"""
        for record in self:
            if record.state == 'paid':
                raise UserError(_('لا يمكن إعادة تعيين التصفيات المدفوعة كمسودة!'))
            
            record.state = 'draft'
    
    def action_print_settlement(self):
        """طباعة التصفية"""
        self.ensure_one()
        return self.env.ref('hr_end_of_service_sa.action_report_annual_leave_settlement_pdf').report_action(self)
    
    def get_settlement_summary(self):
        """ملخص التصفية"""
        self.ensure_one()
        return {
            'employee_name': self.employee_id.name,
            'employee_code': self.employee_id.employee_id or '',
            'calculation_date': self.calculation_date,
            'period_from': self.settlement_period_from,
            'period_to': self.settlement_period_to,
            'monthly_salary': self.monthly_salary,
            'daily_salary': self.daily_salary,
            'total_leave_days': self.total_leave_days,
            'used_leave_days': self.used_leave_days,
            'remaining_leave_days': self.remaining_leave_days,
            'leave_settlement_amount': self.leave_settlement_amount,
            'settlement_amount': self.settlement_amount,
            'deductions': self.deductions,
            'net_amount': self.net_amount,
            'state': dict(self._fields['state'].selection)[self.state],
        }