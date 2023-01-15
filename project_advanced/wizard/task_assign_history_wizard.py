from odoo import models, fields, api, _
from odoo.exceptions import ValidationError, UserError

class TaskAssignHistoryWizard(models.TransientModel):
    _name = 'task.assign.history.wizard'


    user_id = fields.Many2one("res.users", string="Assign To", required=True)
    notes = fields.Text(string="Notes")

    def assign_to(self):
        # get task
        task = self.env["project.task"].browse(self._context["active_id"])
        if  task.user_id.id == self.user_id.id:
            raise ValidationError(_('The chosen user is the current user.'))
        val = {
                'old_user_id': task.user_id.id,
                'new_user_id':self.user_id.id,
                'task_id': task.id,
                'description': self.notes,
            }
        task.assign_history_ids.create(val)
        task.user_id = self.user_id.id



