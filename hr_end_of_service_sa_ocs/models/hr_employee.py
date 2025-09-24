# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from datetime import datetime, date


class HrEmployee(models.Model):
    _inherit = 'hr.employee'
    
    # حقول تصفية نهاية الخدمة
    end_of_service_ids = fields.One2many('hr.end.of.service', 'employee_id', string='تصفيات نهاية الخدمة')
    end_of_service_count = fields.Integer(string='عدد التصفيات', compute='_compute_end_of_service_count')
    has_end_of_service = fields.Boolean(string='له تصفية نهاية خدمة', compute='_compute_has_end_of_service')
    last_end_of_service_date = fields.Date(string='تاريخ آخر تصفية', compute='_compute_last_end_of_service_date')
    
    # حقول تصفية الإجازة السنوية
    annual_leave_settlement_ids = fields.One2many('hr.annual.leave.settlement', 'employee_id', string='تصفيات الإجازة السنوية')
    annual_leave_settlement_count = fields.Integer(string='عدد تصفيات الإجازة', compute='_compute_annual_leave_settlement_count')
    
    # معلومات إضافية للحسابات
    hire_date = fields.Date(string='تاريخ التوظيف', help='تاريخ بداية العمل الفعلي')
    probation_period_months = fields.Integer(string='فترة التجربة (بالأشهر)', default=3)
    is_probation_completed = fields.Boolean(string='انتهت فترة التجربة', compute='_compute_probation_status')
    
    @api.depends('end_of_service_ids')
    def _compute_end_of_service_count(self):
        for employee in self:
            employee.end_of_service_count = len(employee.end_of_service_ids)
    
    @api.depends('end_of_service_ids')
    def _compute_has_end_of_service(self):
        for employee in self:
            approved_settlements = employee.end_of_service_ids.filtered(
                lambda x: x.state in ['confirmed', 'approved', 'paid']
            )
            employee.has_end_of_service = bool(approved_settlements)
    
    @api.depends('end_of_service_ids')
    def _compute_last_end_of_service_date(self):
        for employee in self:
            if employee.end_of_service_ids:
                last_settlement = employee.end_of_service_ids.sorted('calculation_date', reverse=True)[0]
                employee.last_end_of_service_date = last_settlement.calculation_date
            else:
                employee.last_end_of_service_date = False
    
    @api.depends('annual_leave_settlement_ids')
    def _compute_annual_leave_settlement_count(self):
        for employee in self:
            employee.annual_leave_settlement_count = len(employee.annual_leave_settlement_ids)
    
    @api.depends('hire_date', 'probation_period_months')
    def _compute_probation_status(self):
        for employee in self:
            if employee.hire_date and employee.probation_period_months:
                from dateutil.relativedelta import relativedelta
                probation_end = employee.hire_date + relativedelta(months=employee.probation_period_months)
                employee.is_probation_completed = date.today() > probation_end
            else:
                employee.is_probation_completed = False
    
    def action_create_end_of_service(self):
        """إنشاء تصفية نهاية خدمة جديدة"""
        self.ensure_one()
        
        # التحقق من وجود تصفية سابقة
        existing_settlement = self.env['hr.end.of.service'].search([
            ('employee_id', '=', self.id),
            ('state', 'in', ['confirmed', 'approved', 'paid'])
        ])
        
        if existing_settlement:
            raise UserError(_('يوجد تصفية نهاية خدمة سابقة لهذا الموظف!'))
        
        # إنشاء تصفية جديدة
        settlement_vals = {
            'employee_id': self.id,
        }
        
        # جلب معلومات العقد الحالي
        contract = self.env['hr.contract'].search([
            ('employee_id', '=', self.id),
            ('state', '=', 'open')
        ], limit=1)
        
        if contract:
            settlement_vals.update({
                'contract_id': contract.id,
                'basic_salary': contract.wage,
                'start_date': contract.date_start or self.hire_date,
            })
        elif self.hire_date:
            settlement_vals['start_date'] = self.hire_date
        
        settlement = self.env['hr.end.of.service'].create(settlement_vals)
        
        return {
            'type': 'ir.actions.act_window',
            'name': _('تصفية نهاية الخدمة'),
            'res_model': 'hr.end.of.service',
            'res_id': settlement.id,
            'view_mode': 'form',
            'target': 'current',
        }
    
    def action_view_end_of_service(self):
        """عرض تصفيات نهاية الخدمة"""
        self.ensure_one()
        action = self.env.ref('hr_end_of_service_sa.action_hr_end_of_service').read()[0]
        action['domain'] = [('employee_id', '=', self.id)]
        action['context'] = {'default_employee_id': self.id}
        return action
    
    def action_create_annual_leave_settlement(self):
        """إنشاء تصفية إجازة سنوية جديدة"""
        self.ensure_one()
        
        settlement_vals = {
            'employee_id': self.id,
        }
        
        # جلب معلومات العقد الحالي
        contract = self.env['hr.contract'].search([
            ('employee_id', '=', self.id),
            ('state', '=', 'open')
        ], limit=1)
        
        if contract:
            settlement_vals.update({
                'contract_id': contract.id,
                'monthly_salary': contract.wage,
            })
        
        settlement = self.env['hr.annual.leave.settlement'].create(settlement_vals)
        
        return {
            'type': 'ir.actions.act_window',
            'name': _('تصفية الإجازة السنوية'),
            'res_model': 'hr.annual.leave.settlement',
            'res_id': settlement.id,
            'view_mode': 'form',
            'target': 'current',
        }
    
    def action_view_annual_leave_settlements(self):
        """عرض تصفيات الإجازة السنوية"""
        self.ensure_one()
        action = self.env.ref('hr_end_of_service_sa.action_hr_annual_leave_settlement').read()[0]
        action['domain'] = [('employee_id', '=', self.id)]
        action['context'] = {'default_employee_id': self.id}
        return action
    
    def get_service_years(self, end_date=None):
        """حساب سنوات الخدمة"""
        self.ensure_one()
        if not end_date:
            end_date = date.today()
        
        start_date = self.hire_date or (self.contract_ids and self.contract_ids[0].date_start)
        if not start_date:
            return 0
        
        from dateutil.relativedelta import relativedelta
        diff = relativedelta(end_date, start_date)
        return diff.years + (diff.months / 12) + (diff.days / 365)
    
    def get_current_salary_components(self):
        """جلب مكونات الراتب الحالي"""
        self.ensure_one()
        contract = self.env['hr.contract'].search([
            ('employee_id', '=', self.id),
            ('state', '=', 'open')
        ], limit=1)
        
        if contract:
            return {
                'basic_salary': contract.wage,
                'housing_allowance': getattr(contract, 'housing_allowance', 0),
                'transport_allowance': getattr(contract, 'transport_allowance', 0),
                'other_allowances': getattr(contract, 'other_allowances', 0),
            }
        return {
            'basic_salary': 0,
            'housing_allowance': 0,
            'transport_allowance': 0,
            'other_allowances': 0,
        }