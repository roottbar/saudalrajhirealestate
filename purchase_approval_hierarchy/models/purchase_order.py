from odoo import models, fields, api, _
from odoo.exceptions import UserError

class PurchaseOrder(models.Model):
    _inherit = 'purchase.order'

    state = fields.Selection(selection_add=[
        ('approval_1', 'Approval Stage 1'),
        ('approval_2', 'Approval Stage 2'),
        ('approval_3', 'Approval Stage 3'),
        ('approved', 'Approved'),
    ], ondelete={
        'approval_1': 'set default',
        'approval_2': 'set default',
        'approval_3': 'set default',
        'approved': 'set default'
    })

    @api.returns('self', lambda value: value.id)
    def action_approve_1(self):
        for order in self:
            if not self.env.user.has_group('purchase_approval_hierarchy.group_purchase_approval_1'):
                raise UserError(_("You don't have the approval level 1 access rights."))
            if order.state != 'draft':
                raise UserError(_("Order must be in draft state."))
            order.write({'state': 'approval_1'})
        return True

    def action_approve_2(self):
        self.ensure_one()
        if not self.env.user.has_group('purchase_approval_hierarchy.group_purchase_approval_2'):
            raise UserError(_("You do not have permission to perform Approval 2."))
        if self.state != 'approval_1':
            raise UserError(_("Order is not in a state to perform Approval 2."))
        self.state = 'approval_2'

    def action_approve_3(self):
        self.ensure_one()
        if not self.env.user.has_group('purchase_approval_hierarchy.group_purchase_approval_3'):
            raise UserError(_("You do not have permission to perform Approval 3."))
        if self.state != 'approval_2':
            raise UserError(_("Order is not in a state to perform Approval 3."))
        self.state = 'approval_3'

    def action_final_approve(self):
        self.ensure_one()
        if self.state != 'approval_3':
            raise UserError(_("Order must pass Approval 3 before final approval."))
        self.state = 'approved'
