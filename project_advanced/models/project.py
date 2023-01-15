# -*- coding: utf-8 -*-
from odoo import api, fields, models


class Project(models.Model):
    _inherit = "project.project"

    project_task_template_id = fields.Many2one("project.task.template", string="Template")
    allowed_user_ids = fields.Many2many("res.users", string="Allowed Users")

    @api.onchange('project_task_template_id')
    def onchange_project_task_template(self):
        if self.project_task_template_id:
            stages = self.project_task_template_id.type_ids.ids
            task_stages = self.mapped("task_ids.stage_id")
            if task_stages:
                stages += task_stages.ids
            self.type_ids = [(6, 0, stages)]


class ProjectTask(models.Model):
    _inherit = "project.task"

    in_progress = fields.Boolean(related="stage_id.in_progress", string="In progress", radonly=True, store=True)
    is_ready = fields.Boolean(related="stage_id.is_ready", string="Is Ready", radonly=True, store=True)
    is_review = fields.Boolean(related="stage_id.is_review", string="Is Review", radonly=True, store=True)
    is_closed = fields.Boolean(related="stage_id.is_closed", string="Is Closed", radonly=True, store=True)
    start_date = fields.Datetime(string="Start Date", copy=False, tracking=True)
    privacy_visibility = fields.Selection(related="project_id.privacy_visibility", string="Visibility", radonly=True,
                                          store=True)
    allowed_user_ids = fields.Many2many("res.users", string="Allowed Users")
    assign_history_ids = fields.One2many("project.task.assign.history", "task_id", string="Assign History",
                                         ondelete="cascade", readonly=True)
    ref = fields.Char(string="Reference", index=True, readonly=True, copy=False)

    @api.model
    def create(self, vals):
        vals.update({"ref": self.env['ir.sequence'].next_by_code('project.task')})
        return super(ProjectTask, self).create(vals)

    def write(self, vals):
        for rec in self:
            if not rec.ref:
                vals.update({"ref": self.env['ir.sequence'].next_by_code('project.task')})
        return super(ProjectTask, self).write(vals)

    def name_get(self):
        result = []
        for rec in self:
            result.append((rec.id, "%s" % (rec.name)))
        return result

    @api.model
    def name_search(self, name='', args=None, operator='ilike', limit=100):
        args = args or []
        domain_name = ['|', ('name', 'ilike', name), ('ref', 'ilike', name)]
        recs = self.search(domain_name + args, limit=limit)
        return recs.name_get()

    @api.onchange("project_id")
    def onchange_project(self):
        self.allowed_user_ids = self.project_id.allowed_user_ids

    @api.onchange('start_date')
    def onchange_start_date(self):
        self.planned_date_begin = self.start_date

    @api.onchange('planned_date_begin', "planned_hours")
    def onchange_planned_date_begin(self):
        planned_date_end = False
        if self.user_id and self.sudo().user_id.employee_id and self.planned_hours and self.planned_date_begin:
            # get resource calendar of user
            employee = self.sudo().user_id.employee_id
            calendar = employee.contract_id.resource_calendar_id or employee.resource_calendar_id

            planned_date_end = calendar.plan_hours(self.planned_hours, self.planned_date_begin, compute_leaves=True)
        self.planned_date_end = planned_date_end

    def calc_expect_start_date(self):
        start_date = False
        if self.user_id and self.sudo().user_id.employee_id:
            # get tasks of user
            tasks = self.sudo().search(
                [('id', '!=', self.id), ('user_id', '=', self.user_id.id), ('planned_date_end', '!=', False),
                 ('is_closed', '=', False)])
            # get resource calendar of user
            employee = self.sudo().user_id.employee_id
            resource_calendar = employee.contract_id.resource_calendar_id or employee.resource_calendar_id

            if resource_calendar and tasks:
                # get last end date of tasks
                date = tasks[0].planned_date_end
                for task in tasks[1:]:
                    if date < task.planned_date_end:
                        date = task.planned_date_end

                # get duration between tasks from settings
                duration_between_tasks = self.env['ir.config_parameter'].sudo().get_param(
                    'project_advanced.duration_between_tasks', False)

                start_date = resource_calendar.plan_hours(float(duration_between_tasks), date, compute_leaves=True)

        self.start_date = start_date
        self.planned_date_begin = self.start_date
        self.onchange_planned_date_begin()


class ProjectTaskType(models.Model):
    _inherit = "project.task.type"

    in_progress = fields.Boolean(string="In progress", copy=False)
    is_ready = fields.Boolean(string="Is Ready", copy=False)
    is_review = fields.Boolean(string="Is Review", copy=False)


class ProjectTaskAssignHistory(models.Model):
    _name = 'project.task.assign.history'

    old_user_id = fields.Many2one("res.users", string="Old Assign User")
    new_user_id = fields.Many2one("res.users", string="New Assign User", required=True)
    task_id = fields.Many2one("project.task", string="Task", required=True)
    description = fields.Text(string="Description")
