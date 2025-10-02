from odoo import models, fields, api, _
from odoo.exceptions import ValidationError


class PurchaseRequestQuotationLineWizard(models.TransientModel):
    _name = 'purchase.request.quotation.line.wizard'
    _description = "Purchase Request Quotation Line Wizard"

    pr_line_wiz_id = fields.Many2one('purchase.request.quotation.wizard', string='Purchase Request Line',
                                     ondelete='cascade')
    product_id = fields.Many2one('product.product', string='Product', readonly=True)
    price_unit = fields.Float(string='Unit Price', digits='Product Price')
    product_qty = fields.Float(string='Quantity', digits='Product Unit of Measure', readonly=True)
    uom_id = fields.Many2one('uom.uom', string='Unit of Measure', readonly=True)
    purchase_request_line = fields.Many2one('purchase.request.line', readonly=True)

    @api.constrains('price_unit')
    def _check_price_unit(self):
        if self._context.get('create_purchase_order', False):
            for line in self:
                if line.price_unit <= 0:
                    raise ValidationError(_("Unit Price must be positive"))


class PurchaseRequestQuotationWizard(models.TransientModel):
    _name = 'purchase.request.quotation.wizard'
    _description = 'Purchase Request Quotation Wizard'

    @api.model
    def _default_picking_type(self):
        picking_type = self.env['stock.picking.type'].search(
            [('code', '=', 'incoming'), ('warehouse_id.company_id', '=', self.env.company.id)])
        if not picking_type:
            picking_type = self.env['stock.picking.type'].search(
                [('code', '=', 'incoming'), ('warehouse_id', '=', False)])
        return picking_type[:1]

    select_purchase_order = fields.Boolean(string="Select RFQ")
    purchase_order_id = fields.Many2one("purchase.order", string="Purchase RFQ",
                                        domain=[('state', 'in', ['draft'])])
    vendor_id = fields.Many2one("res.partner", string="Vendor")
    lines = fields.One2many("purchase.request.quotation.line.wizard", 'pr_line_wiz_id', string="Lines")
    picking_type_id = fields.Many2one('stock.picking.type', 'Deliver To', default=_default_picking_type,
                                      domain="[('warehouse_id', '=', False)]")
    purchase_request_id = fields.Many2one('purchase.request', string='Purchase Request')

    @api.onchange('select_purchase_order')
    def onchange_method(self):
        if self.select_purchase_order:
            self.vendor_id = False
        else:
            self.purchase_order_id = False

    def _prepare_purchase_order_line(self, line, price_unit, purchase_order):
        vals = {
            'name': line.name,
            'sequence': line.sequence,
            'product_id': line.product_id.id,
            'product_qty': line.product_qty,
            'price_unit': price_unit,
            'product_uom': line.uom_id.id,
            'taxes_id': [(6, 0, line.taxes_id.ids)],
            'account_analytic_id': line.account_analytic_id,
            'analytic_tag_ids': [(6, 0, line.analytic_tag_ids.ids)],
            'date_planned': line.date,
            'order_id': purchase_order.id,
        }
        return vals

    def action_create_purchase_order(self):
        # create request for question or purchase order
        purchase_order = self.purchase_order_id
        if not self.select_purchase_order:
            purchase_order = self.env["purchase.order"].create({
                'origin': ",".join(purchase_request.name for purchase_request in
                                   self.mapped("lines.purchase_request_line.purchase_request_id")),
                'partner_id': self.vendor_id.id,
                'picking_type_id': self.picking_type_id and self.picking_type_id.id or False,
                'from_pr': True,
            })

        purchase_order_line_obj = self.env['purchase.order.line']
        for line in self.lines:
            purchase_request_line = line.purchase_request_line
            if purchase_request_line.purchase_order_line:
                raise ValidationError(
                    _("This Product %s already have purchase order") % purchase_request_line.name)
            vals = self._prepare_purchase_order_line(purchase_request_line, line.price_unit, purchase_order)
            purchase_order_line = purchase_order_line_obj.create(vals)

            # update purchase request
            purchase_request_line.write({"purchase_order_line": purchase_order_line.id})
        if self._context.get("create_purchase_order", False):
            purchase_order.button_confirm()
        return {
            'res_model': 'purchase.order',
            'type': 'ir.actions.act_window',
            'view_mode': 'form',
            'view_id': self.sudo().env.ref('purchase.purchase_order_form').id,
            'res_id': purchase_order.id,
        }
