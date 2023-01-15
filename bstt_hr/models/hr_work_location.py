#!/usr/bin/python
# -*- coding: utf-8 -*-

from odoo import models, fields, api, _


class WorkLocation(models.Model):
    _name = "hr.work.location"
    _description = "Work Location"
    _order = 'name'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    active = fields.Boolean(default=True)
    name = fields.Char(string="Work Location", required=True)
    company_id = fields.Many2one('res.company', required=True, default=lambda self: self.env.company)
    address_id = fields.Many2one('res.partner', required=True, string="Work Address", domain="['|', ('company_id', '=', False), ('company_id', '=', company_id)]")
    location_number = fields.Char()

    project_id = fields.Many2one('project.project', 'المشروع', index=True, copy=False)
    analytic_account_id = fields.Many2one('account.analytic.account', string="الحساب التحليلي", copy=False)

    @api.onchange('project_id')
    def _onchange_project_id(self):
        self.analytic_account_id = False
        if self.project_id.id:
            analytic_account_id = self.env['account.analytic.account'].search([('project_ids', 'in', [self.project_id.id])], limit=1)
            self.analytic_account_id = analytic_account_id

