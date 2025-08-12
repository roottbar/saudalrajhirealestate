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

    def action_approve_1(self):
        self.ensure_one()
        if not self.env.user.has_group('purchase_approval_hierarchy.group_purchase_approval_1'):
            raise UserError(_("You don't have approval level 1 access rights."))
        if self.state != 'draft':
            raise UserError(_("Order must be in draft state."))
        self.write({'state': 'approval_1'})
        return True

    def action_approve_2(self):
        self.ensure_one()
        if not self.env.user.has_group('purchase_approval_hierarchy.group_purchase_approval_2'):
            raise UserError(_("You don't have approval level 2 access rights."))
        if self.state != 'approval_1':
            raise UserError(_("Order must be in approval stage 1."))
        self.write({'state': 'approval_2'})
        return True

    def action_approve_3(self):
        self.ensure_one()
        if not self.env.user.has_group('purchase_approval_hierarchy.group_purchase_approval_3'):
            raise UserError(_("You don't have approval level 3 access rights."))
        if self.state != 'approval_2':
            raise UserError(_("Order must be in approval stage 2."))
        self.write({'state': 'approval_3'})
        return True

    def action_final_approve(self):
        self.ensure_one()
        if self.state != 'approval_3':
            raise UserError(_("Order must be in approval stage 3."))
        self.write({'state': 'approved'})
        return True