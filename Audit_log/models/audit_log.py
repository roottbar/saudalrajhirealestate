from odoo import models, fields

class AuditLog(models.Model):
    _name = 'custom.audit.log'
    _description = 'Custom Audit Log'
    _order = 'date desc'

    user_id = fields.Many2one('res.users', string='User', required=True)
    model = fields.Char(string='Model', required=True)
    record_id = fields.Integer(string='Record ID', required=True)
    action = fields.Selection([
        ('create', 'Create'),
        ('write', 'Update'),
        ('unlink', 'Delete')
    ], string='Action', required=True)
    date = fields.Datetime(string='Date', required=True, default=fields.Datetime.now)
    changes = fields.Text(string='Changes')