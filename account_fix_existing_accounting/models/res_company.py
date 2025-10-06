from odoo import models


class ResCompany(models.Model):
    _inherit = "res.company"

    def _existing_accounting(self):
        self.ensure_one()
        # Use search with limit to check existence instead of search_count(limit=1)
        return bool(
            self.env["account.move.line"].sudo().search(
                [("company_id", "child_of", self.id)], limit=1
            )
        )