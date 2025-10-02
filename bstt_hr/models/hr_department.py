#!/usr/bin/python
# -*- coding: utf-8 -*-

from odoo import models, fields, api, _


class Department(models.Model):
    _inherit = "hr.department"

    dept_type = fields.Selection(selection=[
            ('company', 'شركة'),
            ('branch', 'فرع'),
            ('ministry', 'إدارة'),
            ('department', 'قسم'),
        ], string='النوع', required=True, copy=True, tracking=True, default='department')
    code = fields.Char("الكود", required=True)

    analytic_account = fields.Many2one('account.analytic.account', string='الحساب التحليلي', ondelete='restrict', readonly=True)
    ref_analytic_account = fields.Char(string='رقم اشارة الحساب التحليلي', readonly=True)
    # Odoo 18: account.analytic.group model removed; drop grouped analytic account linkage.
    # group_analytic_account = fields.Many2one('account.analytic.group', string='الحساب التحليلي المجمع', ondelete='restrict', readonly=True)

    # @api.onchange('code')
    # def _onchange_code(self):
    #     # Analytic Accounts
    #     self.ref_analytic_account = str(self.parent_id.ref_analytic_account) + str(
    #         self.code) if self.parent_id else '' + str(self.code)
    #     group_analytic_account = self.env['account.analytic.group'].sudo().create(
    #         {'name': self.name, 'parent_id': self.parent_id.group_analytic_account.id or False})
    #     analytic_account = self.env['account.analytic.account'].sudo().create(
    #         {'name': self.name, 'group_id': self.group_analytic_account.id, 'code': self.ref_analytic_account})
    #     self.analytic_account = analytic_account
    #     self.group_analytic_account = group_analytic_account

    @api.model
    def create(self, vals):
        obj = super(Department, self).create(vals)
        # Analytic Accounts
        obj.ref_analytic_account = str(obj.parent_id.ref_analytic_account) + str(obj.code) if obj.parent_id else str(obj.code)
        # Odoo 18: analytic groups were removed. Create a plain analytic account without group linkage.
        analytic_account = self.env['account.analytic.account'].sudo().create({
            'name': obj.name,
            'code': obj.ref_analytic_account,
        })
        obj.analytic_account = analytic_account
        return obj
