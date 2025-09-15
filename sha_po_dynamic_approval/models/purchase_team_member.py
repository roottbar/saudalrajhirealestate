from odoo import models, fields


class PurchaseTeamMember(models.Model):
    _name = "purchase.team.member"
    _description = "Purchase Team Member"

    purchase_team_id = fields.Many2one(comodel_name="purchase.order.teams", string="Purchase Team")
    partner_id = fields.Many2one(comodel_name="res.users", string="Team Members")
    role = fields.Char(string="Role")
    min_amount = fields.Float(string="Minimum Amount")
    max_amount = fields.Float(string="Maximum Amount")