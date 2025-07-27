# -*- coding: utf-8 -*-

from odoo import api, fields, models

class MrpProduction(models.Model):
    _inherit = 'mrp.production'

    project_id = fields.Many2one(
        'project.project', 'Project',
        help="Project to which this production order is linked."
    )
    analytic_account_id = fields.Many2one(
        related='project_id.analytic_account_id',
        string='Analytic Account',
        store=True,
        readonly=True
    )
    
    partner_id = fields.Many2one(
        'res.partner', 
        string='Customer',
        compute='_compute_partner_id',
        store=True,
        help="Customer from the related sales order"
    )
    
    @api.depends('origin')
    def _compute_partner_id(self):
        for production in self:
            partner_id = False
            if production.origin:
                # البحث عن أمر البيع المرتبط
                sale_order = self.env['sale.order'].search([
                    ('name', '=', production.origin)
                ], limit=1)
                if sale_order:
                    partner_id = sale_order.partner_id.id
            production.partner_id = partner_id

    def _prepare_project_values(self):
        return {
            'name': self.name,
            'partner_id': self.partner_id.id if self.partner_id else False,
            'user_id': self.user_id.id,
            'company_id': self.company_id.id,
        }

    def _prepare_production_task_values(self, project):
        return {
            'name': '%s: %s' % (self.name, self.product_id.name),
            'project_id': project.id,
            'user_id': self.user_id.id,
            'partner_id': self.partner_id.id if self.partner_id else False,
            'company_id': self.company_id.id,
            'description': 'Manufacturing Order: %s' % self.name,
        }

    @api.model
    def create(self, vals):
        production = super(MrpProduction, self).create(vals)
        if production.project_id:
            production._create_production_task()
        return production

    def write(self, vals):
        result = super(MrpProduction, self).write(vals)
        if 'project_id' in vals:
            for production in self:
                if production.project_id:
                    production._create_production_task()
        return result

    def _create_production_task(self):
        if self.project_id:
            task_vals = self._prepare_production_task_values(self.project_id)
            task = self.env['project.task'].create(task_vals)
            return task
        return False

    def action_confirm(self):
        result = super(MrpProduction, self).action_confirm()
        for production in self:
            if not production.project_id and production.analytic_account_id:
                # إنشاء مشروع تلقائياً إذا كان هناك حساب تحليلي
                project_vals = production._prepare_project_values()
                project_vals['analytic_account_id'] = production.analytic_account_id.id
                project = self.env['project.project'].create(project_vals)
                production.project_id = project.id
                production._create_production_task()
        return result

    def unlink(self):
        # حذف المهام المرتبطة
        tasks = self.env['project.task'].search([
            ('name', 'like', self.name)
        ])
        tasks.unlink()
        return super(MrpProduction, self).unlink()
