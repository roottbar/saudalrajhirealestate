from odoo import models, fields, api, _
from odoo.exceptions import UserError

class PurchaseOrder(models.Model):
    _inherit = 'purchase.order'

    approval_state = fields.Selection([
        ('draft', 'Draft'),
        ('approval_1', 'Approval Stage 1'),
        ('approval_2', 'Approval Stage 2'),
        ('approval_3', 'Approval Stage 3'),
        ('approved', 'Approved'),
    ], string="Approval State", default='draft', readonly=True, tracking=True)

    def action_approve_1(self):
        self.ensure_one()
        if not self.env.user.has_group('purchase_approval_hierarchy.group_purchase_approval_1'):
            raise UserError(_("You do not have permission to perform Approval 1."))
        if self.approval_state != 'draft':
            raise UserError(_("Order is not in a state to perform Approval 1."))
        self.approval_state = 'approval_1'

    def action_approve_2(self):
        self.ensure_one()
        if not self.env.user.has_group('purchase_approval_hierarchy.group_purchase_approval_2'):
            raise UserError(_("You do not have permission to perform Approval 2."))
        if self.approval_state != 'approval_1':
            raise UserError(_("Order is not in a state to perform Approval 2."))
        self.approval_state = 'approval_2'

    def action_approve_3(self):
        self.ensure_one()
        if not self.env.user.has_group('purchase_approval_hierarchy.group_purchase_approval_3'):
            raise UserError(_("You do not have permission to perform Approval 3."))
        if self.approval_state != 'approval_2':
            raise UserError(_("Order is not in a state to perform Approval 3."))
        self.approval_state = 'approval_3'

    def action_final_approve(self):
        self.ensure_one()
        if self.approval_state != 'approval_3':
            raise UserError(_("Order must pass Approval 3 before final approval."))
        self.approval_state = 'approved'