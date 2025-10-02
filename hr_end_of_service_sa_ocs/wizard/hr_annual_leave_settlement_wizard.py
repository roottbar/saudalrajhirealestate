# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError
from datetime import datetime, date
from dateutil.relativedelta import relativedelta


class HrAnnualLeaveSettlementWizard(models.TransientModel):
    _name = 'hr.annual.leave.settlement.wizard'
    _description = 'معالج إنشاء تصفية الإجازة السنوية'
    
    # معلومات أساسية
    employee_id = fields.Many2one('hr.employee', string='الموظف')
    employee_ids = fields.Many2many('hr.employee', string='الموظفين')
    calculation_date = fields.Date(string='تاريخ الحساب', default=fields.Date.context_today, required=True)
    settlement_type = fields.Selection([
        ('annual', 'تصفية سنوية'),
        ('end_of_service', 'تصفية نهاية خدمة'),
        ('custom', 'تصفية مخصصة')
    ], string='نوع التصفية', default='annual', required=True)
    
    # فترة التصفية
    settlement_period_from = fields.Date(string='من تاريخ', required=True)
    settlement_period_to = fields.Date(string='إلى تاريخ', required=True)
    settlement_date = fields.Date(string='تاريخ التصفية', default=fields.Date.context_today)
    
    # إعدادات الإجازة
    annual_leave_days = fields.Float(string='أيام الإجازة السنوية', default=22.0, help='22 يوم حسب النظام السعودي')
    include_used_leaves = fields.Boolean(string='احتساب الإجازات المستخدمة', default=True)
    
    # خيارات إضافية
    auto_confirm = fields.Boolean(string='تأكيد تلقائي', default=False)
    notes = fields.Text(string='ملاحظات')
    
    # معلومات الشركة
    company_id = fields.Many2one('res.company', string='الشركة', default=lambda self: self.env.company)
    
    @api.constrains('settlement_period_from', 'settlement_period_to')
    def _check_settlement_period(self):
        for record in self:
            if record.settlement_period_from >= record.settlement_period_to:
                raise ValidationError(_('تاريخ البداية يجب أن يكون قبل تاريخ النهاية!'))
    
    @api.constrains('annual_leave_days')
    def _check_annual_leave_days(self):
        for record in self:
            if record.annual_leave_days < 0:
                raise ValidationError(_('أيام الإجازة السنوية لا يمكن أن تكون سالبة!'))
    
    @api.onchange('settlement_type')
    def _onchange_settlement_type(self):
        if self.settlement_type == 'annual':
            # تعيين فترة السنة الحالية
            today = date.today()
            self.settlement_period_from = date(today.year, 1, 1)
            self.settlement_period_to = date(today.year, 12, 31)
        elif self.settlement_type == 'end_of_service':
            # تعيين فترة من بداية السنة حتى اليوم
            today = date.today()
            self.settlement_period_from = date(today.year, 1, 1)
            self.settlement_period_to = today
    
    @api.onchange('employee_id')
    def _onchange_employee_id(self):
        if self.employee_id and self.settlement_type == 'annual':
            # تعيين فترة التصفية حسب تاريخ توظيف الموظف
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
    
    @api.onchange('employee_ids')
    def _onchange_employee_ids(self):
        if self.employee_ids and self.settlement_type == 'annual':
            # تعيين فترة التصفية حسب تاريخ توظيف أول موظف
            first_employee = self.employee_ids[0]
            if first_employee.hire_date:
                hire_date = first_employee.hire_date
                current_year = date.today().year
                
                # حساب بداية ونهاية السنة المالية للإجازة
                year_start = date(current_year, hire_date.month, hire_date.day)
                if year_start > date.today():
                    year_start = date(current_year - 1, hire_date.month, hire_date.day)
                
                year_end = year_start + relativedelta(years=1) - relativedelta(days=1)
                
                self.settlement_period_from = year_start
                self.settlement_period_to = min(year_end, date.today())
    
    def action_create_settlements(self):
        """إنشاء تصفيات الإجازة السنوية"""
        self.ensure_one()
        
        # تحديد الموظفين المراد إنشاء تصفيات لهم
        employees = self.employee_ids if self.employee_ids else self.employee_id
        if not employees:
            raise UserError(_('يجب تحديد موظف واحد على الأقل!'))
        
        created_settlements = self.env['hr.annual.leave.settlement']
        
        for employee in employees:
            # إنشاء تصفية جديدة
            settlement_vals = self._prepare_settlement_vals(employee)
            settlement = self.env['hr.annual.leave.settlement'].create(settlement_vals)
            created_settlements |= settlement
            
            # تأكيد تلقائي إذا كان مطلوباً
            if self.auto_confirm:
                settlement.action_confirm()
        
        if not created_settlements:
            raise UserError(_('لم يتم إنشاء أي تصفيات.'))
        
        # عرض التصفيات المنشأة
        if len(created_settlements) == 1:
            return {
                'type': 'ir.actions.act_window',
                'name': _('تصفية الإجازة السنوية'),
                'res_model': 'hr.annual.leave.settlement',
                'res_id': created_settlements.id,
                'view_mode': 'form',
                'target': 'current',
            }
        else:
            return {
                'type': 'ir.actions.act_window',
                'name': _('تصفيات الإجازة السنوية'),
                'res_model': 'hr.annual.leave.settlement',
                'view_mode': 'tree,form',
                'domain': [('id', 'in', created_settlements.ids)],
                'target': 'current',
            }
    
    def _prepare_settlement_vals(self, employee):
        """تحضير قيم تصفية الإجازة السنوية"""
        self.ensure_one()
        
        # جلب العقد الحالي أو الأخير
        contract = self.env['hr.contract'].search([
            ('employee_id', '=', employee.id),
            ('state', 'in', ['open', 'close'])
        ], order='date_start desc', limit=1)
        
        if not contract:
            raise UserError(_('لا يوجد عقد للموظف %s') % employee.name)
        
        # تحضير القيم الأساسية
        vals = {
            'employee_id': employee.id,
            'contract_id': contract.id,
            'calculation_date': self.calculation_date,
            'settlement_period_from': self.settlement_period_from,
            'settlement_period_to': self.settlement_period_to,
            'settlement_date': self.settlement_date,
            'basic_salary': contract.wage,
            'housing_allowance': 0.0,
            'transport_allowance': 0.0,
            'other_allowances': 0.0,
            'monthly_salary': contract.wage,
            'total_leave_days': self.annual_leave_days,
            'notes': self.notes,
        }
        
        # حساب أيام الإجازة المستخدمة إذا كان مطلوباً
        if self.include_used_leaves:
            used_days = self._calculate_used_leave_days(employee)
            vals['used_leave_days'] = used_days
        
        return vals
    
    def _calculate_used_leave_days(self, employee):
        """حساب أيام الإجازة المستخدمة"""
        self.ensure_one()
        
        # البحث عن إجازات الموظف في الفترة المحددة
        leave_requests = self.env['hr.leave'].search([
            ('employee_id', '=', employee.id),
            ('state', '=', 'validate'),
            ('request_date_from', '>=', self.settlement_period_from),
            ('request_date_to', '<=', self.settlement_period_to),
            ('holiday_status_id.unpaid', '=', False),  # الإجازات المدفوعة فقط
        ])
        
        return sum(leave_requests.mapped('number_of_days'))
    
    def action_preview_settlements(self):
        """معاينة التصفيات قبل الإنشاء"""
        self.ensure_one()
        
        # تحديد الموظفين المراد معاينة تصفياتهم
        employees = self.employee_ids if self.employee_ids else self.employee_id
        if not employees:
            raise UserError(_('يجب تحديد موظف واحد على الأقل!'))
        
        preview_data = []
        
        for employee in employees:
            # جلب العقد الحالي
            contract = self.env['hr.contract'].search([
                ('employee_id', '=', employee.id),
                ('state', 'in', ['open', 'close'])
            ], order='date_start desc', limit=1)
            
            if not contract:
                status = 'لا يوجد عقد'
                estimated_amount = 0
                used_days = 0
                remaining_days = 0
            else:
                status = 'جاهز للتصفية'
                # حساب أيام الإجازة المستخدمة
                used_days = self._calculate_used_leave_days(employee) if self.include_used_leaves else 0
                remaining_days = self.annual_leave_days - used_days
                # حساب المبلغ المقدر
                daily_salary = contract.wage / 30
                estimated_amount = remaining_days * daily_salary
            
            preview_data.append({
                'employee_name': employee.name,
                'employee_code': employee.employee_id or '',
                'status': status,
                'monthly_salary': contract.wage if contract else 0,
                'used_days': used_days,
                'remaining_days': remaining_days,
                'estimated_amount': estimated_amount,
            })
        
        # عرض البيانات في رسالة
        message = "معاينة تصفيات الإجازة السنوية:\n\n"
        total_amount = 0
        
        for data in preview_data:
            message += f"الموظف: {data['employee_name']} ({data['employee_code']})\n"
            message += f"الحالة: {data['status']}\n"
            if data['monthly_salary'] > 0:
                message += f"الراتب الشهري: {data['monthly_salary']:,.2f}\n"
                message += f"أيام الإجازة المستخدمة: {data['used_days']:.1f}\n"
                message += f"أيام الإجازة المتبقية: {data['remaining_days']:.1f}\n"
                message += f"المبلغ المقدر: {data['estimated_amount']:,.2f}\n"
                total_amount += data['estimated_amount']
            message += "\n"
        
        message += f"إجمالي المبلغ المقدر: {total_amount:,.2f}"
        
        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': _('معاينة تصفيات الإجازة'),
                'message': message,
                'type': 'info',
                'sticky': True,
            }
        }
    
    def action_calculate_for_period(self):
        """حساب الإجازة لفترة محددة"""
        self.ensure_one()
        
        # تحديد الموظفين المراد حساب إجازاتهم
        employees = self.employee_ids if self.employee_ids else self.employee_id
        if not employees:
            raise UserError(_('يجب تحديد موظف واحد على الأقل!'))
        
        # حساب عدد الأشهر في الفترة
        period_months = relativedelta(self.settlement_period_to, self.settlement_period_from).months
        period_months += relativedelta(self.settlement_period_to, self.settlement_period_from).years * 12
        
        # حساب أيام الإجازة المستحقة للفترة (22 يوم سنوياً)
        if period_months > 0:
            proportional_days = (self.annual_leave_days / 12) * period_months
            self.annual_leave_days = proportional_days
        
        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': _('حساب الإجازة للفترة'),
                'message': f'تم حساب {proportional_days:.1f} يوم إجازة للفترة من {self.settlement_period_from} إلى {self.settlement_period_to}',
                'type': 'success',
            }
        }
    
    def action_bulk_create_annual_settlements(self):
        """إنشاء تصفيات سنوية جماعية لجميع الموظفين"""
        self.ensure_one()
        
        # جلب جميع الموظفين النشطين
        active_employees = self.env['hr.employee'].search([
            ('active', '=', True),
            ('company_id', '=', self.company_id.id)
        ])
        
        if not active_employees:
            raise UserError(_('لا يوجد موظفين نشطين في الشركة!'))
        
        self.employee_ids = [(6, 0, active_employees.ids)]
        
        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': _('تحديد الموظفين'),
                'message': f'تم تحديد {len(active_employees)} موظف للتصفية الجماعية',
                'type': 'success',
            }
        }
