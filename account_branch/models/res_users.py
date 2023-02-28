from odoo import fields, models


class Users(models.Model):
    _inherit = 'res.users'

    allowed_see_other_invoice = fields.Boolean('See Other Invoices', default=False)
    allowed_see_other_payments = fields.Boolean('See Other Payments', default=False)
