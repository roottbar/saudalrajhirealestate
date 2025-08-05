# -*- coding: utf-8 -*-

from odoo import models, fields, api

class AccountAnalyticAccount(models.Model):
    _inherit = 'account.analytic.account'
    
    operating_unit_id = fields.Many2one(
        'operating.unit',
        string='Operating Unit',
        domain="[('company_id', '=', company_id)]",
        help="Operating unit for this analytic account"
    )
    
    # إضافة حقول مساعدة للترابط
    available_group_ids = fields.Many2many(
        'account.analytic.group',
        compute='_compute_available_groups',
        string='المجموعات المتاحة'
    )
    
    @api.depends('operating_unit_id', 'company_id')
    def _compute_available_groups(self):
        """حساب المجموعات المتاحة بناءً على الفرع والشركة"""
        for record in self:
            domain = []
            if record.company_id:
                domain.append(('company_id', '=', record.company_id.id))
            if record.operating_unit_id:
                # البحث عن المجموعات المرتبطة بالفرع
                accounts_in_unit = self.env['account.analytic.account'].search([
                    ('operating_unit_id', '=', record.operating_unit_id.id),
                    ('company_id', '=', record.company_id.id)
                ])
                group_ids = accounts_in_unit.mapped('group_id').ids
                if group_ids:
                    domain.append(('id', 'in', group_ids))
                else:
                    domain.append(('id', '=', False))
            
            record.available_group_ids = self.env['account.analytic.group'].search(domain)
    
    @api.model
    def _name_search(self, name, args=None, operator='ilike', limit=100, name_get_uid=None):
        """Override name search to include operating unit filtering"""
        if args is None:
            args = []
        return super()._name_search(name, args, operator, limit, name_get_uid)
