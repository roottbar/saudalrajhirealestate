from odoo import fields, models, _


class BranchBranch(models.Model):
    _inherit = "branch.branch"

    account_asset_count = fields.Integer('Asset Count', compute="_get_asset_count")

    def _get_asset_count(self):
        self.account_asset_count = self.env['account.asset'].search_count([('branch_id', '=', self.id)])

    def action_view_assets(self):
        return {
            'type': 'ir.actions.act_window',
            'name': _('Branch Moves'),
            'res_model': 'account.asset',
            'view_mode': 'tree,form',
            'context': {},
            'domain': [('branch_id', '=', self.id)],
        }
