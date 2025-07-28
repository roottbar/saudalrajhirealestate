# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError


class ConstructionProject(models.Model):
    _inherit = 'project.project'

    project_type = fields.Selection(
        [('construction', 'Construction Project')],
        string='Project Type',
        default='construction'
    )
    total_cost = fields.Float(
        string='Total Project Cost',
        compute='_compute_total_cost',
        store=True
    )
    completion_percentage = fields.Float(
        string='Completion Percentage',
        compute='_compute_completion_percentage'
    )

    @api.depends('task_ids', 'task_ids.stage_cost')
    def _compute_total_cost(self):
        for project in self:
            project.total_cost = sum(task.stage_cost for task in project.task_ids)

    @api.depends('task_ids', 'task_ids.stage_id')
    def _compute_completion_percentage(self):
        for project in self:
            total_tasks = len(project.task_ids)
            if total_tasks == 0:
                project.completion_percentage = 0
            else:
                completed_tasks = len(project.task_ids.filtered(lambda t: t.stage_id.is_closed))
                project.completion_percentage = (completed_tasks / total_tasks) * 100


class ConstructionTask(models.Model):
    _inherit = 'project.task'

    material_ids = fields.One2many(
        'construction.task.material',
        'task_id',
        string='Materials'
    )
    labor_ids = fields.One2many(
        'construction.task.labor',
        'task_id',
        string='Labor'
    )
    equipment_ids = fields.One2many(
        'construction.task.equipment',
        'task_id',
        string='Equipment'
    )
    stage_cost = fields.Float(
        string='Stage Cost',
        compute='_compute_stage_cost',
        store=True
    )

    @api.depends('material_ids.total_cost', 'labor_ids.total_cost', 'equipment_ids.total_cost')
    def _compute_stage_cost(self):
        for task in self:
            material_cost = sum(material.total_cost for material in task.material_ids)
            labor_cost = sum(labor.total_cost for labor in task.labor_ids)
            equipment_cost = sum(equipment.total_cost for equipment in task.equipment_ids)
            task.stage_cost = material_cost + labor_cost + equipment_cost


class ConstructionTaskMaterial(models.Model):
    _name = 'construction.task.material'
    _description = 'Construction Task Material'

    task_id = fields.Many2one(
        'project.task',
        string='Task'
    )
    product_id = fields.Many2one(
        'product.product',
        string='Material',
        domain=[('type', '=', 'product')],
        required=True
    )
    quantity = fields.Float(
        string='Quantity',
        default=1.0
    )
    uom_id = fields.Many2one(
        'uom.uom',
        string='Unit of Measure',
        related='product_id.uom_id',
        readonly=True
    )
    cost_per_unit = fields.Float(
        string='Cost Per Unit',
        related='product_id.standard_price',
        readonly=True
    )
    total_cost = fields.Float(
        string='Total Cost',
        compute='_compute_total_cost',
        store=True
    )

    @api.depends('quantity', 'cost_per_unit')
    def _compute_total_cost(self):
        for material in self:
            material.total_cost = material.quantity * material.cost_per_unit


class ConstructionTaskLabor(models.Model):
    _name = 'construction.task.labor'
    _description = 'Construction Task Labor'
    
    task_id = fields.Many2one('project.task', string='Task')
    employee_id = fields.Many2one('hr.employee', string='Employee', required=True)
    hours = fields.Float(string='Hours', default=1.0)
    total_cost = fields.Float(
        string='Total Cost',
        compute='_compute_total_cost',
        store=True
    )
    
    @api.depends('hours', 'employee_id.timesheet_cost')
    def _compute_total_cost(self):
        for labor in self:
            rate = labor.employee_id.timesheet_cost or 0.0
            labor.total_cost = labor.hours * rate


class ConstructionTaskEquipment(models.Model):
    _name = 'construction.task.equipment'
    _description = 'Construction Task Equipment'

    task_id = fields.Many2one(
        'project.task',
        string='Task'
    )
    equipment_id = fields.Many2one(
        'maintenance.equipment',
        string='Equipment',
        required=True
    )
    hours = fields.Float(
        string='Hours Used',
        default=1.0
    )
    hourly_cost = fields.Float(
        string='Hourly Cost',
        compute='_compute_hourly_cost'
    )
    total_cost = fields.Float(
        string='Total Cost',
        compute='_compute_total_cost',
        store=True
    )

    @api.depends('equipment_id')
    def _compute_hourly_cost(self):
        for equipment in self:
            # You can customize this calculation based on your equipment cost model
            equipment.hourly_cost = equipment.equipment_id.maintenance_cost_period == 'hour' and equipment.equipment_id.maintenance_cost_amount or 0.0

    @api.depends('hours', 'hourly_cost')
    def _compute_total_cost(self):
        for equipment in self:
            equipment.total_cost = equipment.hours * equipment.hourly_cost
