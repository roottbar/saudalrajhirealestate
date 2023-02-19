from odoo import fields, models


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    def _get_default_branch(self):
        if self.env.user.id != 1:
            branch = self.env.user.branch_id
        else:
            branch = False
        return branch

    branch_id = fields.Many2one('branch.branch', string='Branch',
                                domain=lambda self: self._get_allowed_branches(),
                                store=True, )

    def _get_allowed_branches(self):
        return [('id', 'in', self.env.user.allowed_branches.ids)]
