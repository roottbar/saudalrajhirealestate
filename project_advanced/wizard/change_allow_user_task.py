from odoo import models, fields, api, _
from odoo.exceptions import ValidationError, UserError


class ChangeAllowUserTaskLine(models.TransientModel):
    _name = 'change.allow.user.task.line'
    _description = "Change Allow User Task Line"

    user_id = fields.Many2one("res.users", string="Allow To", required=True)
    task_ids = fields.Many2many("project.task", string="Tasks")
    allow_small_wiz_id = fields.Many2one('change.allow.user.task', string='Allow Users')
    all_tasks = fields.Boolean(string="All Tasks", default=True)
    project_id = fields.Many2one("project.project", string="Project")

    @api.onchange('all_tasks')
    def onchange_task_ids(self):
        for line in self:
            return {'domain': {'task_ids': [('id', 'in', line.project_id.task_ids.ids)]}}


class ChangeAllowUserTask(models.TransientModel):
    _name = 'change.allow.user.task'
    _description = "Change Allow User Task"

    project_id = fields.Many2one("project.project", string="Project")
    update_tasks = fields.Boolean(string="Update Tasks")
    assign_allow_users = fields.Selection(string="Assign Allow Users",
                                          selection=[('all', 'All Tasks'), ('special', 'Special Tasks')],
                                          default="all")
    line_ids = fields.One2many("change.allow.user.task.line", "allow_small_wiz_id", string="Allow User",
                               ondelete="cascade")

    @api.onchange('assign_allow_users')
    def onchange_assign_allow_users(self):
        lines = []
        if self.assign_allow_users == "special":
            for user in self.project_id.allowed_user_ids:
                lines.append((0, 0, {'user_id': user.id, 'project_id': self.project_id.id}))
        self.line_ids = lines or False

    def change_allowed_users_tasks(self):
        # change allowed users for all tasks of project (if change allow user of project and privacy visibility is not employees)
        project = self.project_id
        if project.privacy_visibility == "employees" or not project.allowed_user_ids or not self.project_id.task_ids:
            return

        if self.update_tasks:
            if self.assign_allow_users == "all":
                project.task_ids.write({"allowed_user_ids": [(4, user.id) for user in project.allowed_user_ids]})
            else:
                for line in self.line_ids:
                    if line.all_tasks:
                        project.task_ids.write({"allowed_user_ids": [(4, line.user_id.id)]})
                    elif line.task_ids:
                        line.task_ids.write({"allowed_user_ids": [(4, line.user_id.id)]})
        return True


