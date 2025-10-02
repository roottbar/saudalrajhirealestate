# -*- coding: utf-8 -*-

from odoo import api, models, fields, _
from odoo.exceptions import ValidationError


class PurchaseRequisition(models.Model):
    _inherit = 'purchase.requisition'
    request_id = fields.Many2one(comodel_name='purchase.request', string='Request ', )
    locked = fields.Boolean(string='Locked')

    @api.onchange('request_id')
    def change_request_id(self):
        for rec in self:
            line_ids = []
            for line in rec.request_id.line_ids:
                order_line_values =  {
                    'requisition_id': self._origin.id or self.id,
                    'product_id': line.product_id.id,
                    'product_description_variants': line.name,
                    'product_qty': line.product_qty,
                    'product_uom_id': line.product_uom_id.id,
                    'price_unit': line.estimated_cost,
                }
                line_ids.append((0, 0, order_line_values))
            rec.line_ids = line_ids

    @api.model
    def create(self, vals):
        if 'request_id' in vals:
            request_id = self.env['purchase.request'].browse(vals['request_id'])
            if any(request_id.agreement_ids.filtered(lambda line: line.locked == True)) == True:
                raise ValidationError(_("You Can not Do this Action Which One Request Had been Confirmed "))
        return super(PurchaseRequisition, self).create(vals)

    def action_in_progress(self):
        res = super().action_in_progress()
        for rec in self.env['purchase.requisition'].search([('request_id', '=', self.request_id.id)]):
            rec.locked = True
        return res

    def action_cancel(self):
        for rec in self:
            if rec.locked == True:
                raise  ValidationError(_("You Can not Do this Action Which Request Had been Confirmed "))
        return super(self, PurchaseRequisition).action_cancel()

    def action_draft(self):
        for rec in self:
            if rec.locked == True:
                raise  ValidationError(_("You Can not Do this Action Which Request Had been Confirmed "))
        return super(self, PurchaseRequisition).action_draft()