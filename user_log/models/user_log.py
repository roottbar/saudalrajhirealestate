from odoo import models, fields, api
from datetime import datetime

class UserLog(models.Model):
    _name = 'user.log'
    _description = 'User Activity Log'
    _order = 'create_date desc'

    name = fields.Char(string='Description', compute='_compute_description')
    user_id = fields.Many2one('res.users', string='User', required=True)
    model = fields.Char(string='Model')
    record_id = fields.Integer(string='Record ID')
    action = fields.Selection([
        ('create', 'Create'),
        ('write', 'Update'),
        ('unlink', 'Delete'),
        ('read', 'Read'),
        ('login', 'Login'),
        ('logout', 'Logout'),
    ], string='Action')
    date = fields.Datetime(string='Date', default=fields.Datetime.now)
    changes = fields.Text(string='Changes')
    ip_address = fields.Char(string='IP Address')

    @api.depends('model', 'action', 'record_id')
    def _compute_description(self):
        for log in self:
            log.name = f"{log.action.upper()} on {log.model} (ID: {log.record_id})"

    @api.model
    def create_log(self, user_id, model, record_id, action, changes=None, ip_address=None):
        return self.create({
            'user_id': user_id,
            'model': model,
            'record_id': record_id,
            'action': action,
            'changes': changes,
            'ip_address': ip_address,
        })

    class BaseModel(models.AbstractModel):
        _inherit = 'base'

        @api.model
        def create(self, vals):
            record = super(BaseModel, self).create(vals)
            if self._name != 'user.log':  # Avoid logging our own model
                self.env['user.log'].create_log(
                    user_id=self.env.user.id,
                    model=self._name,
                    record_id=record.id,
                    action='create',
                    changes=str(vals),
                    ip_address=self.env.request.httprequest.remote_addr if hasattr(self.env,
                                                                                   'request') and self.env.request else None
                )
            return record

        def write(self, vals):
            if self._name != 'user.log':  # Avoid logging our own model
                for record in self:
                    old_vals = {field: record[field] for field in vals.keys()}
                    self.env['user.log'].create_log(
                        user_id=self.env.user.id,
                        model=self._name,
                        record_id=record.id,
                        action='write',
                        changes=f"Old values: {old_vals}\nNew values: {vals}",
                        ip_address=self.env.request.httprequest.remote_addr if hasattr(self.env,
                                                                                       'request') and self.env.request else None
                    )
            return super(BaseModel, self).write(vals)

        def unlink(self):
            if self._name != 'user.log':  # Avoid logging our own model
                for record in self:
                    self.env['user.log'].create_log(
                        user_id=self.env.user.id,
                        model=self._name,
                        record_id=record.id,
                        action='unlink',
                        ip_address=self.env.request.httprequest.remote_addr if hasattr(self.env,
                                                                                       'request') and self.env.request else None
                    )
            return super(BaseModel, self).unlink()
    class BaseModel(models.AbstractModel):
        _inherit = 'base'

        @api.model
        def create(self, vals):
            record = super(BaseModel, self).create(vals)
            if self._name != 'user.log':  # Avoid logging our own model
                self.env['user.log'].create_log(
                    user_id=self.env.user.id,
                    model=self._name,
                    record_id=record.id,
                    action='create',
                    changes=str(vals),
                    ip_address=self.env.request.httprequest.remote_addr if hasattr(self.env, 'request') and self.env.request else None
                )
            return record

        def write(self, vals):
            if self._name != 'user.log':  # Avoid logging our own model
                for record in self:
                    old_vals = {field: record[field] for field in vals.keys()}
                    self.env['user.log'].create_log(
                        user_id=self.env.user.id,
                        model=self._name,
                        record_id=record.id,
                        action='write',
                        changes=f"Old values: {old_vals}\nNew values: {vals}",
                        ip_address=self.env.request.httprequest.remote_addr if hasattr(self.env, 'request') and self.env.request else None
                    )
            return super(BaseModel, self).write(vals)

        def unlink(self):
            if self._name != 'user.log':  # Avoid logging our own model
                for record in self:
                    self.env['user.log'].create_log(
                        user_id=self.env.user.id,
                        model=self._name,
                        record_id=record.id,
                        action='unlink',
                        ip_address=self.env.request.httprequest.remote_addr if hasattr(self.env, 'request') and self.env.request else None
                    )
            return super(BaseModel, self).unlink()