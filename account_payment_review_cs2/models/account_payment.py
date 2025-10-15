from odoo import models, fields


class AccountPayment(models.Model):
    _inherit = 'account.payment'

    # Ensure 'state' has a valid selection by deriving base states and adding 'review'.
    state = fields.Selection(selection='_selection_state_with_review')

    def _selection_state_with_review(self):
        # Get the existing selection for account.payment.state and append 'review'.
        base = self.env['account.payment'].fields_get(allfields=['state'])['state'].get('selection', [])
        if ('review', 'Reviewed') not in base:
            new = []
            inserted = False
            for key, label in base:
                new.append((key, label))
                if key == 'draft' and not inserted:
                    new.append(('review', 'Reviewed'))
                    inserted = True
            if not inserted:
                new.append(('review', 'Reviewed'))
            return new
        return base

    def action_review(self):
        # Move payment to 'review' state
        self.write({'state': 'review'})
        return True
