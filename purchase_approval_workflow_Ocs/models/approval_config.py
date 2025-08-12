from odoo import models, fields, api

class PurchaseApprovalConfig(models.Model):
    _name = 'purchase.approval.config'
    _description = 'Purchase Approval Configuration'

    name = fields.Char('Name', required=True)
    min_amount = fields.Float('Minimum Amount', required=True)
    max_amount = fields.Float('Maximum Amount', required=True)
    level_1_required = fields.Boolean('Requires Level 1 Approval')
    level_2_required = fields.Boolean('Requires Level 2 Approval')
    level_3_required = fields.Boolean('Requires Level 3 Approval')