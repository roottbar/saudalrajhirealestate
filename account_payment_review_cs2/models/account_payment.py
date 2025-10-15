from odoo import models, fields


class AccountPayment(models.Model):
    _inherit = 'account.payment'

    # Add 'review' to the payment states safely (no dynamic recursion)
    state = fields.Selection(selection_add=[('review', 'Reviewed')])

    def action_review(self):
        # Move payment to 'review' state
        self.write({'state': 'review'})
        return True
