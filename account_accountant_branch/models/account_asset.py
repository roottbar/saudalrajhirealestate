from odoo import fields, models


class AccountAsset(models.Model):
    _inherit = "account.asset"

    def _get_default_branch(self):
        return self.env.user.branch_id

    branch_id = fields.Many2one('branch.branch',
                                string='Branch',
                                store=True,
                                readonly=False,
                                default=_get_default_branch,
                                domain=lambda self: [("id", "in", self.env.user.allowed_branches.ids)])

    def validate(self):
        super(AccountAsset, self.with_context(default_branch_id=self.branch_id.id)).validate()
