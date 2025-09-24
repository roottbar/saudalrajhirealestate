# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError
from datetime import datetime, date
from dateutil.relativedelta import relativedelta
import calendar


class HrEndOfService(models.Model):
    _name = 'hr.end.of.service'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = 'تصفية نهاية الخدمة'
    _order = 'create_date desc'
    _rec_name = 'employee_id'

    # معلومات أساسية
    employee_id = fields.Many2one('hr.employee', string='الموظف', required=True, ondelete='cascade')
    contract_id = fields.Many2one('hr.contract', string='العقد', required=True)
    department_id = fields.Many2one('hr.department', string='القسم', related='employee_id.department_id', store=True)
    job_id = fields.Many2one('hr.job', string='المنصب', related='employee_id.job_id', store=True)
    
    # تواريخ مهمة
    start_date = fields.Date(string='تاريخ بداية العمل', required=True)
    end_date = fields.Date(string='تاريخ نهاية الخدمة', required=True, default=fields.Date.today)
    calculation_date = fields.Date(string='تاريخ الحساب', default=fields.Date.today, required=True)
    
    # معلومات الراتب
    basic_salary = fields.Float(string='الراتب الأساسي', required=True)
    housing_allowance = fields.Float(string='بدل السكن')
    transport_allowance = fields.Float(string='بدل المواصلات')
    other_allowances = fields.Float(string='بدلات أخرى')
    total_salary = fields.Float(string='إجمالي الراتب', compute='_compute_total_salary', store=True)
    
    # فترة الخدمة
    service_years = fields.Integer(string='سنوات الخدمة', compute='_compute_service_period', store=True)
    service_months = fields.Integer(string='أشهر الخدمة', compute='_compute_service_period', store=True)
    service_days = fields.Integer(string='أيام الخدمة', compute='_compute_service_period', store=True)
    total_service_days = fields.Integer(string='إجمالي أيام الخدمة', compute='_compute_service_period', store=True)
    
    # نوع إنهاء الخدمة
    termination_type = fields.Selection([
        ('resignation', 'استقالة'),
        ('termination_with_cause', 'فصل تأديبي (بسبب)'),
        ('termination_without_cause', 'فصل تعسفي (بدون سبب)'),
        ('end_of_contract', 'انتهاء مدة العقد'),
        ('retirement', 'تقاعد'),
        ('death', 'وفاة'),
        ('disability', 'عجز عن العمل'),
        ('mutual_agreement', 'اتفاق متبادل')
    ], string='نوع إنهاء الخدمة', required=True, default='resignation')
    
    # حسابات تصفية نهاية الخدمة
    end_of_service_benefit = fields.Float(string='مكافأة نهاية الخدمة', compute='_compute_end_of_service_benefit', store=True)
    notice_period_amount = fields.Float(string='بدل فترة الإشعار')
    remaining_vacation_days = fields.Float(string='أيام الإجازة المتبقية')
    vacation_amount = fields.Float(string='مبلغ الإجازات المتبقية', compute='_compute_vacation_amount', store=True)
    other_benefits = fields.Float(string='مزايا أخرى')
    
    # خصومات
    advance_deduction = fields.Float(string='خصم السلف')
    loan_deduction = fields.Float(string='خصم القروض')
    other_deductions = fields.Float(string='خصومات أخرى')
    total_deductions = fields.Float(string='إجمالي الخصومات', compute='_compute_total_deductions', store=True)
    
    # المبلغ النهائي
    gross_amount = fields.Float(string='إجمالي المستحقات', compute='_compute_gross_amount', store=True)
    net_amount = fields.Float(string='صافي المستحقات', compute='_compute_net_amount', store=True)
    
    # حالة التصفية
    state = fields.Selection([
        ('draft', 'مسودة'),
        ('confirmed', 'مؤكد'),
        ('approved', 'معتمد'),
        ('paid', 'مدفوع'),
        ('cancelled', 'ملغي')
    ], string='الحالة', default='draft', tracking=True)
    
    # ملاحظات
    notes = fields.Text(string='ملاحظات')
    
    # معلومات إضافية
    company_id = fields.Many2one('res.company', string='الشركة', default=lambda self: self.env.company)
    currency_id = fields.Many2one('res.currency', string='العملة', related='company_id.currency_id')
    payslip_count = fields.Integer(string='عدد قسائم الراتب', compute='_compute_payslip_count')
    
    @api.depends('basic_salary', 'housing_allowance', 'transport_allowance', 'other_allowances')
    def _compute_total_salary(self):
        for record in self:
            record.total_salary = record.basic_salary + record.housing_allowance + record.transport_allowance + record.other_allowances
    
    def _compute_payslip_count(self):
        """حساب عدد قسائم الراتب للموظف"""
        for record in self:
            record.payslip_count = self.env['hr.payslip'].search_count([('employee_id', '=', record.employee_id.id)])
    
    @api.depends('start_date', 'end_date')
    def _compute_service_period(self):
        for record in self:
            if record.start_date and record.end_date:
                # حساب الفترة بالسنوات والأشهر والأيام
                start = record.start_date
                end = record.end_date
                
                # حساب الفرق
                diff = relativedelta(end, start)
                record.service_years = diff.years
                record.service_months = diff.months
                record.service_days = diff.days
                
                # حساب إجمالي الأيام
                record.total_service_days = (end - start).days + 1
            else:
                record.service_years = 0
                record.service_months = 0
                record.service_days = 0
                record.total_service_days = 0
    
    @api.depends('total_salary', 'service_years', 'service_months', 'service_days', 'termination_type')
    def _compute_end_of_service_benefit(self):
        for record in self:
            if record.total_salary and record.total_service_days:
                record.end_of_service_benefit = record._calculate_saudi_end_of_service_benefit()
            else:
                record.end_of_service_benefit = 0.0
    
    def _calculate_saudi_end_of_service_benefit(self):
        """حساب مكافأة نهاية الخدمة حسب نظام العمل السعودي"""
        self.ensure_one()
        
        if not self.total_salary or not self.total_service_days:
            return 0
        
        # حساب إجمالي سنوات الخدمة بدقة
        total_years = self.service_years + (self.service_months / 12) + (self.service_days / 365)
        
        # حساب المكافأة الأساسية حسب المادة 84 من نظام العمل
        benefit = self._calculate_base_benefit(total_years)
        
        # تطبيق قواعد نوع إنهاء الخدمة
        benefit = self._apply_termination_rules(benefit, total_years)
        
        # تطبيق الحد الأقصى للمكافأة (راتب سنتين)
        max_benefit = self.total_salary * 24
        if benefit > max_benefit:
            benefit = max_benefit
        
        return benefit
    
    def _calculate_base_benefit(self, total_years):
        """حساب المكافأة الأساسية حسب سنوات الخدمة"""
        self.ensure_one()
        
        if total_years >= 5:
            # أول 5 سنوات: نصف شهر عن كل سنة
            first_five_benefit = 5 * (self.total_salary / 2)
            # باقي السنوات: شهر كامل عن كل سنة
            remaining_years = total_years - 5
            remaining_benefit = remaining_years * self.total_salary
            return first_five_benefit + remaining_benefit
        else:
            # أقل من 5 سنوات: نصف شهر عن كل سنة
            return total_years * (self.total_salary / 2)
    
    def _apply_termination_rules(self, base_benefit, total_years):
         """تطبيق قواعد نوع إنهاء الخدمة على المكافأة حسب نظام العمل السعودي"""
         self.ensure_one()
         
         if self.termination_type == 'resignation':
             return self._calculate_resignation_benefit(base_benefit, total_years)
         elif self.termination_type == 'termination_with_cause':
             return 0  # لا يستحق مكافأة في حالة الفصل التأديبي
         elif self.termination_type in ['termination_without_cause', 'end_of_contract', 'retirement', 'death', 'disability', 'mutual_agreement']:
             return base_benefit  # المكافأة كاملة
         else:
             return base_benefit
    
    def _calculate_resignation_benefit(self, base_benefit, total_years):
        """حساب مكافأة الاستقالة حسب المادة 84 من نظام العمل السعودي"""
        self.ensure_one()
        
        if total_years < 2:
            return 0  # لا يستحق مكافأة إذا استقال قبل سنتين
        elif total_years < 5:
            return base_benefit / 3  # ثلث المكافأة إذا استقال بين 2-5 سنوات
        elif total_years < 10:
            return base_benefit * 2 / 3  # ثلثي المكافأة إذا استقال بين 5-10 سنوات
        else:
            return base_benefit  # أكثر من 10 سنوات: المكافأة كاملة
    
    @api.depends('remaining_vacation_days', 'total_salary')
    def _compute_vacation_amount(self):
        for record in self:
            if record.remaining_vacation_days and record.total_salary:
                # حساب قيمة الإجازات المتبقية
                daily_salary = record.total_salary / 30
                record.vacation_amount = record.remaining_vacation_days * daily_salary
            else:
                record.vacation_amount = 0.0
    
    @api.depends('advance_deduction', 'loan_deduction', 'other_deductions')
    def _compute_total_deductions(self):
        for record in self:
            record.total_deductions = record.advance_deduction + record.loan_deduction + record.other_deductions
    
    @api.depends('end_of_service_benefit', 'notice_period_amount', 'vacation_amount', 'other_benefits')
    def _compute_gross_amount(self):
        for record in self:
            record.gross_amount = record.end_of_service_benefit + record.notice_period_amount + record.vacation_amount + record.other_benefits
    
    @api.depends('gross_amount', 'total_deductions')
    def _compute_net_amount(self):
        for record in self:
            record.net_amount = record.gross_amount - record.total_deductions
    
    @api.onchange('employee_id')
    def _onchange_employee_id(self):
        if self.employee_id:
            # التحقق من وجود تصفية سابقة
            existing_settlement = self.search([
                ('employee_id', '=', self.employee_id.id),
                ('state', 'in', ['confirmed', 'approved', 'paid']),
                ('id', '!=', self.id)
            ])
            if existing_settlement:
                raise UserError(_('يوجد تصفية نهاية خدمة سابقة لهذا الموظف!'))
            
            # جلب معلومات العقد الحالي
            contract = self.env['hr.contract'].search([
                ('employee_id', '=', self.employee_id.id),
                ('state', '=', 'open')
            ], limit=1)
            
            if contract:
                self.contract_id = contract.id
                self.basic_salary = contract.wage
                self.start_date = contract.date_start
                # جلب البدلات من العقد إذا كانت متوفرة
                if hasattr(contract, 'housing_allowance'):
                    self.housing_allowance = contract.housing_allowance
                if hasattr(contract, 'transport_allowance'):
                    self.transport_allowance = contract.transport_allowance
    
    @api.constrains('start_date', 'end_date')
    def _check_dates(self):
        for record in self:
            if record.start_date and record.end_date:
                if record.end_date < record.start_date:
                    raise ValidationError(_('تاريخ نهاية الخدمة يجب أن يكون بعد تاريخ بداية العمل!'))
    
    @api.constrains('employee_id')
    def _check_existing_settlement(self):
        for record in self:
            if record.employee_id:
                existing = self.search([
                    ('employee_id', '=', record.employee_id.id),
                    ('state', 'in', ['confirmed', 'approved', 'paid']),
                    ('id', '!=', record.id)
                ])
                if existing:
                    raise ValidationError(_('يوجد تصفية نهاية خدمة سابقة لهذا الموظف!'))
    
    def action_confirm(self):
        """تأكيد التصفية"""
        for record in self:
            if record.state != 'draft':
                raise UserError(_('يمكن تأكيد التصفيات في حالة المسودة فقط!'))
            record.state = 'confirmed'
    
    def action_approve(self):
        """اعتماد التصفية"""
        for record in self:
            if record.state != 'confirmed':
                raise UserError(_('يمكن اعتماد التصفيات المؤكدة فقط!'))
            record.state = 'approved'
    
    def action_set_to_paid(self):
        """تحديد كمدفوع"""
        for record in self:
            if record.state != 'approved':
                raise UserError(_('يمكن تحديد التصفيات المعتمدة كمدفوعة فقط!'))
            record.state = 'paid'
            # تحديث حالة الموظف
            record.employee_id.active = False
    
    def action_cancel(self):
        """إلغاء التصفية"""
        for record in self:
            if record.state == 'paid':
                raise UserError(_('لا يمكن إلغاء التصفيات المدفوعة!'))
            record.state = 'cancelled'
    
    def action_reset_to_draft(self):
        """إعادة إلى المسودة"""
        for record in self:
            if record.state == 'paid':
                raise UserError(_('لا يمكن إعادة التصفيات المدفوعة إلى المسودة!'))
            record.state = 'draft'
    
    def action_print_settlement(self):
        """طباعة التصفية"""
        self.ensure_one()
        return self.env.ref('hr_end_of_service_sa.action_report_end_of_service').report_action(self)
    
    def action_view_payslips(self):
        """عرض قسائم الراتب المرتبطة بالموظف"""
        self.ensure_one()
        payslips = self.env['hr.payslip'].search([('employee_id', '=', self.employee_id.id)])
        return {
            'name': _('قسائم الراتب'),
            'type': 'ir.actions.act_window',
            'res_model': 'hr.payslip',
            'view_mode': 'tree,form',
            'domain': [('employee_id', '=', self.employee_id.id)],
            'context': {'default_employee_id': self.employee_id.id},
        }
    
    def name_get(self):
        result = []
        for record in self:
            name = f"{record.employee_id.name} - {record.calculation_date}"
            result.append((record.id, name))
        return result
