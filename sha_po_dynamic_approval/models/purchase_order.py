from odoo import models, fields, api, _
from odoo.exceptions import UserError


class PurchaseOrder(models.Model):
    _inherit = "purchase.order"

    purchase_team_id = fields.Many2one(comodel_name='purchase.order.teams', string="Purchase Team",
                                       default=lambda self: self.env['purchase.order.teams'].search(
                                           [('short_code', '=', 'DefaultPO')], limit=1))
    purchase_approve_line = fields.One2many(comodel_name="purchase.approve.route", inverse_name="purchase_id")
    team_lead_id = fields.Many2one('res.users', related='purchase_team_id.team_lead_id')
    is_approval_member = fields.Boolean(string="Is Approval Member", compute='_compute_is_approval_member')

    def _compute_is_approval_member(self):
        for order in self:
            if order.purchase_approve_line.filtered(lambda l: l.partner_id.id == order.env.user.id):
                order.is_approval_member = True
            else:
                order.is_approval_member = False

    @api.model
    def create(self, vals):
        res = super(PurchaseOrder, self).create(vals)
        if res.purchase_team_id:
            for member_id in res.purchase_team_id.team_member:
                self.env["purchase.approve.route"].create({
                    "purchase_id": res.id,
                    "partner_id": member_id.partner_id.id,
                    "role": member_id.role,
                    "state": "draft",
                })
        return res

    def write(self, vals):
        res = super(PurchaseOrder, self).write(vals)
        if 'purchase_team_id' in vals:
            for line_id in self.purchase_approve_line:
                line_id.sudo().unlink()
            if self.purchase_team_id:
                for member_id in self.purchase_team_id.team_member:
                    self.env["purchase.approve.route"].create({
                        "purchase_id": self.id,
                        "partner_id": member_id.partner_id.id,
                        "role": member_id.role,
                        "state": "draft",
                    })
        return res

    def button_confirm(self):
        if self.purchase_approve_line and self.team_lead_id.id != self.env.user.id:
            if self.purchase_approve_line.filtered(lambda l: l.state != 'done'):
                raise UserError(_('%s Order is not approved') % self.name)
        return super(PurchaseOrder, self).button_confirm()

    def approve_purchase(self):
        if self.purchase_approve_line:
            approval_lines = self.purchase_approve_line.filtered(
                lambda l: l.partner_id.id == self.env.user.id)
            for line_id in approval_lines:
                if line_id.state in ['draft', 'cancel']:
                    line_id.write({
                        "state": "done",
                    })
                    return {
                        'effect': {
                            'fadeout': 'slow',
                            'message': 'Thank You! The Purchase Order Has Been Approved From Your Side!',
                            'type': 'rainbow_man',
                            'img_url': 'sha_po_dynamic_approval/static/img/approved.png'
                        },
                    }
                else:
                    raise UserError(_("This purchase order has already been approved by you."))
            else:
                raise UserError(_("Sorry, you don't have access to approve %s Order") % self.name)

    def disapprove_purchase(self):
        if self.purchase_approve_line:
            approval_lines = self.purchase_approve_line.filtered(
                lambda l: l.partner_id.id == self.env.user.id)
            for line_id in approval_lines:
                if line_id.state in ['draft', 'done']:
                    line_id.write({
                        "state": "cancel",
                    })
                    return {
                        'effect': {
                            'fadeout': 'slow',
                            'message': 'The Purchase Order Has Been Rejected!!',
                            'type': 'rainbow_man',
                            'img_url': 'sha_po_dynamic_approval/static/img/reject.png'
                        },
                    }
                else:
                    raise UserError(_("This Purchase Order Has Already Been Rejected By You."))
            else:
                raise UserError(_("Sorry, you don't have access to approve %s Order") % self.name)
