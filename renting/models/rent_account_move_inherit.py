# -*- coding: utf-8 -*-

from odoo import models, fields, api
from odoo.exceptions import UserError


class RentAccountMoveInherit(models.Model):
    _inherit = 'account.move'

    contract_document_number = fields.Char(string='Document Number')
    obj_sale_order = fields.Many2one('sale.order')
    so_contract_number = fields.Char(string='Contract Number', related='obj_sale_order.contract_number')
    inv_contract_status = fields.Char(string='Contract Status')
    is_maintain = fields.Boolean(string='صبانة')
    property_name = fields.Many2one('rent.property', string='العقار')
    unit_number = fields.Many2one('product.template', string='رقم الوحدة',
                                  domain="[('property_id', '=', property_name)]",
                                  )
    fromdate = fields.Datetime(string='From Date', default=fields.Date.context_today, copy=False)
    todate = fields.Datetime(string='To Date', default=fields.Date.context_today, copy=False)
    invoice_line_ids = fields.One2many('account.move.line', 'move_id', string='Invoice lines',
                                       copy=False,
                                       domain=[('exclude_from_invoice_tab', '=', False), ('rent_fees', '=', False)],
                                       readonly="state != 'draft'")
    rent_sale_line_id= fields.Many2one(comodel_name='rent.sale.invoices')
    # def action_post(self):
    #     # update method_number in deferred earning with contract period
    #     if self.fromdate and self.todate:
    #         accounts = self.invoice_line_ids.filtered(lambda l: l.account_id.create_asset == 'validate')
    #         if accounts:
    #             date_diff_months = (self.todate.month - self.fromdate.month) + 12 * (
    #                     self.todate.year - self.fromdate.year)
    #             accounts.account_id.asset_model.method_number = date_diff_months
    #
    #     result = super(RentAccountMoveInherit, self).action_post()
    #     return result

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
        if result.asset_id:
            if result.asset_id.property_address_area:
                result.operating_unit_id = result.asset_id.property_address_area.id

        return result

    # @api.model
    # def _compute_name(self):
    #     result = super(RentAccountMoveInherit, self)._compute_name()
    #     for rec in self:
    #         name = rec.name
    #         split_name = name.split("/", 1)
    #         if len(split_name) > 2:
    #             if split_name[1]:
    #                 rec.name = str(rec.journal_id.code + '/' + split_name[1])
    #
    #     return result


class RentAccountMoveLineInherit(models.Model):
    _inherit = 'account.move.line'

    rent_fees = fields.Boolean(default=False)

