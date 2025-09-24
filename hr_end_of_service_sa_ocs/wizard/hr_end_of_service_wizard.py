# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError
from datetime import datetime, date


class HrEndOfServiceWizard(models.TransientModel):
    _name = 'hr.end.of.service.wizard'
    _description = 'معالج إنشاء تصفية نهاية الخدمة'
    
    # معلومات أساسية
    employee_ids = fields.Many2many('hr.employee', string='الموظفين', required=True)
    calculation_date = fields.Date(string='تاريخ الحساب', default=fields.Date.context_today, required=True)
    end_date = fields.Date(string='تاريخ انتهاء الخدمة', default=fields.Date.context_today, required=True)
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
    
    # خيارات إضافية
    include_vacation_settlement = fields.Boolean(string='تضمين تصفية الإجازة', default=True)
    auto_confirm = fields.Boolean(string='تأكيد تلقائي', default=False)
    notes = fields.Text(string='ملاحظات')
    
    # معلومات الشركة
    company_id = fields.Many2one('res.company', string='الشركة', default=lambda self: self.env.company)
    
    @api.constrains('calculation_date', 'end_date')
    def _check_dates(self):
        for record in self:
            if record.calculation_date > record.end_date:
                raise ValidationError(_('تاريخ الحساب يجب أن يكون قبل أو يساوي تاريخ انتهاء الخدمة!'))
    
    @api.onchange('employee_ids')
    def _onchange_employee_ids(self):
        if self.employee_ids:
            # التحقق من وجود تصفيات سابقة
            existing_settlements = self.env['hr.end.of.service'].search([
                ('employee_id', 'in', self.employee_ids.ids),
                ('state', 'in', ['confirmed', 'approved', 'paid'])
            ])
            
            if existing_settlements:
                employee_names = ', '.join(existing_settlements.mapped('employee_id.name'))
                return {
                    'warning': {
                        'title': _('تحذير'),
                        'message': _('يوجد تصفيات نهاية خدمة سابقة للموظفين التاليين: %s') % employee_names
                    }
                }
    
    def action_create_settlements(self):
        """إنشاء تصفيات نهاية الخدمة"""
        self.ensure_one()
        
        if not self.employee_ids:
            raise UserError(_('يجب تحديد موظف واحد على الأقل!'))
        
        created_settlements = self.env['hr.end.of.service']
        
        for employee in self.employee_ids:
            # التحقق من وجود تصفية سابقة
            existing_settlement = self.env['hr.end.of.service'].search([
                ('employee_id', '=', employee.id),
                ('state', 'in', ['confirmed', 'approved', 'paid'])
            ])
            
            if existing_settlement:
                continue  # تخطي الموظف إذا كان له تصفية سابقة
            
            # إنشاء تصفية جديدة
            settlement_vals = self._prepare_settlement_vals(employee)
            settlement = self.env['hr.end.of.service'].create(settlement_vals)
            created_settlements |= settlement
            
            # إنشاء تصفية إجازة إذا كان مطلوباً
            if self.include_vacation_settlement:
                self._create_vacation_settlement(employee, settlement)
            
            # تأكيد تلقائي إذا كان مطلوباً
            if self.auto_confirm:
                settlement.action_confirm()
        
        if not created_settlements:
            raise UserError(_('لم يتم إنشاء أي تصفيات. تأكد من عدم وجود تصفيات سابقة للموظفين المحددين.'))
        
        # عرض التصفيات المنشأة
        if len(created_settlements) == 1:
            return {
                'type': 'ir.actions.act_window',
                'name': _('تصفية نهاية الخدمة'),
                'res_model': 'hr.end.of.service',
                'res_id': created_settlements.id,
                'view_mode': 'form',
                'target': 'current',
            }
        else:
            return {
                'type': 'ir.actions.act_window',
                'name': _('تصفيات نهاية الخدمة'),
                'res_model': 'hr.end.of.service',
                'view_mode': 'tree,form',
                'domain': [('id', 'in', created_settlements.ids)],
                'target': 'current',
            }
    
    def _prepare_settlement_vals(self, employee):
        """تحضير قيم تصفية نهاية الخدمة"""
        self.ensure_one()
        
        # جلب العقد الحالي أو الأخير
        contract = self.env['hr.contract'].search([
            ('employee_id', '=', employee.id),
            ('state', 'in', ['open', 'close'])
        ], order='date_start desc', limit=1)
        
        # حساب تاريخ البداية
        start_date = employee.hire_date or (contract and contract.date_start)
        if not start_date:
            raise UserError(_('لا يمكن تحديد تاريخ بداية الخدمة للموظف %s') % employee.name)
        
        # تحضير القيم الأساسية
        vals = {
            'employee_id': employee.id,
            'calculation_date': self.calculation_date,
            'start_date': start_date,
            'end_date': self.end_date,
            'termination_type': self.termination_type,
            'notes': self.notes,
            'company_id': self.company_id.id,
        }
        
        # إضافة معلومات العقد إذا وجد
        if contract:
            vals.update({
                'contract_id': contract.id,
                'basic_salary': contract.wage,
                'housing_allowance': getattr(contract, 'housing_allowance', 0),
                'transport_allowance': getattr(contract, 'transport_allowance', 0),
                'other_allowances': getattr(contract, 'other_allowances', 0),
            })
        
        return vals
    
    def _create_vacation_settlement(self, employee, end_of_service_settlement):
        """إنشاء تصفية إجازة مرتبطة بتصفية نهاية الخدمة"""
        self.ensure_one()
        
        # جلب العقد الحالي
        contract = self.env['hr.contract'].search([
            ('employee_id', '=', employee.id),
            ('state', 'in', ['open', 'close'])
        ], order='date_start desc', limit=1)
        
        if not contract:
            return
        
        # تحضير قيم تصفية الإجازة
        vacation_vals = {
            'employee_id': employee.id,
            'contract_id': contract.id,
            'calculation_date': self.calculation_date,
            'settlement_period_from': end_of_service_settlement.start_date,
            'settlement_period_to': self.end_date,
            'monthly_salary': contract.wage,
            'notes': f'تصفية إجازة مرتبطة بتصفية نهاية الخدمة رقم {end_of_service_settlement.id}',
        }
        
        vacation_settlement = self.env['hr.annual.leave.settlement'].create(vacation_vals)
        
        # ربط تصفية الإجازة بتصفية نهاية الخدمة
        end_of_service_settlement.write({
            'vacation_settlement_id': vacation_settlement.id
        })
        
        # تأكيد تلقائي إذا كان مطلوباً
        if self.auto_confirm:
            vacation_settlement.action_confirm()
    
    def action_preview_settlements(self):
        """معاينة التصفيات قبل الإنشاء"""
        self.ensure_one()
        
        if not self.employee_ids:
            raise UserError(_('يجب تحديد موظف واحد على الأقل!'))
        
        preview_data = []
        
        for employee in self.employee_ids:
            # التحقق من وجود تصفية سابقة
            existing_settlement = self.env['hr.end.of.service'].search([
                ('employee_id', '=', employee.id),
                ('state', 'in', ['confirmed', 'approved', 'paid'])
            ])
            
            if existing_settlement:
                status = 'يوجد تصفية سابقة'
                estimated_benefit = 0
            else:
                status = 'جاهز للتصفية'
                # حساب تقديري للمكافأة
                estimated_benefit = self._calculate_estimated_benefit(employee)
            
            preview_data.append({
                'employee_name': employee.name,
                'employee_code': employee.employee_id or '',
                'status': status,
                'estimated_benefit': estimated_benefit,
            })
        
        # عرض البيانات في رسالة
        message = "معاينة تصفيات نهاية الخدمة:\n\n"
        for data in preview_data:
            message += f"الموظف: {data['employee_name']} ({data['employee_code']})\n"
            message += f"الحالة: {data['status']}\n"
            if data['estimated_benefit'] > 0:
                message += f"المكافأة المقدرة: {data['estimated_benefit']:,.2f}\n"
            message += "\n"
        
        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': _('معاينة التصفيات'),
                'message': message,
                'type': 'info',
                'sticky': True,
            }
        }
    
    def _calculate_estimated_benefit(self, employee):
        """حساب تقديري لمكافأة نهاية الخدمة"""
        self.ensure_one()
        
        # جلب العقد الحالي
        contract = self.env['hr.contract'].search([
            ('employee_id', '=', employee.id),
            ('state', 'in', ['open', 'close'])
        ], order='date_start desc', limit=1)
        
        if not contract:
            return 0
        
        # حساب سنوات الخدمة
        start_date = employee.hire_date or contract.date_start
        if not start_date:
            return 0
        
        from dateutil.relativedelta import relativedelta
        service_period = relativedelta(self.end_date, start_date)
        total_years = service_period.years + (service_period.months / 12) + (service_period.days / 365)
        
        # حساب الراتب الإجمالي
        total_salary = contract.wage
        total_salary += getattr(contract, 'housing_allowance', 0)
        total_salary += getattr(contract, 'transport_allowance', 0)
        total_salary += getattr(contract, 'other_allowances', 0)
        
        # حساب المكافأة الأساسية
        if total_years >= 5:
            first_five_benefit = 5 * (total_salary / 2)
            remaining_years = total_years - 5
            remaining_benefit = remaining_years * total_salary
            base_benefit = first_five_benefit + remaining_benefit
        else:
            base_benefit = total_years * (total_salary / 2)
        
        # تطبيق قواعد نوع إنهاء الخدمة
        if self.termination_type == 'resignation':
            if total_years < 2:
                return 0
            elif total_years < 5:
                return base_benefit / 3
            elif total_years < 10:
                return base_benefit * 2 / 3
            else:
                return base_benefit
        elif self.termination_type == 'termination_with_cause':
            return 0
        else:
            return base_benefit