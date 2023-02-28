from odoo import api, fields, models

class Investigation(models.Model):
    _name = "investigation"
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = "Investigation"

    state = fields.Selection([('new', 'New'), ('currently', 'Currently'), ('done', 'Done')], string="Status", default='new')