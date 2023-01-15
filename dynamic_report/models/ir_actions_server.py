from odoo import fields, models, api


class ActionsServer(models.Model):
    _inherit = 'ir.actions.server'

    template_id = fields.Many2one('report.template')


