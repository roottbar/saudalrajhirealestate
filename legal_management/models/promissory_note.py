from odoo import api, fields, models

class PromissoryNote(models.Model):
    _name = "promissory.note"
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = "Promissory Note"

    state = fields.Selection([('new', 'New'), ('currently', 'Currently'), ('done', 'Done')], string="Status", default='new')
    issuer_bond = fields.Many2one('res.company', string='Issuer of bond', required=True, default=lambda self: self.env.user.company_id)

