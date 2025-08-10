from dateutil.relativedelta import relativedelta

from odoo import _, api, fields, models

DATE_OPTIONS = [
    ("1_weeks", _("1 Week")),
    ("2_weeks", _("2 Weeks")),
    ("1_months", _("1 Month")),
    ("2_months", _("2 Month")),
    ("1_years", _("1 Year")),
    ("2_years", _("2 Years")),
    ("custom", _("Custom")),
]


class ProjectSprint(models.Model):
    _name = "project.sprint"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _description = "Project Sprint"
    _sql_constraints = [
        (
            "date_check",
            "CHECK (date_start <= date_end)",
            _("Error: End date must be greater than start date!"),
        ),
    ]

    name = fields.Char(required=True, track_visibility='onchange')
    user_ids = fields.Many2many(
        comodel_name="res.users",
        string="Members",
        required=True,
        domain="[('share', '=', False), ('active', '=', True)]",
        track_visibility='onchange',
        relation="project_sprint_user_rel",
    )
    description = fields.Text(track_visibility='onchange')
    project_id = fields.Many2one(
        comodel_name="project.project",
        string="Project",
        track_visibility='onchange',
    )
    task_ids = fields.One2many(
        comodel_name="project.task",
        inverse_name="sprint_id",
        string="Tasks",
        domain="[('project_id', '=', project_id)]",
    )
    date_start = fields.Date(
        string="Start Date", default=fields.Date.today, required=True
    )
    date_option = fields.Selection(
        selection=DATE_OPTIONS, default=DATE_OPTIONS[0][0], required=True
    )
    date_end = fields.Date(
        string="End Date",
        required=True,
        compute="_compute_date_end",
        store=True,
        readonly=False,
    )
    state = fields.Selection(
        selection=[
            ("draft", "Draft"),
            ("in_progress", "In progress"),
            ("done", "Done"),
        ],
        default="draft",
    )
    tasks_count = fields.Integer(compute="_compute_tasks_count")

    def _compute_tasks_count(self):
        for sprint in self:
            sprint.tasks_count = len(sprint.task_ids)

    def action_start(self):
        self.state = "in_progress"

    def action_done(self):
        self.state = "done"
        self._check_task_state()

    def action_tasks(self):
        self.ensure_one()
        return {
            "name": _("Tasks"),
            "type": "ir.actions.act_window",
            "res_model": "project.task",
            "view_mode": "tree,form",
            "domain": [("sprint_id", "=", self.id)],
            "context": {"default_sprint_id": self.id},
        }

    @api.model
    def cron_update_sprint_state(self):
        sprints = self.search([("state", "=", "in_progress")])
        for sprint in sprints:
            if sprint.date_end < fields.Date.today():
                sprint.action_done()
        sprints = self.search([("state", "=", "draft")])
        for sprint in sprints:
            if sprint.date_start <= fields.Date.today():
                sprint.action_start()

    def _check_task_state(self):
        for task in self.task_ids:
            task.write(
                {
                    "kanban_state": "done",
                    "stage_id": self.env["project.task.type"]
                    .search([("name", "=", "Done")], limit=1)
                    .id,
                }
            )

    @api.depends("date_start", "date_option")
    def _compute_date_end(self):
        for sprint in self:
            if sprint.date_start and sprint.date_option != "custom":
                if sprint.date_option.endswith("_weeks"):
                    weeks = int(sprint.date_option.split("_")[0])
                    sprint.date_end = sprint.date_start + relativedelta(weeks=weeks)
                elif sprint.date_option.endswith("_months"):
                    months = int(sprint.date_option.split("_")[0])
                    sprint.date_end = sprint.date_start + relativedelta(months=months)
                elif sprint.date_option.endswith("_years"):
                    years = int(sprint.date_option.split("_")[0])
                    sprint.date_end = sprint.date_start + relativedelta(years=years)
