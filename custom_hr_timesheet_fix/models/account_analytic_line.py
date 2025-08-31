from odoo import models

class AccountAnalyticLine(models.Model):
    _inherit = 'account.analytic.line'

    def _timesheet_get_portal_domain(self):
        domain = super(AccountAnalyticLine, self)._timesheet_get_portal_domain()
        # Fix for TypeError: missing mode
        domain = self.env['ir.rule']._compute_domain(self._name, mode='read')
        return domain
