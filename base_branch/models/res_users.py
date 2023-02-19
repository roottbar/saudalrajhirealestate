from odoo import fields, models, api


class Users(models.Model):
    _inherit = 'res.users'

    branch_id = fields.Many2one('branch.branch', string='Branch', related="partner_id.branch_id",
                                store=1, default=lambda self: self._get_default_branch(),
                                readonly=False)
    allowed_branches = fields.Many2many('branch.branch', string='Allowed Branches')
    allowed_see_other_customers = fields.Boolean('See Other Customers', default=False)

    def _get_default_branch(self):
        return self.env.user.branch_id

    # @api.model_create_multi
    # def create(self, vals_list):
    #     for values in vals_list:
    #         if not values.get('login', False):
    #             values['login'] = values['email'] if 'email' in values else None
    #     return super(Users, self).create(vals_list)
