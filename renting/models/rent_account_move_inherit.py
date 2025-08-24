# -*- coding: utf-8 -*-

from odoo import models, fields, api


class RentAccountMoveInherit(models.Model):
    _inherit = 'account.move'

    contract_document_number = fields.Char(string='Document Number')
    obj_sale_order = fields.Many2one('sale.order')
    so_contract_number = fields.Char(string='Contract Number', related='obj_sale_order.contract_number')
    inv_contract_status = fields.Char(string='Contract Status')
    is_maintain = fields.Boolean(string='صيانة')
    property_name = fields.Many2one('rent.property', string='العقار')
    unit_number = fields.Many2one(
        'product.template',
        string='رقم الوحدة',
        domain="[('property_id', '=', property_name)]"
    )
    fromdate = fields.Datetime(string='From Date', default=fields.Date.context_today, copy=False)
    todate = fields.Datetime(string='To Date', default=fields.Date.context_today, copy=False)

    # ✅ بدل إعادة تعريف invoice_line_ids
    custom_invoice_line_ids = fields.One2many(
        'account.move.line', 'move_id',
        string='Custom Invoice lines',
        copy=False, readonly=True,
        domain=[('rent_fees', '=', False)],
        states={'draft': [('readonly', False)]})

    rent_sale_line_id = fields.Many2one(comodel_name='rent.sale.invoices')

    asset_id = fields.Many2one('account.asset', string="Asset")

    @api.onchange("asset_id", "journal_id")
    def _onchange_asset1(self):
        if (
            self.asset_id
            and self.asset_id.property_address_area
            and self.asset_id.property_address_area != self.operating_unit_id
        ):
            self.operating_unit_id = self.asset_id.property_address_area
            for line in self.line_ids:
                line.operating_unit_id = self.asset_id.property_address_area

    @api.model
    def create(self, vals):
        result = super(RentAccountMoveInherit, self).create(vals)
        if result.asset_id and result.asset_id.property_address_area:
            result.operating_unit_id = result.asset_id.property_address_area.id
        return result


class RentAccountMoveLineInherit(models.Model):
    _inherit = 'account.move.line'

    rent_fees = fields.Boolean(default=False)
