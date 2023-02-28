from odoo import fields, models, _


class BranchBranch(models.Model):
    _name = "branch.branch"
    _description = "Branch"
    name = fields.Char('Branch Name')
    short_code = fields.Char('Branch Short Code')
    partner_sequence_id = fields.Many2one('ir.sequence', string='Partner Sequence',
                                          required=True, copy=False)
    company_id = fields.Many2one(comodel_name='res.company', string='Company', store=True,
                                 default=lambda self: self.env.company)
    street = fields.Char('Street')
    street2 = fields.Char('Street2')
    zip = fields.Char('Zip', change_default=True)
    city = fields.Char(string="City")
    city_id = fields.Many2one('res.city', string='City of Address')
    state_id = fields.Many2one("res.country.state", string='State')
    country_id = fields.Many2one('res.country', string='Country')
    color = fields.Integer(string='')

    def action_view_users(self):
        return {
            'type': 'ir.actions.act_window',
            'name': _('Branch Users'),
            'res_model': 'res.users',
            'view_mode': 'tree,form',
            'domain': [('branch_id', '=', self.id)],
        }

    def action_view_allow_users(self):
        return {
            'type': 'ir.actions.act_window',
            'name': _('Branch Users'),
            'res_model': 'res.users',
            'view_mode': 'tree,form',
            'domain': [('allowed_branches', 'in', self.id)],
        }
