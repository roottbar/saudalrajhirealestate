from odoo import api, models, _
from odoo.exceptions import ValidationError


class AccountMove(models.Model):
    _inherit = 'account.move'

    @api.constrains('operating_unit_id', 'company_id')
    def _check_company_operating_unit(self):
        """
        Control the visibility/enforcement of the OU/company match constraint
        based on a system parameter set from settings.
        """
        icp = self.env['ir.config_parameter'].sudo()
        enforce = icp.get_param('payment_enhancements_ou.enforce_ou_company_match', default='True')
        # Accept truthy values 'True', '1' or True
        enforce_bool = str(enforce).lower() in ('true', '1', 'yes', 'y')
        if not enforce_bool:
            # Skip enforcement entirely when disabled
            return True

        for move in self:
            if move.company_id and move.operating_unit_id and move.company_id != move.operating_unit_id.company_id:
                # Keep the same message to match original behavior
                raise ValidationError(_('The Company in the Move and in Operating Unit must be the same.'))
        return True